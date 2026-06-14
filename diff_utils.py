import os
import requests
from dotenv import load_dotenv

load_dotenv()   # 加载环境变量

def get_pr_diff(repo_owner: str, repo_name: str, pr_number: int) -> str:
    """
    从 GitHub 获取指定 PR 的 diff 文本。
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("请在 .env 中设置 GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"获取 diff 失败，HTTP {response.status_code}: {response.text}")