import arxiv
import time
import requests
import yaml

class ArxivPaperCrawler:
    def __init__(self, query, args_path):
        # 初始化查询关键字和从 YAML 文件读取参数
        self.query = query
        with open(args_path, 'r', encoding='utf-8') as f:
            self.args = yaml.safe_load(f)

    def crawl_papers(self):
        # 从 YAML 文件中获取请求头和最大查询数量
        headers = self.args.get('headers', {})
        max_results = self.args.get('max_results', 5)
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
            response = requests.get(result.pdf_url, headers=headers)
            with open(f"{result.entry_id.split('/')[-1]}.pdf", 'wb') as f:
                f.write(response.content)
            time.sleep(1)
        print(f"获取到 {len(papers)} 篇论文")
        for num, paper in enumerate(papers):
            print(f'第{num}篇论文的摘要是{paper["abstract"]}')
        return papers

# 示例调用
if __name__ == "__main__":
    query = 'all:"graph neural network" OR all:"GNN"'
    args_path = 'config.yaml'  # 假设 YAML 文件名为 config.yaml
    crawler = ArxivPaperCrawler(query, args_path)
    papers = crawler.crawl_papers()


