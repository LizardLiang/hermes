"""Crowdin API client for upload operations with Gemini translation."""

import json
import os
import re
from collections.abc import Callable

import requests
from google import genai

from .crowdin_api import CrowdinError


class CrowdinUploadAPI:
    """Crowdin API client for uploading translations with Gemini AI support."""

    DEFAULT_PROMPTS = """你是一個多語系機器人，根據輸入的關鍵字進行翻譯。請回傳 JSON 格式的翻譯結果（**只回傳純 JSON 本體**，不要有任何說明文字、程式碼框或語法標記），
請注意：請勿使用程式碼區塊、請勿使用 Markdown 格式（例如 ```json 之類），只需輸出 JSON 本體內容。絕對禁止使用三個反引號。

格式規則如下：
1. 使用標準語系代碼為最外層 key，例如："zh-TW"、"zh-CN"、"en-US" 等。
2. 各語系內的 key 為 "__原文關鍵字"，value 為該語言的翻譯結果。
3. 支援語言：
   - zh-TW（繁體中文）
   - zh-CN（簡體中文）
   - en-US（英文）
   - ja-JP（日文）
   - th-TH（泰文）
   - vi-VN（越南文）
   - id-ID（印尼文）

以下是範例：

Input: 直接能源排放, 間接能源排放

Output:
{
  "zh-TW": {
    "__直接能源排放": "直接能源排放",
    "__間接能源排放": "間接能源排放"
  },
  "zh-CN": {
    "__直接能源排放": "直接能源排放",
    "__間接能源排放": "间接能源排放"
  },
  "en-US": {
    "__直接能源排放": "Direct energy emissions",
    "__間接能源排放": "Indirect energy emissions"
  },
  "ja-JP": {
    "__直接能源排放": "直接的なエネルギー排出",
    "__間接能源排放": "間接エネルギー排出"
  },
  "th-TH": {
    "__直接能源排放": "การปล่อยพลังงานโดยตรง",
    "__間接能源排放": "การปล่อยพลังงานทางอ้อม"
  },
  "vi-VN": {
    "__直接能源排放": "Phát thải năng lượng trực tiếp",
    "__間接能源排放": "Phát thải năng lượng gián tiếp"
  },
  "id-ID": {
    "__直接能源排放": "Emisi energi langsung",
    "__間接能源排放": "Emisi energi tidak langsung"
  }
}

請依照相同格式回傳 JSON 本體，**不要加上任何說明、註解、標記或程式碼框**。
Input: """

    def __init__(
        self,
        api_token: str,
        project_id: str,
        gemini_api_key: str,
        key_file_path: str | None = None,
        prompt_file_path: str | None = None,
        data_path: str = "GSSKPIM-1 (translations)/",
        log_callback: Callable[[str], None] | None = None,
    ):
        self.api_token = api_token
        self.project_id = project_id
        self.base_url = f"https://api.crowdin.com/api/v2/projects/{self.project_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self.data_path = data_path
        self.t_file_path = os.path.join(data_path, "zh-TW", "CommonResource.json")
        self.log = log_callback or print

        # Load translations context
        self.translations: dict[str, dict[str, str]] = {}
        self.key_context = ""
        self.prompt_context = self.DEFAULT_PROMPTS
        self.existing_translations: dict = {}

        # Load key file
        if key_file_path and os.path.exists(key_file_path):
            with open(key_file_path, encoding="utf-8") as f:
                self.key_context = f.read()

        # Load custom prompts if provided
        if prompt_file_path and os.path.exists(prompt_file_path):
            with open(prompt_file_path, encoding="utf-8") as f:
                self.prompt_context = f.read()

        # Load existing translations
        if os.path.exists(self.t_file_path):
            with open(self.t_file_path, encoding="utf-8") as f:
                self.existing_translations = json.load(f)

        # Get languages from Crowdin
        self.languages = self._get_languages()
        self.added_keys: dict[str, int] = {}

        # Initialize Gemini client (new SDK)
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.gemini_model = "gemini-2.0-flash"

    def _get_languages(self) -> dict[str, str]:
        """Get available languages from Crowdin."""
        url = f"{self.base_url}/languages/progress"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            languages = {}
            for item in response.json().get("data", []):
                locale = item["data"]["language"]["locale"]
                lang_id = item["data"]["languageId"]
                languages[locale] = lang_id
            return languages
        else:
            self.log(f"Warning: Could not get languages: {response.text}")
            return {}

    def translate_missing_with_gemini(
        self,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, dict[str, str]]:
        """
        Use Gemini AI to translate missing keys.

        Returns:
            Dict of translations by language
        """
        if not self.key_context.strip():
            self.log("No keys to translate")
            return {}

        self.log("使用 Gemini 翻譯新字詞...")
        prompt = f"{self.prompt_context}{self.key_context}"

        try:
            if progress_callback:
                progress_callback("Sending to Gemini...")

            result = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
            )
            translated_text = result.text.strip()

            if progress_callback:
                progress_callback("Parsing response...")

            # Try to extract JSON from response
            match = re.search(r"```json\n(.*?)\n```", translated_text, re.DOTALL)
            if match:
                translations = json.loads(match.group(1))
            else:
                # Try parsing as raw JSON
                translations = json.loads(translated_text)

            # Merge into self.translations
            for lang, values in translations.items():
                self.translations.setdefault(lang, {})
                for key, val in values.items():
                    self.translations[lang][key] = val

            self.log("成功整併 JSON 翻譯結果")
            return self.translations

        except Exception as e:
            raise CrowdinError(f"Translation failed: {e}")

    def add_keys(
        self,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict[str, int]:
        """
        Add new translation keys to Crowdin.

        Args:
            progress_callback: Callback with (current, total) progress

        Returns:
            Dict mapping key identifiers to their Crowdin IDs
        """
        added_keys = {}
        zh_tw_keys = self.translations.get("zh-TW", {})
        total = len(zh_tw_keys)

        for idx, key in enumerate(zh_tw_keys):
            if progress_callback:
                progress_callback(idx + 1, total)

            if key in self.existing_translations:
                # Key already exists, check if it's in Crowdin
                response = requests.get(
                    f"{self.base_url}/strings?filter={key}",
                    headers=self.headers,
                )
                if response.status_code == 200:
                    self.log(f"Key '{key}' 已存在")
                    continue
            else:
                # Add new key
                new_key = {
                    "text": key.split("__")[1] if "__" in key else key,
                    "identifier": key,
                    "fileId": 15,  # Default file ID
                }
                response = requests.post(
                    f"{self.base_url}/strings",
                    headers=self.headers,
                    data=json.dumps(new_key),
                )

                if response.status_code == 201:
                    response_data = response.json().get("data", {})
                    self.log(f"新增 Key: {response_data['identifier']}")
                    added_keys[response_data["identifier"]] = response_data["id"]
                else:
                    raise CrowdinError(f"Failed to add key '{key}': {response.text}")

        self.added_keys = added_keys
        return added_keys

    def add_translations(
        self,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        """
        Add translations for newly added keys.

        Args:
            progress_callback: Callback with (current, total) progress
        """
        if not self.added_keys:
            self.log("No new keys to translate")
            return

        translation_url = f"{self.base_url}/translations"
        total_operations = sum(len(keys) for keys in self.translations.values()) * len(
            self.added_keys
        )
        current = 0

        for language_id, keys in self.translations.items():
            if language_id not in self.languages:
                continue

            for key, value in keys.items():
                if key in self.added_keys:
                    current += 1
                    if progress_callback:
                        progress_callback(current, total_operations)

                    translation_item = {
                        "stringId": self.added_keys[key],
                        "languageId": self.languages[language_id],
                        "text": value,
                    }
                    response = requests.post(
                        translation_url,
                        headers=self.headers,
                        data=json.dumps(translation_item),
                    )

                    if response.status_code == 201:
                        self.log(f"新增 {language_id} {key} 翻譯成功")
                    else:
                        self.log(f"Warning: Failed to add translation: {response.text}")

    def run_full_upload(
        self,
        progress_callback: Callable[[str, int], None] | None = None,
    ) -> None:
        """
        Run the full upload workflow: translate → add keys → add translations.

        Args:
            progress_callback: Callback with (stage, progress) updates
        """
        # Stage 1: Translate with Gemini
        if progress_callback:
            progress_callback("Translating with Gemini...", 0)

        self.translate_missing_with_gemini()

        # Stage 2: Add keys
        if progress_callback:
            progress_callback("Adding keys to Crowdin...", 33)

        self.add_keys()

        # Stage 3: Add translations
        if progress_callback:
            progress_callback("Adding translations...", 66)

        self.add_translations()

        if progress_callback:
            progress_callback("Complete!", 100)
