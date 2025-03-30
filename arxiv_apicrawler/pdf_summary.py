# 需申请API_KEY：https://platform.deepseek.com/
import os
import requests
from dotenv import load_dotenv  # 新增环境变量库

# 修改环境变量加载方式（指定绝对路径）
from pathlib import Path


DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def check_api_connection(max_Reconnect=5):
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "检查API连接"},
            {"role": "user", "content": "测试连接"}
        ],
        "temperature": 0.1
    }
    reconnect_count = 0
    while reconnect_count <= max_Reconnect:
        try:
            response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
            # 检查状态码:- 状态码为 200-299：正常继续;状态码为 400-599：抛出 HTTPError 异常
            response.raise_for_status()
            print("DeepSeek API 连接成功")
            return True
        except requests.exceptions.RequestException as e:
            print(f"连接失败，第 {reconnect_count + 1} 次尝试重连: {e}")
            reconnect_count += 1
    print("达到最大重连次数，无法连接到DeepSeek API，终止流程。")
    return False


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


if __name__ == "__main__":
    # 检查API连接
    print(check_api_connection())

# 专业级Prompt设计
system_prompt = """你是一名专业的学术论文解析专家，请严格按以下结构提取信息（JSON格式）：

{
  "metadata": {
    "title": "论文标题（英文原标题）",
    "authors": [
      {
        "family_name": "姓氏",
        "given_initial": "名字首字母",
        "affiliation": "所属机构"
      }
    ],
    "keywords": ["关键词1", "关键词2", "关键词3（不超过5个）"],
    "publication": {
      "journal": "期刊/会议名称",
      "year": 2023,
      "doi": "数字对象唯一标识符"
    }
  },
  "content": {
    "abstract": {
      "text": "摘要全文",
      "contribution": "本文的核心创新点"
    },
    "methodology": [
      {
        "section_title": "章节标题",
        "paragraphs": [
          {
            "heading": "子标题",
            "content": "技术细节描述",
            "technical_details": {
              "algorithms": ["算法名称1", "算法名称2"],
              "framework": "方法框架的文字描述"
            }
          }
        ]
      }
    ],
    "formulas": [
      {
        "id": "eq1",
        "latex": "完整的LaTeX公式",
        "context": "公式所在的上下文描述",
        "section": "公式所在章节"
      }
    ]
  },
  "experiments": {
    "baselines": ["对比算法1", "对比算法2"],
    "datasets": [
      {
        "name": "数据集名称",
        "stats": {
          "samples": 10000,
          "features": 256,
          "classes": 10
        }
      }
    ],
    "metrics": [
      {
        "name": "评估指标名称",
        "value": 98.5,
        "unit": "%"
      }
    ],
    "results": {
      "main_result": "主要实验结果总结",
      "comparison": "与基线的对比分析"
    }
  },
  "references": [
    {
      "title": "引用文献标题",
      "authors": ["作者1", "作者2"],
      "year": 2020,
      "context": "在本文中的引用位置说明"
    }
  ]
}

要求：
1. 公式必须保留原始编号并关联上下文，例如：Eq.3 → {"id":"eq3", "section":"3.1 Method Overview"}
2. 作者信息需拆分姓氏和名字首字母（例如：Zhang → "family_name":"Zhang", "given_initial":"Y."）
3. 实验部分需包含数据集统计特征和技术指标的具体数值
4. 参考文献去重标准：标题相同且作者重叠超过50%视为重复
5. 方法论部分按论文实际章节结构分层解析
6. 关键词必须来自论文作者标注的Keywords章节
7. 若某部分无对应内容，保留空对象结构（例如空数组/空对象）"""