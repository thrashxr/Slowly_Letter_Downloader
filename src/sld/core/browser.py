import os
import asyncio
from typing import Optional, Callable
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from ..config import config

class BrowserEngine:
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False

    async def start(self, headless: bool = True):
        """Starts the Playwright engine."""
        if self.is_running:
            return

        self.playwright = await async_playwright().start()
        
        args = ["--disable-blink-features=AutomationControlled"]
        if not headless:
            args.append("--start-maximized")
            
        try:
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=config.chrome_profile_path,
                channel="chrome",
                headless=headless,
                slow_mo=50, 
                args=args,
                no_viewport=True,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        except Exception as e:
            print(f"Could not launch system Chrome, falling back to bundled Chromium: {e}")
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=config.chrome_profile_path,
                headless=headless,
                slow_mo=50,
                args=args,
                no_viewport=True
            )
        
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
            
        self.is_running = True

    async def login_mode(self):
        """Starts browser in HEADED mode for user to login manually."""
        await self.close() 
        await self.start(headless=False)
        
        if self.page:
            await self.page.goto("https://web.slowly.app", wait_until="networkidle")
            
    async def save_session(self):
        """Saves cookies/storage state to disk."""
        if self.context:
            await self.context.storage_state(path=config.session_path)
            print(f"Session saved to {config.session_path}")

    async def save_session(self):
        """Deprecated: Persistent context saves automatically."""
        pass

    async def close(self):
        """Closes the browser and stops Playwright."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
            
        self.is_running = False
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    async def wait_for_login(self, timeout: int = 300) -> bool:
        """
        Waits for the user to be logged in by checking the URL.
        Returns True if successful, False if timeout.
        """
        if not self.page:
            return False
            
        print("Waiting for login... (Please login in the browser window)")
        
        try:
            await self.page.wait_for_url("**/home", timeout=timeout * 1000)
            print("Login detected!")
            return True
        except Exception as e:
            print(f"Login wait timed out or failed: {e}")
            return False

