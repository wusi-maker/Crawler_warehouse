import requests
import logging
import re
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import multiprocessing

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://arxiv.org/search/'

class ArxivCrawler:
    def __init__(self, query):
        self.query = query
        # 请求头，用于模拟浏览器行为
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'}

    def scrape_page(self, url):
        logging.info('scraping %s...', url)
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            logging.error('get invalid status code %s while scraping %s', response.status_code, url)
        except requests.RequestException:
            logging.error('error occurred while scraping %s', url, exc_info=True)

    def scrape_index(self):
        params = {
            'query': self.query,
            'searchtype': 'all',
            'source': 'header'
        }
        index_url = BASE_URL
        return self.scrape_page(index_url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()]))

    # 通过使用
    def parse_index(self, html):
        doc = pq(html)
        items = doc('.arxiv-result').items()
        for item in items:
            href = item.find('p.list-title a').attr('href')
            details_url = urljoin(BASE_URL, href)
            logging.info('get item url %s', details_url)
            yield details_url

    def scrape_detail(self, url):
        return self.scrape_page(url)

    def parse_detail(self, html):
        doc = pq(html)
        # 这里可以根据实际页面结构解析详细信息
        title = doc('h1.title.mathjax').text()
        abstract = doc('blockquote.abstract.mathjax').text()
        return {
            'title': title,
            'abstract': abstract
        }

    def main(self):
        index_html = self.scrape_index()
        logging.info(f'get key page html{index_html}')
        
        # detail_urls = self.parse_index(index_html)
        # for detail_url in detail_urls:
        #     detail_html = self.scrape_detail(detail_url)
        #     # data = self.parse_detail(detail_html)
        #     logging.info('get detail data %s', )

if __name__ == '__main__':
    query = 'Vehicle+trajectory+prediction'
    crawler = ArxivCrawler(query)
    crawler.main()