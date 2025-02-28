# 用于测试CSS选择器的选择效果

# 假设 html 是你已经获取到的关键字对应页面的 HTML 内容
html = """
<h1 class="title is-clearfix">
    
        Showing 1–50 of 11 results for all: <span class="mathjax">Vehicle+trajectory+prediction</span>
    
</h1>
"""

from pyquery import PyQuery as pq

# 使用 pyquery 解析 HTML
doc = pq(html)

# 使用 CSS 选择器定位目标元素并获取文本
result_text = doc('.title.is-clearfix').text()

# 提取总页数
import re
total_pages_match = re.search(r'of (\d[\d,]*)\s*results', result_text)
if total_pages_match:
    total_pages_str = total_pages_match.group(1).replace(',', '')
    total_pages = int(total_pages_str)
    print(f"总页数: {total_pages}")
else:
    print("未找到总页数信息。")

# 打印结果
print(result_text)
