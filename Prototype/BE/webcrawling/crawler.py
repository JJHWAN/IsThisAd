from urllib.parse import quote
import pandas as pd

from Prototype.BE.webcrawling.constant import *
from Prototype.BE.webcrawling.package.thread import ThreadWithReturnValue
from Prototype.BE.webcrawling.worker import  Worker

class BlogCrawler:

    def __init__(self, query):
        # 변경되지 않을 attrs
        self.query = query
        self.quote = quote(self.query)
        self.workers = []
        for i in range(0, MAX_THREAD):
            self.workers.append(Worker(i))

    def get_data_with_query(self):
        end_point = False
        data = []
        index = 0
        while end_point:
            threads = []
            for i in range(0, MAX_THREAD):
                t = ThreadWithReturnValue(target=self.workers[i].get_data_with_index, args=(index+i, ))
                t.start()
                threads.append(t)
            index += MAX_THREAD

            for thread in threads:
                tmp = thread.join()
                if len(tmp) == 1:
                    end_point = True
                data += thread.join()
            print(index, ": done")

        self.write_csv(data)

    def write_csv(self):
        df = pd.DataFrame(data, columns=['post_link', 'image_src', 'blog_text'])
        file_name = "data" + self.query
        df.to_csv('C:\\Users\\USER\\Desktop\\data\\' + file_name + '.csv', encoding='utf-8')
