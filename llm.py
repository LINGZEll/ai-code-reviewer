from openai import OpenAI
import os
from dotenv import load_dotenv   # 新增这行

load_dotenv()                      # 新增这行：读取 .env 文件

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def review_code(diff_text):

    prompt = f"""
你是一位资深软件工程师。

请审查以下代码变更：

{diff_text}

请从以下方面分析：

1. Bug风险
2. 代码规范
3. 性能问题
4. 安全问题
5. 改进建议

输出简洁专业。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content