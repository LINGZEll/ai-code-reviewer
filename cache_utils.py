import hashlib
import json
import os

CACHE_FILE = "review_cache.json"

def load_cache():
    """从JSON文件加载缓存字典"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_cache(cache):
    """保存缓存字典到JSON文件"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def get_diff_hash(diff_text: str) -> str:
    """计算diff的SHA256哈希值作为缓存键"""
    return hashlib.sha256(diff_text.encode('utf-8')).hexdigest()

def get_cached_review(diff_text: str):
    """如果存在缓存，返回审查结果；否则返回None"""
    cache = load_cache()
    h = get_diff_hash(diff_text)
    return cache.get(h)

def save_review_cache(diff_text: str, review_result: str):
    """保存审查结果到缓存"""
    cache = load_cache()
    h = get_diff_hash(diff_text)
    cache[h] = review_result
    save_cache(cache)