# AI Code Reviewer

基于大语言模型（DeepSeek）的 GitHub Pull Request 智能代码审查系统。

## 项目简介

本项目是一个自动化的代码审查工具，集成 GitHub Webhook，当仓库中创建或更新 Pull Request 时，自动获取代码变更（diff），调用大语言模型从 **Bug风险、代码规范、性能问题、安全漏洞、改进建议** 五个维度进行评审，并将结果以 Review（可批准/请求修改）或普通评论的形式发布回 PR 页面。

## 功能展示

| 审查维度 | 示例输出 |
|---------|----------|
| Bug风险 | 无逻辑错误，但变量命名不规范可能导致误解 |
| 代码规范 | 缺少类型注解，建议添加 |
| 性能问题 | 循环内重复调用 API，建议缓存结果 |
| 安全问题 | **严重**：硬编码密码泄露风险 |
| 改进建议 | 使用环境变量或密钥管理服务 |

## 技术栈

- Python 3.13+
- FastAPI + Uvicorn
- GitHub API
- DeepSeek API
- ngrok
- python-dotenv

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/LINGZELL/ai-code-reviewer.git
cd ai-code-reviewer