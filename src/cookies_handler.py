import pickle
import logger


class CookiesHandler():
    
    def __init__(self):
        self.path = 'cookies'
        self.logger = logger.create_rotating_log()

    def save_cookies(self, request_cookies, filename):
        with open(f'{self.path}/Thread-{filename}', 'wb') as f:
            pickle.dump(request_cookies, f)
            self.logger.info(f'Save cookies of Thread-{filename}')

    def load_cookies(self, filename):
        with open(f'{self.path}/Thread-{filename}', 'rb') as f:
            self.logger.info(f'Load cookies of Thread-{filename}')
            return pickle.load(f)