# 需申请API_KEY：https://platform.deepseek.com/
import os
import requests
from dotenv import load_dotenv  # 新增环境变量库

# 修改环境变量加载方式（指定绝对路径）
from pathlib import Path

# 计算项目根目录路径（向上两级）
project_root = Path(__file__).parent.parent
env_path = project_root / "API_KEY.env"
print(f"加载环境变量路径: {env_path}")
print(f"环境变量存在性: {env_path.exists()}")
# 显式加载指定路径的.env文件
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("错误：未找到DEEPSEEK_API_KEY环境变量")
    print("请检查：1. .env文件是否存在 2. 变量名是否正确 3. 文件路径")
else:
    print("DeepSeek API 调用成功")


DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
def parse_with_deepseek(text):
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",  # 从环境变量读取
        "Content-Type": "application/json"
    }
    payload = {
        # 模型采用DeepSeek-R1
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1  # 降低随机性
    }


    try:
        # 发送 POST 请求到DeepSeek API
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        # 检查状态码
        response.raise_for_status() 
        # 解析响应内容
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            print("响应内容不符合预期:", result)
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误发生: {req_err}")
        return None
    except ValueError as json_err:
        print(f"JSON 解析错误发生: {json_err}")
        return None


# 专业级Prompt设计
system_prompt = """你是一名学术论文解析专家，请从文本中提取以下信息（JSON格式）：
{
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "keywords": ["关键词1", "关键词2"],
  "abstract": "摘要文本",
  "formulas": [
    {"id": "eq1", "latex": "公式LaTeX"},
  ],
  "references": [
    {"title": "引用论文标题", "year": 2020}
  ]
}
要求：
1. 公式保留原始上下文编号（如Eq.1）
2. 作者名格式为"姓氏, 名字首字母."
3. 引用文献需去重
4. 若无对应内容留空"""