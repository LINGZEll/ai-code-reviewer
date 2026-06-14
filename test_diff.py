from diff_utils import get_pr_diff

diff = get_pr_diff("octocat", "Hello-World", 1)
print(diff[:500])  # 打印前500字符