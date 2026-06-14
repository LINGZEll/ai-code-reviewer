import os
import requests
from dotenv import load_dotenv

load_dotenv()


def post_pr_comment(repo_owner: str, repo_name: str, pr_number: int, comment_body: str):
    """
    发布普通评论到 PR（保留原有功能，以备不时之需）
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("请在 .env 中设置 GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment_body}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("普通评论发布成功")
        return response.json()
    else:
        raise Exception(f"发布评论失败: {response.status_code} {response.text}")


def submit_pr_review(repo_owner: str, repo_name: str, pr_number: int, body: str, event: str = "COMMENT"):
    """
    提交 PR 审查意见（Review），可标记通过/请求修改/仅评论。
    如果遇到“不能对自己的 PR 请求修改”错误，自动降级为普通评论。
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("请在 .env 中设置 GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": body,
        "event": event
    }
    response = requests.post(url, headers=headers, json=data)

    # 成功
    if response.status_code in (200, 201):
        print(f"Review 提交成功，event={event}")
        return response.json()

    # 特殊处理：不能对自己的 PR 请求修改
    if response.status_code == 422 and "on your own pull request" in response.text:
        print("检测到不能对自己的 PR 请求修改，降级为普通评论")
        return post_pr_comment(repo_owner, repo_name, pr_number, body)

    # 其他错误
    raise Exception(f"提交 Review 失败: {response.status_code} {response.text}")