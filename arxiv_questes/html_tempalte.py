from pyquery import PyQuery as pq
import re
from urllib.parse import urljoin
import logging
import requests
from arxiv_html import ArxivCrawler

real_html = """
<h1 class="title is-clearfix">
    Showing 1-50 of 1158 results for all: <span class="mathjax">Vehicle+trajectory+prediction</span>
</h1>
"""

class CustomArxivCrawler(ArxivCrawler):
    def __init__(self, query):
        # 调用父类的初始化方法
        super().__init__(query,div='linux')
        # 通过父类的方法来获取对应的HTML方法
        self.html = self.scrape_index()

    def get_total_pages(self):
        # 使用 pyquery 解析 HTML
        doc = pq(self.html)
        # 使用 CSS 选择器定位目标元素并获取文本
        result_text = doc('.title.is-clearfix').text()
        # 提取总页数
        total_pages_match = re.search(r'Showing (\d+)[–-](\d+) of (\d[\d,]*)\s*results', result_text)
        if total_pages_match:
            total_pages_str = total_pages_match.group(3).replace(',', '')
            # 每页的论文数量
            end_num_str = total_pages_match.group(2)
            total_pages = int(total_pages_str)
            pages_num = total_pages // int(end_num_str)
            print(f"总结果为: {total_pages}")
            print(f"总页数为: {pages_num}")
            return pages_num, int(end_num_str)
        else:
            print(result_text)
            print("未找到总页数信息。")
            return None, None

    # 爬取所有页面
    def crawl_all_pages(self):
        pages_num, end_num = self.get_total_pages()
        if pages_num is not None:
            start_num = 0
            for i in range(pages_num):
                start_num = start_num + end_num
                query_param = f"start={start_num}"
                full_url = self.base_url + '&' + query_param
                print(f"当前页面为: {full_url}")
                print(self.scrape_page(full_url))


if __name__ == '__main__':
    query = 'Vehicle+trajectory+prediction'
    crawler = CustomArxivCrawler(query)
    crawler.get_total_pages()