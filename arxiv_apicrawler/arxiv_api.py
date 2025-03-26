import arxiv
import time
import requests
from typing import List, Dict, Any
from datetime import datetime

import ast
import argparse
import yaml
import os
# 与处理pdf以减少token的使用】
import re
import fitz
from pdf_summary import parse_with_deepseek,check_api_connection



def get_parser():
    #  从命令行中获取参数
    parser = argparse.ArgumentParser(description='Arxiv Paper Crawler')

    # 添加保存文件路径参数
    parser.add_argument('--save_base_dir', type=str, 
                        default='./result/',help='保存文件路径')
    parser.add_argument('--config', type=str,
                        default='config',help='保存文件路径')
    # 添加基础保存参数的路径
    parser.add_argument('--base_path', type=str, 
                        default='.', help='基础路径')

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
        current_time = datetime.now().strftime("%Y-%m-%d")

        # 初始化查询关键字和 YAML 文件路径
        parser=get_parser()
        p=parser.parse_args()
        p.config=p.save_base_dir+p.config+'.yaml' 

        query_dir="_".join(query_list)
        self.original_dir=p.save_base_dir+query_dir+'/original_dir/'+current_time+'/'
        self.processed_dir=p.save_base_dir+query_dir+'/processed_dir/'+current_time+'/'
        if not load_arg(parser, p):
           save_arg(p)
        self.args = load_arg(parser, p)

    # 解析pdf内容，仅仅提取正文内容
    def extract_main_content(self, pdf_path: str) -> str:
        """专业级学术论文解析方法"""
        doc = fitz.open(pdf_path)
        text_parts = []
        section_blacklist = {'references', 'acknowledgements', 'appendix', 'supplementary'}
        current_section = None
        
        for page in doc:
            text = page.get_text("text")
            for line in text.split('\n'):
                # 识别章节标题（支持数字编号和全大写格式）
                section_match = re.match(r'^\s*(\d+(\.\d+)*)?\s*([A-Z][A-Z\s]+)\s*$', line, re.IGNORECASE)
                if section_match:
                    current_section = section_match.group(3).strip().lower()
                    if current_section in section_blacklist:
                        break  # 遇到黑名单章节则停止收集
                
                # 仅收集有效章节内容
                if current_section not in section_blacklist:
                    text_parts.append(line)
        
        # 后处理流程
        processed_text = self.postprocess_text('\n'.join(text_parts))
        return processed_text or "无法提取有效文本"  # 保证最低返回内容

    def postprocess_text(self, text: str) -> str:
        """文本后处理"""
        # 移除页眉页脚
        text = re.sub(r'\n\d+\n', '\n', text)  # 页码
        text = re.sub(r'arXiv:\d+\.\d+v\d+.*\n', '', text)  # arXiv标识
        
        # 移除公式编号
        text = re.sub(r'\(Eq\.?(\d+)\)', r'(\1)', text)  # 将 (Eq.3) 简化为 (3)
        
        # 合并短行
        text = re.sub(r'-\n(\w)', r'\1', text)  # 处理换行连字符
        max_line_length = 15000  # 定义最大行长度
        return text  # 限制最大长度

    # 根据传入的查询关键字爬取对应pdf并使用API进行解析
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

            # 新增PDF预处理流程
            print(f"开始解析论文 {result.entry_id.split('/')[-1]}")
            try:
                # 使用PyMuPDF提取结构化文本
                full_text = self.extract_main_content(pdf_path)
                print(f"论文解析完成，有效文本长度：{len(full_text)}字符")
            except Exception as e:
                print(f"PDF解析失败: {e}, 回退到摘要处理")
                full_text = result.summary
            if  not check_api_connection():
                print("API连接失败，终止程序")
                break
            # 调用 DeepSeek API 解析
            response_text = parse_with_deepseek(full_text)

            if response_text:
                # 确保处理目录存在
                if not os.path.exists(self.processed_dir):
                    os.makedirs(self.processed_dir)

                # 保存回答文件
                output_path = os.path.join(self.processed_dir, f"{result.entry_id.split('/')[-1]}_summary.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response_text)

        for num, paper in enumerate(papers):
            print(f'第{num}篇论文的摘要是{paper["abstract"]}')
        return papers



# 示例调用
if __name__ == "__main__":
    
    query = ["graph neural network", "Trajectory prediction"]
    crawler = ArxivPaperCrawler(query)
    papers = crawler.crawl_papers()


