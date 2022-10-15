from urllib.parse import quote

from Prototype.BE.webcrawling.constant import *
from Prototype.BE.webcrawling.package.thread import ThreadWithReturnValue
from Prototype.BE.webcrawling.worker import Worker


class BlogCrawler:

    def __init__(self, query):
        # 변경되지 않을 attrs
        self.query = query
        self.quote = quote(self.query)
        self.workers = []
        for i in range(0, MAX_THREAD):
            self.workers.append(Worker(self.query, i))

    def get_data_with_query(self):
        threads = []
        for i in range(0, MAX_THREAD):
            t = ThreadWithReturnValue(target=(self.workers[i]).data_with_index, args=(i,))
            t.start()
            threads.append(t)

        for i in range(0, MAX_THREAD):
            threads[i].join()
