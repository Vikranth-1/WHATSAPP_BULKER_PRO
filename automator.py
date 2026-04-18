from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from urllib.parse import quote
import os
import threading
import random

class WhatsAppAutomator:
    def __init__(self, logger_callback=None):
        self.driver = None
        self.logger = logger_callback or print
        self.is_running = False
        self.stop_requested = False

    def log(self, message):
        self.logger(message)

    def get_user_data_dir(self):
        """Returns the default user data directory path based on the operating system."""
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ['LOCALAPPDATA'], 'AnirudhBagri', 'WABulker', 'User Data')
        elif os.name == 'posix':
            if os.uname()[0] == 'Darwin':
                return os.path.join(os.environ['HOME'], 'Library', 'AnirudhBagri', 'WABulker', 'User Data')
            else:
                return os.path.join(os.environ['HOME'], '.config', 'anirudhbagri', 'wabulker', 'user_data')
        else:
            return os.path.join(os.getcwd(), 'whatsapp_user_data')

    def initialize_driver(self):
        self.log("Initializing Chrome browser...")
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--profile-directory=Default")
        user_data_dir = self.get_user_data_dir()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Ensure directory exists
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.log("Browser initialized successfully.")

    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.log("Browser closed.")

    def send_messages(self, numbers, message, min_delay=8, max_delay=15):
        self.is_running = True
        self.stop_requested = False
        
        try:
            for idx, number in enumerate(numbers):
                if self.stop_requested:
                    self.log("Process stopped by user.")
                    break
                
                number = number.strip()
                if not number:
                    continue
                
                self.log(f"({idx+1}/{len(numbers)}) Sending to {number}...")
                
                url = f'https://web.whatsapp.com/send?phone={number}&text={quote(message)}'
                
                sent = False
                for attempt in range(3):
                    if self.stop_requested: break
                    try:
                        self.driver.get(url)
                        # Wait for the send button to be clickable
                        wait = WebDriverWait(self.driver, 30)
                        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']")))
                        sleep(1)
                        send_btn.click()
                        sent = True
                        sleep(3) # Wait for message to be sent
                        self.log(f"✅ Successfully sent to {number}")
                        
                        # Random delay before next message
                        if idx < len(numbers) - 1: # Don't wait after the last one
                            delay = random.randint(min_delay, max_delay)
                            self.log(f"⏳ Waiting {delay}s before next message...")
                            sleep(delay)
                        break
                    except Exception as e:
                        self.log(f"⚠️ Retry {attempt+1}/3 for {number}...")
                        sleep(2)
                
                if not sent and not self.stop_requested:
                    self.log(f"❌ Failed to send to {number}")

        except Exception as e:
            self.log(f"Critical error: {str(e)}")
        finally:
            self.is_running = False
            self.log("All tasks completed.")

    def login(self):
        self.log("Opening WhatsApp Web. Please scan QR code if needed.")
        if not self.driver:
            self.initialize_driver()
        self.driver.get('https://web.whatsapp.com')
        
    def stop(self):
        self.stop_requested = True
        self.log("Stop requested...")