from fastapi import FastAPI, Request, HTTPException
import os
import hmac
import hashlib
from dotenv import load_dotenv

from diff_utils import get_pr_diff
from llm import review_code
from github_utils import submit_pr_review
from cache_utils import get_cached_review, save_review_cache

load_dotenv()

app = FastAPI(title="AI Code Reviewer")

# 获取 Webhook Secret（如果未设置，则跳过验证）
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """验证 GitHub webhook 签名"""
    if not WEBHOOK_SECRET:
        # 没有配置 secret，不验证（不安全，但兼容旧版本）
        return True
    if not signature_header:
        return False
    # 签名格式：sha256=xxxxxxxx
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@app.post("/webhook")
async def github_webhook(request: Request):
    # 1. 获取原始请求体（字节）
    body = await request.body()
    # 2. 获取签名头
    signature = request.headers.get("X-Hub-Signature-256")
    # 3. 验证签名
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 4. 解析 JSON
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    if event != "pull_request":
        return {"msg": "忽略非PR事件"}

    action = payload.get("action")
    if action not in ["opened", "reopened", "synchronize"]:
        return {"msg": f"忽略action={action}"}

    pr = payload["pull_request"]
    repo = payload["repository"]
    repo_owner = repo["owner"]["login"]
    repo_name = repo["name"]
    pr_number = pr["number"]

    print(f"收到 PR #{pr_number}, action={action}, 开始审查...")

    try:
        diff_text = get_pr_diff(repo_owner, repo_name, pr_number)
        if not diff_text.strip():
            return {"msg": "diff为空"}

        review_result = get_cached_review(diff_text)
        if review_result:
            print("✅ 命中缓存，直接使用已保存的审查结果")
        else:
            print("🔄 未命中缓存，调用 LLM 审查...")
            review_result = review_code(diff_text)
            save_review_cache(diff_text, review_result)
            print("💾 审查结果已缓存")

        # 自动判断审查结论
        serious_keywords = ["安全风险", "Bug风险", "严重漏洞", "必须修复", "高危", "硬编码"]
        needs_changes = any(kw in review_result for kw in serious_keywords)
        review_event = "REQUEST_CHANGES" if needs_changes else "APPROVE"

        submit_pr_review(repo_owner, repo_name, pr_number, review_result, review_event)
        print(f"PR #{pr_number} 审查完成")
        return {"status": "ok", "pr": pr_number}
    except Exception as e:
        print(f"处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "AI Code Reviewer is running"}