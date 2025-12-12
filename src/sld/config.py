import os
import platform
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    APP_NAME = "SlowlyLetterDownloader"
    
    def __init__(self):
        self.system = platform.system()
        self.user_data_dir = self._get_user_data_dir()
        self.config_file = self.user_data_dir / "config.json"
        
        # Ensure directory exists
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default config
        self.data = self._load_config()

    def _get_user_data_dir(self) -> Path:
        """
        Returns the platform-specific user data directory.
        macOS: ~/Library/Application Support/SlowlyLetterDownloader
        Windows: %APPDATA%/SlowlyLetterDownloader
        Linux: ~/.config/SlowlyLetterDownloader (XDG fallback)
        """
        home = Path.home()
        
        if self.system == "Windows":
            return Path(os.getenv("APPDATA", home / "AppData" / "Roaming")) / self.APP_NAME
        elif self.system == "Darwin":
            return home / "Library" / "Application Support" / self.APP_NAME
        else:
            # Linux / Unix
            xdg_config = os.getenv("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / self.APP_NAME
            return home / ".config" / self.APP_NAME

    def _load_config(self) -> Dict[str, Any]:
        defaults = {
            "download_path": str(Path.home() / "Desktop" / "Slowly Letters"),
            "theme": "System",  # System, Light, Dark
            "letter_format": "pdf", # Future proofing
            "browser_headless": True
        }
        
        if not self.config_file.exists():
            self._save_config(defaults)
            return defaults
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**defaults, **user_config}
        except Exception as e:
            print(f"Error loading config: {e}")
            return defaults

    def _save_config(self, data: Dict[str, Any]):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self._save_config(self.data)
    
    @property
    def download_path(self) -> Path:
        return Path(self.data["download_path"])
    
    @property
    def session_path(self) -> Path:
        return self.user_data_dir / "session.json"

    @property
    def chrome_profile_path(self) -> Path:
        """Directory for persistent Chrome User Data"""
        path = self.user_data_dir / "ChromeProfile"
        path.mkdir(parents=True, exist_ok=True)
        return path

# Singleton instance
config = Config()
