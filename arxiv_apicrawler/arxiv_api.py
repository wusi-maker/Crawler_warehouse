import arxiv
import time
import requests
from typing import List, Dict, Any
from datetime import datetime

import ast
import argparse
import yaml
import os


def get_parser():
    parser = argparse.ArgumentParser(description='Arxiv Paper Crawler')

    # 添加保存文件路径参数
    parser.add_argument('--save_base_dir', type=str, 
                        default='./result/',help='保存文件路径')
    parser.add_argument('--config', type=str,
                        default='config',help='保存文件路径')
    # 添加基础保存参数的路径
    parser.add_argument('--base_path', type=str, 
                        default='.', help='保存yaml文件的路径')

    # 论文爬取相关参数
    parser.add_argument('--max_results', type=int, 
                        default=5, help='最大查询数量')
    parser.add_argument('--headers', type=ast.literal_eval, 
                        default={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'}, help='请求头')
    parser.add_argument('--sleep_time', type=int, 
                        default=1, help='请求间隔时间')
    return parser

def load_arg(parser, p):
    # save arg
    if  os.path.exists(p.config):
        with open(p.config, 'r') as f:
            default_arg = yaml.safe_load(f)

        key = vars(p).keys()
        for k in default_arg.keys():
            if k not in key:
                print(f'WRONG ARG: {k}')
                raise ValueError(f'Unexpected argument {k} in config file')
        parser.set_defaults(**default_arg)
        return parser.parse_args()
    else:
        return False

def save_arg(args):
    # save arg
    arg_dict = vars(args)
    if not os.path.exists(args.save_base_dir):
        os.makedirs(args.save_base_dir)
    with open(args.config, 'w') as f:
        yaml.dump(arg_dict, f)


class ArxivPaperCrawler:
    def __init__(self, query_list:List[str]):
        self.query=" OR ".join(f'all:"{q}"' for q in query_list)
        current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")

        # 初始化查询关键字和 YAML 文件路径
        parser=get_parser()
        p=parser.parse_args()
        p.config=p.save_base_dir+p.config+'.yaml' 

        query_dir="_".join(query_list)
        self.original_dir=p.save_base_dir+query_dir+'/original_dir/'
        self.processed_dir=p.save_base_dir+query_dir+'/processed_dir/' 
        if not load_arg(parser, p):
           save_arg(p)
        self.args = load_arg(parser, p)



    def crawl_papers(self):
        # 从 YAML 文件中获取请求头和最大查询数量
        headers = self.args.headers
        max_results = self.args.max_results    
        client = arxiv.Client()
        search = arxiv.Search(
            query=self.query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        papers = []
        for result in client.results(search):
            abstract = result.summary.split(' ')
            if len(abstract) > 50:
                abstract = abstract[:50] + ['...']
            result_abstract = ' '.join(abstract)
            paper = {
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "abstract": result_abstract,
                "published": result.published.strftime("%Y-%m-%d"),
                "pdf_url": result.pdf_url,
                "arxiv_id": result.entry_id.split('/')[-1]
            }
            papers.append(paper)
            # 下载论文 PDF
            if not os.path.exists(self.original_dir):
                os.makedirs(self.original_dir)
            pdf_path = os.path.join(self.original_dir, f"{result.entry_id.split('/')[-1]}.pdf")
             # 检查文件是否已经存在
            if not os.path.exists(pdf_path):
                response = requests.get(result.pdf_url, headers=headers)
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                time.sleep(self.args.sleep_time)


        for num, paper in enumerate(papers):
            print(f'第{num}篇论文的摘要是{paper["abstract"]}')
        return papers

# 示例调用
if __name__ == "__main__":
    query = ["graph neural network", "GNN"]
    crawler = ArxivPaperCrawler(query)
    papers = crawler.crawl_papers()


