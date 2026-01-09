"""Configuration management for Hermes (portable mode)."""

import base64
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "hermes"


def get_app_dir() -> Path:
    """
    Get the application directory (where config will be stored).

    - If running as PyInstaller executable: directory containing the .exe
    - If running from source: current working directory
    """
    if getattr(sys, "frozen", False):
        # Running as compiled executable (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Running from source - use current working directory
        return Path.cwd()


def get_config_dir() -> Path:
    """Get the config directory path."""
    return get_app_dir()


def get_config_file() -> Path:
    """Get the config file path."""
    return get_config_dir() / "hermes.config.json"


# Simple obfuscation for tokens (not encryption, just prevents casual viewing)
def _encode_token(token: str) -> str:
    """Encode token for storage (base64 obfuscation)."""
    if not token:
        return ""
    return base64.b64encode(token.encode("utf-8")).decode("ascii")


def _decode_token(encoded: str) -> str:
    """Decode token from storage."""
    if not encoded:
        return ""
    try:
        return base64.b64decode(encoded.encode("ascii")).decode("utf-8")
    except Exception:
        return encoded  # Return as-is if decoding fails (plain text fallback)


@dataclass
class Profile:
    """A configuration profile for Crowdin operations."""

    name: str
    project_id: str = ""
    data_path: str = "GSSKPIM-1 (translations)/"
    result_path: str = "i18n/default/"
    key_path: str = "keys.txt"
    prompts_path: str = "prompts.txt"

    # Tokens stored directly in profile (obfuscated in JSON)
    _crowdin_token: str = field(default="", repr=False)
    _gemini_token: str = field(default="", repr=False)

    @property
    def crowdin_token(self) -> str | None:
        """Get Crowdin API token."""
        return self._crowdin_token or None

    @crowdin_token.setter
    def crowdin_token(self, value: str) -> None:
        """Set Crowdin API token."""
        self._crowdin_token = value or ""

    @property
    def gemini_token(self) -> str | None:
        """Get Gemini API token."""
        return self._gemini_token or None

    @gemini_token.setter
    def gemini_token(self, value: str) -> None:
        """Set Gemini API token."""
        self._gemini_token = value or ""

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "name": self.name,
            "project_id": self.project_id,
            "data_path": self.data_path,
            "result_path": self.result_path,
            "key_path": self.key_path,
            "prompts_path": self.prompts_path,
            # Tokens are obfuscated (base64) - not encrypted, just not plaintext
            "crowdin_token": _encode_token(self._crowdin_token),
            "gemini_token": _encode_token(self._gemini_token),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        """Create Profile from dict."""
        profile = cls(
            name=data.get("name", "default"),
            project_id=data.get("project_id", ""),
            data_path=data.get("data_path", "GSSKPIM-1 (translations)/"),
            result_path=data.get("result_path", "i18n/default/"),
            key_path=data.get("key_path", "keys.txt"),
            prompts_path=data.get("prompts_path", "prompts.txt"),
        )
        # Decode obfuscated tokens
        profile._crowdin_token = _decode_token(data.get("crowdin_token", ""))
        profile._gemini_token = _decode_token(data.get("gemini_token", ""))
        return profile


@dataclass
class Config:
    """Main configuration container."""

    profiles: dict[str, Profile] = field(default_factory=dict)
    active_profile: str = "default"

    def __post_init__(self):
        """Ensure default profile exists."""
        if "default" not in self.profiles:
            self.profiles["default"] = Profile(name="default")

    @property
    def current_profile(self) -> Profile:
        """Get the currently active profile."""
        if self.active_profile not in self.profiles:
            self.active_profile = "default"
        return self.profiles[self.active_profile]

    def add_profile(self, profile: Profile) -> None:
        """Add or update a profile."""
        self.profiles[profile.name] = profile

    def delete_profile(self, name: str) -> bool:
        """Delete a profile. Cannot delete 'default'."""
        if name == "default":
            return False
        if name in self.profiles:
            del self.profiles[name]
            if self.active_profile == name:
                self.active_profile = "default"
            return True
        return False

    def save(self) -> None:
        """Save configuration to disk."""
        config_file = get_config_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "active_profile": self.active_profile,
            "profiles": {name: p.to_dict() for name, p in self.profiles.items()},
        }
        config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from disk."""
        config_file = get_config_file()

        if not config_file.exists():
            config = cls()
            config.save()
            return config

        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            profiles = {name: Profile.from_dict(p) for name, p in data.get("profiles", {}).items()}
            return cls(
                profiles=profiles,
                active_profile=data.get("active_profile", "default"),
            )
        except Exception:
            # If config is corrupted, start fresh
            return cls()


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """Reload config from disk."""
    global _config
    _config = Config.load()
    return _config


def get_config_path() -> Path:
    """Get the path to the config file."""
    return get_config_file()
