import asyncio
import re
import base64
from pathlib import Path
from typing import List, Callable, Dict, Optional
from pdfrw import PdfReader, PdfWriter

from .browser import BrowserEngine
from .utils import sanitize_filename
from ..config import config

class LetterDownloader:
    def __init__(self, browser_engine: BrowserEngine):
        self.browser = browser_engine
        self.stop_requested = False
        
    def _add_metadata(self, pdf_path: Path, letter_count: int, penpal_name: str):
        """Adds metadata to the PDF file."""
        try:
            trailer = PdfReader(str(pdf_path))
            trailer.Info.Letter = str(letter_count)
            trailer.Info.Penpal = penpal_name
            PdfWriter(str(pdf_path), trailer=trailer).write()
        except Exception as e:
            print(f"Error adding metadata to {pdf_path}: {e}")

    async def get_penpals(self) -> Dict[str, str]:
        """
        Scans the home page for penpals.
        Returns a dict of {name: profile_url} (or just list of names/elements if simplified).
        Currently just returns a list of names for selection.
        """
        if not self.browser.page:
            return {}
            
        if "home" not in self.browser.page.url:
            await self.browser.page.goto("https://web.slowly.app/home")
            await self.browser.page.wait_for_load_state("networkidle")

        penpals = {}

        friend_links = await self.browser.page.locator(".side-bar a[href^='/friend/']").all()
        
        for link in friend_links:
            name_el = link.locator("h6")
            if await name_el.count() > 0:
                name = await name_el.inner_text()
                if name:
                    penpals[name] = name 
        
        return penpals

    async def process_penpal(self, penpal_name: str, progress_callback: Optional[Callable] = None):
        """
        Navigates to a penpal's letters and downloads them.
        """
        page = self.browser.page
        if not page:
            return

        print(f"Processing {penpal_name}...")
        
        try:
            await page.locator(f".side-bar h6:text-is('{penpal_name}')").click()
        except Exception as e:
            print(f"Direct click failed ({e}), trying strict False or partial match...")
            await page.locator(f".side-bar h6:has-text('{penpal_name}')").first.click()
            
        
        await page.wait_for_url("**/friend/**")
        
        try:
             await page.wait_for_selector(".col-6.col-xl-4.mb-3", timeout=5000)
        except:
             if progress_callback: progress_callback(f"No letters found for {penpal_name} (or timeout)")
             return
        
        last_height = await page.evaluate("document.body.scrollHeight")
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000) # Wait for load
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        letters = await page.locator(".col-6.col-xl-4.mb-3").all()
        total_letters = len(letters)
        print(f"Found {total_letters} letters for {penpal_name}")
        
        safe_penpal_name = sanitize_filename(penpal_name)
        penpal_dir = config.download_path / safe_penpal_name
        penpal_dir.mkdir(parents=True, exist_ok=True)
        
 
        
        for i in range(total_letters):
            if self.stop_requested:
                break
                

            
            try:
                current_letters_loc = page.locator(".col-6.col-xl-4.mb-3")
                count = await current_letters_loc.count()
                
                if i >= count:
                    print(f"Index {i} out of range (count {count}). List changed?")
                    break
                    
                await current_letters_loc.nth(i).click()
                
                signature_loc = page.locator(".media-body.mx-3.mt-2")
                try:
                    await signature_loc.wait_for(timeout=5000)
                except:
                    print(f"Signature not found for letter {i}, assuming load error.")
                    await page.go_back()
                    await page.wait_for_selector(".col-6.col-xl-4.mb-3")
                    continue
                
                text_content = await signature_loc.inner_text() 
                lines = text_content.split('\n')
                date_str = "UnknownDate"
                if len(lines) > 1:
                     date_line = lines[1]
                     date_str = sanitize_filename(date_line)[:20]
                
                filename = f"letter_{total_letters - i}_{safe_penpal_name}.pdf" 
                
                output_path = penpal_dir / filename
                
                if output_path.exists():
                     print(f"Skipping {filename}, exists.")
                else:
                    await page.pdf(path=output_path, format="A4", print_background=True)
                    self._add_metadata(output_path, total_letters - i, penpal_name)
                    
                    if progress_callback:
                        progress_callback(f"Downloaded {filename}")

                back_btn = page.locator("a.flip.active").first
                if await back_btn.count() > 0:
                    await back_btn.click()
                else:
                    await page.go_back()
                
                await page.wait_for_selector(".col-6.col-xl-4.mb-3")
                
            except Exception as e:
                print(f"Error processing letter {i} for {penpal_name}: {e}")
                if "friend" not in page.url:
                     await page.go_back()
                try:
                    await page.wait_for_selector(".col-6.col-xl-4.mb-3", timeout=5000)
                except:
                    pass

        print(f"Finished {penpal_name}")
