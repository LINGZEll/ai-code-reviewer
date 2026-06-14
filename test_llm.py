from llm import review_code

diff = """
+ password = "123456"
+ print(password)
"""

result = review_code(diff)

print(result)