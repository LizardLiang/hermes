"""Crowdin API client for download operations."""

import time
from collections.abc import Callable
from dataclasses import dataclass

import requests


@dataclass
class BuildProgress:
    """Progress information for build operations."""

    status: str
    progress: int  # 0-100
    message: str


class CrowdinError(Exception):
    """Exception for Crowdin API errors."""

    pass


class CrowdinAPI:
    """Crowdin API client for downloading translations."""

    def __init__(self, api_token: str, project_id: str):
        self.api_token = api_token
        self.project_id = project_id
        self.base_url = f"https://api.crowdin.com/api/v2/projects/{self.project_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def initiate_build(self) -> int:
        """
        Initiate a translation build.

        Returns:
            Build ID

        Raises:
            CrowdinError: If build initiation fails
        """
        url = f"{self.base_url}/translations/builds"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 201:
            build_id = response.json()["data"]["id"]
            return build_id
        else:
            raise CrowdinError(
                f"Failed to initiate build: {response.status_code} - {response.text}"
            )

    def check_build_status(
        self,
        build_id: int,
        progress_callback: Callable[[BuildProgress], None] | None = None,
        poll_interval: float = 2.0,
    ) -> bool:
        """
        Check and wait for build to complete.

        Args:
            build_id: The build ID to check
            progress_callback: Optional callback for progress updates
            poll_interval: Seconds between status checks

        Returns:
            True if build completed successfully

        Raises:
            CrowdinError: If build fails
        """
        url = f"{self.base_url}/translations/builds/{build_id}"

        while True:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()["data"]
                status = data["status"]
                progress = data.get("progress", 0)

                if progress_callback:
                    progress_callback(
                        BuildProgress(
                            status=status,
                            progress=progress,
                            message=f"Build {status}: {progress}%",
                        )
                    )

                if status == "finished":
                    return True
                elif status == "inProgress":
                    time.sleep(poll_interval)
                else:
                    raise CrowdinError(f"Build failed with status: {status}")
            else:
                raise CrowdinError(
                    f"Failed to check build status: {response.status_code} - {response.text}"
                )

    def download_build(
        self,
        build_id: int,
        save_path: str = "translations.zip",
        progress_callback: Callable[[int], None] | None = None,
    ) -> str:
        """
        Download the completed build.

        Args:
            build_id: The build ID to download
            save_path: Path to save the ZIP file
            progress_callback: Optional callback for download progress (0-100)

        Returns:
            Path to the downloaded file

        Raises:
            CrowdinError: If download fails
        """
        url = f"{self.base_url}/translations/builds/{build_id}/download"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            download_url = response.json()["data"]["url"]

            # Download with progress tracking
            download_response = requests.get(download_url, stream=True)
            total_size = int(download_response.headers.get("content-length", 0))

            with open(save_path, "wb") as file:
                downloaded = 0
                for chunk in download_response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(int(downloaded * 100 / total_size))

            return save_path
        else:
            raise CrowdinError(
                f"Failed to download build: {response.status_code} - {response.text}"
            )

    def get_languages(self) -> dict[str, str]:
        """
        Get available languages in the project.

        Returns:
            Dict mapping locale to language ID
        """
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
            raise CrowdinError(f"Failed to get languages: {response.status_code} - {response.text}")
