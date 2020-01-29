import json
import logger


class CookiesHandler():
    
    def __init__(self):
        self.path = '../cookies/'
        self.logger = logger.create_rotating_log()

    def save_cookies(self, request_cookies, filename):
        with open(self.path + filename, 'wb') as f:
            json.dump(request_cookies, f)
            self.logger.info(f'Saved cookies {self.path}{filename}')

    def load_cookies(self, filename):
        with open(self.path + filename, 'rb') as f:
            self.logger.info(f'Loaded cookies {self.path}{filename}')
            return json.load(f)