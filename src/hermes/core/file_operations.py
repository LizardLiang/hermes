"""File operations for processing translation files."""

import json
import os
import shutil
import zipfile
from collections.abc import Callable

# Language mapping: output folder -> source folder in ZIP
LANGUAGE_MAPPING = {
    "ar-sa": "ar",
    "en-us": "en",
    "ja-jp": "ja",
    "native": "zh-TW",
    "zh-cn": "zh-CN",
    "th-th": "th",
    "vi-vn": "vi",
    "id-ID": "id",
}


def extract_and_replace_files(
    zip_path: str,
    target_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    """
    Extract ZIP file and replace existing files.

    Args:
        zip_path: Path to the ZIP file
        target_path: Directory to extract to
        progress_callback: Optional callback with (current, total) progress
    """
    # Remove existing directory
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    os.makedirs(target_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        members = zip_ref.namelist()
        total = len(members)

        for idx, member in enumerate(members):
            zip_ref.extract(member, target_path)
            if progress_callback:
                progress_callback(idx + 1, total)


def process_language_files(
    data_path: str,
    result_path: str,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> list[str]:
    """
    Process JSON language files and convert to JS format.

    Args:
        data_path: Path to extracted data
        result_path: Path to save processed files
        progress_callback: Optional callback with (language, current, total)

    Returns:
        List of processed language codes
    """
    processed = []
    total = len(LANGUAGE_MAPPING)

    for idx, (output_folder, source_folder) in enumerate(LANGUAGE_MAPPING.items()):
        lang_path = os.path.join(result_path, output_folder)
        os.makedirs(lang_path, exist_ok=True)

        input_file = os.path.join(data_path, source_folder, "CommonResource.json")
        output_file = os.path.join(lang_path, "CommonResource.js")

        if progress_callback:
            progress_callback(output_folder, idx + 1, total)

        if os.path.exists(input_file):
            with open(input_file, encoding="utf-8") as f:
                data = json.load(f)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(
                    "(function (Radar) {\n"
                    "    Radar.i18n = Radar.i18n || {};\n"
                    "    // 自訂 Resource\n"
                    "    Radar.i18n['CommonResource'] = "
                )
                json.dump(data, f, ensure_ascii=False, indent=8)
                f.write(";\n}(Radar || {}));")

            processed.append(output_folder)

    return processed


def validate_paths(
    data_path: str,
    result_path: str,
) -> tuple[bool, list[str]]:
    """
    Validate that required paths and files exist.

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not os.path.exists(data_path):
        issues.append(f"Data path does not exist: {data_path}")

    # Check for at least one language file
    found_language = False
    for source_folder in LANGUAGE_MAPPING.values():
        input_file = os.path.join(data_path, source_folder, "CommonResource.json")
        if os.path.exists(input_file):
            found_language = True
            break

    if not found_language and os.path.exists(data_path):
        issues.append("No language files found in data path")

    return len(issues) == 0, issues
