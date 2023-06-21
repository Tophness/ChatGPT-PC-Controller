from openai_chat import OpenAIChat
import re
import requests
import random
import uuid
import json
import configparser
import base64
import os

config_file = 'config.ini'

class OpenAILoader:
    def save_config(self, email, password, webdriver_path, chrome_path, user_data_dir, access_token, cookie):
        config = configparser.ConfigParser()
        config['OpenAI'] = {
            'email': email,
            'password': password,
            'webdriver_path': webdriver_path,
            'chrome_path': chrome_path,
            'user_data_dir': user_data_dir
        }
        config['Access'] = {
            'access_token': access_token,
            'cookie': base64.b64encode(cookie.encode()).decode()
        }
        
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(config_file)

        email = None
        password = None
        webdriver_path = 'C:\\Program Files\\Google\\Application\\Chrome\\chromedriver.exe'
        chrome_path = 'C:\\Program Files\\Google\\Application\\Chrome\\chrome.exe'
        user_data_dir = os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\Default'
        access_token = None
        cookie = None

        openai_section = None
        access_section = None
        if('OpenAI' in config):
            openai_section = config['OpenAI']
        if('Access' in config):
            access_section = config['Access']

        if(openai_section):
            email = openai_section.get('email')
            password = openai_section.get('password')
            webdriver_path = openai_section.get('webdriver_path')
            chrome_path = openai_section.get('chrome_path')
            user_data_dir = openai_section.get('user_data_dir')
        if(access_section):
            access_token = access_section.get('access_token', '')
            cookie = access_section.get('cookie', '')
            if(cookie):
                cookie = base64.b64decode(cookie).decode()
        return email, password, webdriver_path, chrome_path, user_data_dir, access_token, cookie

    def get_second_last_chunk_text(self, data):
        chunks = data.split('\n\n')
        if len(chunks) < 3:
            return None
        second_last_chunk = chunks[-3]
        try:
            json_data = json.loads(second_last_chunk[6:])
            regex = re.compile(r'"id": "([^"]+)",.*"conversation_id": "([^"]+)"')
            match = regex.search(second_last_chunk)
            if match:
                id, conversation_id = match.group(1, 2)
                return [json_data['message']['content']['parts'], id, conversation_id]
        except json.JSONDecodeError as error:
            print('Error parsing JSON:', error)
        return None

    def extract_url(self, data):
        regex = re.compile(r'(https?://[^\s]+)')
        match = regex.search(data)
        if match:
            return match.group(0)
        return None

    def chat(self, prompt, model, access_token, cookie):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/event-stream',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Referer': 'https://chat.openai.com/',
            'Alt-Used': 'chat.openai.com',
            'Connection': 'keep-alive',
            'Cookie': cookie,
            'Origin': 'https://chat.openai.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }
        payload = {
            'action': 'next',
            'messages': [{
                'content': {
                    'content_type': 'text',
                    'parts': [prompt]
                },
                'id': str(uuid.uuid4()),
                'role': 'user'
            }],
            'model': 'text-davinci-002-render-sha',
            'parent_message_id': str(uuid.uuid4())
        }
        response = requests.post('https://chat.openai.com/backend-api/conversation', headers=headers, json=payload)
        if response.status_code == 200:
            response_text = response.text
            data = self.get_second_last_chunk_text(response_text)
            return data[0]
        else:
            print('Error:', response.status_code)
            return None

    def start(self, prompt, bypass=False):
        email, password, webdriver_path, chrome_path, user_data_dir, access_token, cookie = self.load_config()
        if not email or not password:
            email = input("Enter your email: ")
            password = input("Enter your password: ")
        if(bypass or not access_token or not cookie):
            chatToken = OpenAIChat(email, password, webdriver_path, chrome_path, user_data_dir)
            access_token, cookie = chatToken.login()
            self.save_config(email, password, webdriver_path, chrome_path, user_data_dir, access_token, cookie)
        return self.chat(prompt, "text-davinci-002-render-sha", access_token, cookie)