from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
import json
import time

class OpenAIChat:
    def __init__(self, email, password, webdriver_path, chrome_path, user_data_dir):
        self.email = email
        self.password = password
        self.webdriver_path = webdriver_path
        self.chrome_path = chrome_path
        self.user_data_dir = user_data_dir
        self.driver = None

    def get_access_token(self):
        self.driver.get("https://chat.openai.com/api/auth/session")
        if "accessToken" in self.driver.page_source:
            pre_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            json_response = json.loads(pre_element.text)
            access_token = json_response.get("accessToken")
            return access_token
        else:
            return None

    def format_cookie(self, cookies):
        allowed_names = ['intercom-session-', 'intercom-device-id-', '_puid', '_dd_s', '_cfuvid', '__cf_bm']
        cookie_pairs = []
        for cookie in cookies:
            name = cookie.get('name')
            value = cookie.get('value')
            if name and value:
                for allowed_name in allowed_names:
                    if name.startswith(allowed_name):
                        cookie_pairs.append(f"{name}={value}")
                        break
        formatted_cookie = '; '.join(cookie_pairs)
        return formatted_cookie

    def login(self):
        try:
            chrome_options = Options()
            chrome_options.binary_location = self.chrome_path
            chrome_options.headless=True
            chrome_options.user_data_dir = self.user_data_dir
            self.driver = Chrome(options=chrome_options, executable_path=self.webdriver_path)

            access_token = self.get_access_token()
            cookie = ''

            if "accessToken" not in self.driver.page_source:
                self.driver.get("https://chat.openai.com/auth/login")
                login_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".btn.relative.btn-primary")
                    )
                )
                login_button.click()

                email_input = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_input.send_keys(self.email)
                continue_button = self.driver.find_element(
                    By.XPATH, "//button[contains(.,'Continue')]"
                )
                continue_button.click()

                password_input = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                password_input.send_keys(self.password)
                continue_button = self.driver.find_element(
                    By.XPATH, "//button[contains(.,'Continue')]"
                )
                continue_button.click()

                next_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(text(),'Next')]")
                    )
                )
                next_button.click()

                next_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(text(),'Next')]")
                    )
                )
                next_button.click()

                done_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(text(),'Done')]")
                    )
                )
                done_button.click()

                final_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "div.overflow-hidden.w-full.h-full.relative.flex.z-0")
                    )
                )
                WebDriverWait(self.driver, 60).until(EC.url_to_be("https://chat.openai.com/"))
                time.sleep(1)
                
                access_token = self.get_access_token()

            self.driver.get("https://chat.openai.com/backend-api/accounts/check/v4-2023-04-27")
            WebDriverWait(self.driver, 60).until(EC.url_to_be("https://chat.openai.com/backend-api/accounts/check/v4-2023-04-27"))
            cookie = self.format_cookie(self.driver.get_cookies())
            if access_token:
                return access_token, cookie
            else:
                return "Access Token not found."
        finally:
            if self.driver:
                self.driver.quit()