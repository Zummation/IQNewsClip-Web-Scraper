from time import sleep
from threading import Thread
from IQNewsClipScraper import IQNewsClipScraper



class IQNewsClipThread():


    def __init__(self, keys=[], sources=[], n_thread=2):
        self.n_thread = n_thread
        self.scrapers = [IQNewsClipScraper() for i in range(n_thread)]
        self.threads = []
        self.thread_queue = [[] for i in range(n_thread)]
        self.container = [(key, source) for key in keys for source in sources]
        
        # put ones to every queue
        for q in self.thread_queue:
            if self.container:
                q += [self.container.pop(0)]


    def _task(self, scraper, queue):
        scraper.login()
        print('A Thread is logging in')
        while queue:
            key, source = queue.pop(0)
            df = scraper.search_all(key, source)
            df.to_csv(f'result/{key}-{source}.csv', index=False)
            print(f'Completed {key}-{source}.csv')


    def start(self):
            
        self.threads = [Thread(target=self._task, args=(self.scrapers[i], self.thread_queue[i])).start() for i in range(self.n_thread)]
        
        # queue arguments in self.container in self.thread_queue
        while True:
            for q in self.thread_queue:
                if len(q) == 1:
                    q += [self.container.pop(0)]
                if not self.container:
                    return
            sleep(1)