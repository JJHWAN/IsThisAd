import re
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup


class Worker:

    def __init__(self, query):
        # 변경되지 않을 attrs
        self.query = query
        self.quote = quote(self.query)
        # 계속 변경될 attrs
        self.url = ""  # for moreContentView Request URL
        self.res = None
        self.soup = None
        self.index = None

    def set_index(self, index):
        self.index = index

    def set_res_soup(self, url):
        """
            set res, soup with url
        """
        self.res = requests.get(url)
        self.res.raise_for_status()  # 문제시 프로그램 종료
        self.soup = BeautifulSoup(self.res.text, "lxml")

    def update_url_viewMorecontent(self):
        query_number = 31 + (self.index - 1) * 30  # 한번에 30개씩 return
        self.url = "https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query=" + quote(
            self.query) + "&rev=44&start=" + str(query_number) \
                   + "&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=&nlu_query=%7B%22r_category%22%3A%2229%22%7D&dkey=0&source_query=&nx_search_query=" \
                   + quote(self.query) + "&spq=0&_callback=viewMoreContents"

    def update_with_posturl(self, url):
        """
        update res, soup and return post link which deleted iframe
        :param url: blog link
        :return: url deleted ifame
        """
        self.res = requests.get(url)
        self.res.raise_for_status()  # 문제시 프로그램 종료
        self.soup = BeautifulSoup(self.res.text, "lxml")

        return "https://blog.naver.com/" + self.soup.iframe["src"]

    def text_scraping(self, url):
        """
        return image link and blog text from blog url
        :param url: blog link with iframe deleted
        :return: [image link], blog text
        """
        res = requests.get(url)
        res.raise_for_status()  # 문제시 프로그램 종료
        soup = BeautifulSoup(self.res.text, "lxml")

        images = self.soup.findAll("img", \
                                   attrs={
                                       "class": ["se-image-resource", "se-sticker-image", "se-inline-image-resource"]})

        image_link = []
        if images:
            for image in images:
                if 'data-lazy-src' in image.attrs:  # for better image
                    image_link.append(image['data-lazy-src'])
                else:
                    image_link.append(image['src'].replace("?type=w80_blur", ""))

        if soup.find("div", attrs={"class": "se-main-container"}):
            text = self.soup.find("div", attrs={"class": "se-main-container"}).get_text()
            text = text.replace("\n", " ")  # 공백 제거
            text = text.replace("\r", " ")
            return image_link, text

        # 만약 스마트에디어 3.0을 사용하는 블로그인 경우
        soup = soup.find("div", attrs={"id": "postViewArea"})
        if soup is not None:
            images = soup.findAll("img")
            if images:
                for image in images:
                    image_link.append(image['src'])
            text = soup.get_text()
            text = text.replace("\n", " ")
            text = text.replace("\r", " ")
            return image_link, text
        else:
            return image_link, None

    def get_data(self):
        """
        return data set from query and index as list
        :return: [post link, [image links], blog text]
        """
        posts = self.soup.find_all("li", attrs={"class": '\\"bx\\"'})
        result_list = []

        for post in posts:
            post_link = post.find("a", attrs={"class": '\\"api_txt_lines'})['href']
            post_link = post_link.replace('\\"', "")
            data = [post_link]

            blog_p = re.compile("blog.naver.com")
            blog_m = blog_p.search(post_link)

            if blog_m:
                images_src, blog_text = self.text_scraping(self.update_url_without_iframe(post_link))
                if blog_text is not None:
                    data.append(images_src)
                    data.append(blog_text)
                result_list.append(data)

        return result_list

    def get_data_with_index(self, index):
        """
        return data set from query & index
        :param index: search index of query
        :return: data set with query & index
        """
        self.set_index(index)
        self.update_url_viewMorecontent(index)
        self.set_res_soup(self, self.url)
        return self.get_data()
