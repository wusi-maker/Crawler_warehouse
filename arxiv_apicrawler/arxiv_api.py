import arxiv

# 定义搜索关键词和参数
search_query = 'all:"graph neural network" OR all:"GNN"'  # 自定义关键词逻辑组合
max_results = 100  # 每次查询最大数量

# 创建搜索客户端
client = arxiv.Client()

# 执行搜索
search = arxiv.Search(
    query=search_query,
    max_results=max_results,
    sort_by=arxiv.SortCriterion.SubmittedDate  # 按提交时间排序
)

# 分批获取结果（避免API限流）
papers = []
for result in client.results(search):
    paper = {
        "title": result.title,
        "authors": [a.name for a in result.authors],
        "abstract": result.summary,
        "published": result.published.strftime("%Y-%m-%d"),
        "pdf_url": result.pdf_url,
        "arxiv_id": result.entry_id.split('/')[-1]  # 提取ID如 arXiv:2001.12345
    }
    papers.append(paper)
    # 可选：下载PDF（需安装requests）
    # import requests
    # response = requests.get(result.pdf_url)
    # with open(f"{result.entry_id.split('/')[-1]}.pdf", 'wb') as f:
    #     f.write(response.content)

print(f"获取到 {len(papers)} 篇论文")
for i in range(len(papers)):
    print(papers[i])
