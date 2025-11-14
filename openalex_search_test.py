"""
search_papers 函数:
目的: 核心搜索函数，负责构建请求、处理分页、捕获错误。
参数:
query: 用于搜索的关键字。
sort: 结果的排序方式。"relevance" 是默认的，但 OpenAlex API 也支持如 "cited_by_count:desc" (按引用数降序), "publication_date:desc" (按发表日期降序) 等。
max_results: 你希望获取的论文总数上限。
per_page: 每次 API 请求返回的论文数量（最大 200）。
filters: 一个字典，用于添加更精确的筛选条件，例如年份、是否包含摘要等。
headers: HTTP 请求头，用于设置 User-Agent。
分页: 通过 page 参数循环请求，直到获取到足够数量的论文或 API 没有返回更多结果。
错误处理: 使用 try...except 捕获 HTTPError (如 400, 429), RequestException (网络错误) 和 JSONDecodeError (响应非 JSON 格式)。
返回: 返回一个包含原始 OpenAlex 数据的字典列表。
extract_paper_info 函数:
目的: 将 OpenAlex API 返回的复杂字典结构，解析成一个更易读、包含关键信息的字典。
处理摘要: OpenAlex 的摘要通常以 abstract_inverted_index 的形式提供，这个函数将其转换回可读的字符串。
处理作者/来源/主题: 从嵌套的字典和列表中提取关键字段。
返回: 返回一个包含 paper_id, title, abstract, citation_count 等字段的字典
"""
import requests
import time
import json
from typing import List, Dict, Optional

# --- 配置 ---
# 可选：如果你有 OpenAlex 的推荐邮箱，可以设置在 User-Agent 中
# 这有助于 OpenAlex 了解 API 的使用情况
DEFAULT_HEADERS = {
    'User-Agent': 'YourAppName/1.0 (your-email@example.com)' # 请替换为你的应用信息
}
# API 基础 URL
BASE_URL = "https://api.openalex.org"
# 请求超时时间（秒）
TIMEOUT = 30
# 每次请求之间的最小延迟（秒），避免过于频繁请求
MIN_DELAY = 1.0

# --- 核心函数 ---

def search_papers(
    query: str,
    sort: str = "relevance", # 排序方式: "relevance", "cited_by_count:desc", "publication_date:desc" 等
    max_results: int = 10,   # 最大返回结果数
    per_page: int = 25,      # 每页返回数量 (1-200)
    filters: Optional[Dict[str, str]] = None, # 可选的过滤条件
    headers: Optional[Dict] = None # 可选的请求头
) -> List[Dict]:
    """
    根据查询条件搜索论文。

    Args:
        query (str): 搜索关键词。
        sort (str, optional): 排序方式。Defaults to "relevance".
        max_results (int, optional): 想要获取的最大结果数。 Defaults to 10.
        per_page (int, optional): 每页请求的数量。 Defaults to 25.
        filters (Optional[Dict[str, str]], optional): 过滤条件字典，例如 {"publication_year": "2024"}。
        headers (Optional[Dict], optional): 请求头。 Defaults to DEFAULT_HEADERS.

    Returns:
        List[Dict]: 论文信息列表。
    """
    if headers is None:
        headers = DEFAULT_HEADERS
    if filters is None:
        filters = {}

    papers = []
    page = 1
    max_pages_needed = -(-max_results // per_page) # 向上取整计算所需页数

    # 构建基础参数
    params = {
        "search": query,
        "sort": sort,
        "per_page": min(per_page, 200), # 确保 per_page 不超过 200
    }

    # 添加过滤器
    if filters:
        # OpenAlex 使用逗号分隔的字符串来表示多个过滤值
        filter_str = ",".join([f"{k}:{v}" for k, v in filters.items()])
        params["filter"] = filter_str

    while len(papers) < max_results:
        params["page"] = page
        print(f"正在获取第 {page} 页数据...")

        try:
            response = requests.get(f"{BASE_URL}/works", params=params, headers=headers, timeout=TIMEOUT)
            response.raise_for_status() # 检查 HTTP 错误

            data = response.json()
            page_results = data.get('results', [])

            if not page_results:
                print("到达结果末尾，没有更多数据。")
                break # 没有更多结果了

            # 添加当前页的结果到总列表
            papers.extend(page_results)

            # 检查是否已达到所需数量或最后一页
            if len(papers) >= max_results or page >= max_pages_needed:
                break

            # 检查 API 返回的元数据以了解总页数（可选，用于更精确的控制）
            meta = data.get('meta', {})
            total_results = meta.get('count', 0)
            total_pages = meta.get('total_pages', 0)
            print(f"  - 本页获取 {len(page_results)} 条结果。")
            print(f"  - 总计已获取 {len(papers)} 条结果 (目标: {max_results})。")
            print(f"  - API 报告总结果数: {total_results}, 总页数: {total_pages}")

            page += 1
            time.sleep(MIN_DELAY) # 避免请求过于频繁

        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e}")
            print(f"响应内容: {e.response.text}")
            if e.response.status_code == 400: # Bad Request
                print("错误可能是由于查询参数格式不正确导致的。")
            elif e.response.status_code == 429: # Too Many Requests
                print("请求过于频繁，被限流。等待更长时间再试。")
                time.sleep(10) # 被限流时等待更久
            break # 遇到 HTTP 错误，停止请求
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            break # 遇到其他请求错误，停止请求
        except json.JSONDecodeError as e:
            print(f"响应JSON解析错误: {e}")
            print(f"响应内容: {response.text[:200]}...") # 打印部分响应内容
            break # 遇到 JSON 解析错误，停止请求

    # 截取到目标数量
    return papers[:max_results]


def extract_paper_info(paper: Dict) -> Dict:
    """
    从 OpenAlex 返回的单个论文数据中提取关键信息。

    Args:
        paper (Dict): OpenAlex API 返回的单个论文字典。

    Returns:
        Dict: 提取后的论文信息字典。
    """
    # OpenAlex ID
    paper_id = paper.get('id', 'N/A')
    if paper_id != 'N/A':
        # 提取 ID 的后缀部分
        paper_id = paper_id.split('/')[-1]

    # 标题
    title = paper.get('title', 'N/A')

    # 摘要 (处理 abstract_inverted_index 格式)
    abstract = "N/A"
    if 'abstract_inverted_index' in paper and paper['abstract_inverted_index']:
        try:
            inverted_idx = paper['abstract_inverted_index']
            # 创建位置到单词的映射
            pos_to_word = {}
            for word, positions in inverted_idx.items():
                for pos in positions:
                    pos_to_word[pos] = word
            # 按位置排序并拼接
            if pos_to_word:
                sorted_positions = sorted(pos_to_word.keys())
                abstract = ' '.join([pos_to_word[pos] for pos in sorted_positions])
        except Exception as e:
            print(f"  - 提取摘要时出错: {e}")

    # 引用数
    citation_count = paper.get('cited_by_count', 0)

    # 发表日期
    publication_date = paper.get('publication_date', 'N/A')

    # 作者列表 (提取前几位)
    authors = []
    if 'authorships' in paper:
        for author_info in paper['authorships']:
            raw_name = author_info.get('author', {}).get('display_name', 'N/A')
            authors.append(raw_name)
            # 例如，只取前3位作者
            if len(authors) >= 3:
                break

    # 期刊/来源
    primary_location = paper.get('primary_location', {})
    source_info = primary_location.get('source', {})
    venue_name = source_info.get('display_name', 'N/A')
    venue_type = source_info.get('type', 'N/A')

    # 主题
    concepts = []
    if 'concepts' in paper:
        for concept in paper['concepts']:
            if concept.get('score', 0) > 0.5: # 例如，只取置信度大于0.5的主题
                concepts.append(concept.get('display_name', 'N/A'))

    return {
        "paper_id": paper_id,
        "title": title,
        "abstract": abstract,
        "citation_count": citation_count,
        "publication_date": publication_date,
        "authors": authors,
        "venue_name": venue_name,
        "venue_type": venue_type,
        "concepts": concepts
    }


# --- 主流程示例 ---
if __name__ == "__main__":
    # 定义查询参数
    search_query = "large language models"
    sort_by = "cited_by_count:desc" # 按引用数降序
    max_papers = 5
    filters_example = {"publication_year": "2024", "has_abstract": "true"} # 2024年且有摘要

    print(f"开始搜索论文: '{search_query}'")
    print(f"排序方式: {sort_by}")
    print(f"最大结果数: {max_papers}")
    print(f"过滤条件: {filters_example}")
    print("-" * 50)

    # 执行搜索
    raw_results = search_papers(
        query=search_query,
        sort=sort_by,
        max_results=max_papers,
        filters=filters_example
    )

    print(f"\n搜索完成，共获取到 {len(raw_results)} 篇论文。")
    print("-" * 50)

    # 解析和打印结果
    for i, raw_paper in enumerate(raw_results, 1):
        print(f"\n--- 论文 {i} ---")
        paper_info = extract_paper_info(raw_paper)
        print(f"ID: {paper_info['paper_id']}")
        print(f"标题: {paper_info['title']}")
        print(f"作者: {', '.join(paper_info['authors'])}")
        print(f"发表日期: {paper_info['publication_date']}")
        print(f"期刊/来源: {paper_info['venue_name']} ({paper_info['venue_type']})")
        print(f"引用数: {paper_info['citation_count']}")
        print(f"主题: {', '.join(paper_info['concepts'])}")
        # 摘要可能很长，这里只打印前100个字符
        abstract_preview = paper_info['abstract'][:100] + "..." if len(paper_info['abstract']) > 100 else paper_info['abstract']
        print(f"摘要 (预览): {abstract_preview}")
        print("-" * 20)

    print("\nPipeline 执行完毕。")