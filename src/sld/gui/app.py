import customtkinter as ctk
import threading
import asyncio
import queue
from typing import Dict
from ..core.browser import BrowserEngine
from ..core.downloader import LetterDownloader
from ..config import config

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AsyncWorker(threading.Thread):
    def __init__(self, app_queue):
        super().__init__()
        self.app_queue = app_queue
        self.loop = asyncio.new_event_loop()
        self.browser = BrowserEngine()
        self.downloader = LetterDownloader(self.browser)
        self.running = True

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        self.submit(self.browser.close())
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Slowly Letter Downloader (Modern)")
        self.geometry("900x600")
        
        # Communication queue
        self.msg_queue = queue.Queue()
        self.worker = AsyncWorker(self.msg_queue)
        self.worker.start()
        
        self.penpal_vars: Dict[str, ctk.IntVar] = {}
        
        self._setup_ui()
        self._check_queue()
        
    def _setup_ui(self):
        # Grid config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Panel (Controls + Friends)
        self.left_panel = ctk.CTkFrame(self, width=250)
        self.left_panel.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self.left_panel, text="Control Panel", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=10)
        
        # Buttons
        self.btn_login = ctk.CTkButton(self.left_panel, text="1. Login (Open Browser)", command=self.action_login)
        self.btn_login.pack(pady=5, padx=10, fill="x")
        
        self.btn_scan = ctk.CTkButton(self.left_panel, text="2. Scan Friends", command=self.action_scan)
        self.btn_scan.pack(pady=5, padx=10, fill="x")
        
        self.btn_download = ctk.CTkButton(self.left_panel, text="3. Download Selected", command=self.action_download, fg_color="green")
        self.btn_download.pack(pady=20, padx=10, fill="x")

        # Scrollable Friend List
        self.scroll_friends = ctk.CTkScrollableFrame(self.left_panel, label_text="Friends")
        self.scroll_friends.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Right Panel (Logs)
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        
        self.lbl_log = ctk.CTkLabel(self.right_panel, text="Logs", font=("Arial", 16))
        self.lbl_log.pack(anchor="w", padx=10, pady=5)
        
        self.txt_log = ctk.CTkTextbox(self.right_panel)
        self.txt_log.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.log_message("Welcome! Please click 'Login' to start.")
        
    def log_message(self, msg: str):
        self.txt_log.insert("end", f"{msg}\n")
        self.txt_log.see("end")

    def _check_queue(self):
        try:
            while True:
                msg_type, content = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self.log_message(content)
                elif msg_type == "friends":
                    self.populate_friends(content)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)
            
    def populate_friends(self, friends: dict):
        # Clear existing
        for widget in self.scroll_friends.winfo_children():
            widget.destroy()
        self.penpal_vars.clear()
        
        if not friends:
            self.log_message("No friends found. did you scroll down in the browser?")
            return

        for name in friends:
            var = ctk.IntVar(value=1)
            cb = ctk.CTkCheckBox(self.scroll_friends, text=name, variable=var)
            cb.pack(anchor="w", pady=2)
            self.penpal_vars[name] = var
            
        self.log_message(f"Found {len(friends)} friends.")

    # --- Actions ---
    
    def action_login(self):
        self.log_message("Launching browser for login...")
        self.worker.submit(self._async_login())
        
    async def _async_login(self):
        await self.worker.browser.login_mode()
        self.msg_queue.put(("log", "Browser opened. Please login manually in the window."))
        # Wait for login sync? optional.

    def action_scan(self):
        self.log_message("Scanning for friends...")
        self.worker.submit(self._async_scan())
        
    async def _async_scan(self):
        try:
            friends = await self.worker.downloader.get_penpals()
            self.msg_queue.put(("friends", friends))
        except Exception as e:
            self.msg_queue.put(("log", f"Error scanning: {e}"))

    def action_download(self):
        selected = [name for name, var in self.penpal_vars.items() if var.get() == 1]
        if not selected:
            self.log_message("No friends selected!")
            return
            
        self.log_message(f"Starting download for: {', '.join(selected)}")
        self.worker.submit(self._async_download(selected))
        
    async def _async_download(self, names):
        for name in names:
            self.msg_queue.put(("log", f"Downloading letters for {name}..."))
            try:
                await self.worker.downloader.process_penpal(
                    name, 
                    progress_callback=lambda m: self.msg_queue.put(("log", m))
                )
            except Exception as e:
                self.msg_queue.put(("log", f"Error downloading {name}: {e}"))
        self.msg_queue.put(("log", "All downloads finished."))

    def on_closing(self):
        self.worker.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
