import requests
import time
import numpy as np
from typing import List, Dict, Optional
from config import Config
from embedding_client import EmbeddingClient


class PaperRetriever:
    """论文检索器 - 基于Semantic Scholar API"""

    def __init__(self):
        self.config = Config
        self.embedding_client = None
        self._init_embedding_client()

    def _init_embedding_client(self):
        """初始化embedding客户端"""
        try:
            print(f"🔄 正在初始化Embedding客户端: {self.config.EMBEDDING_MODEL_NAME}...")
            self.embedding_client = EmbeddingClient()
            print(f"✅ Embedding客户端初始化成功")
        except Exception as e:
            print(f"⚠️  Embedding客户端初始化失败: {e}，将跳过语义重排序")
            self.embedding_client = None

    def get_newest_paper(self, query: str, max_results: Optional[int] = None, max_retries: Optional[int] = None) -> List[Dict]:
        """获取最新论文"""
        max_results = max_results or self.config.MAX_PAPERS_PER_QUERY
        max_retries = max_retries or self.config.SEMANTIC_SCHOLAR_MAX_RETRIES

        url = "http://api.semanticscholar.org/graph/v1/paper/search/bulk"
        params = {"query": query, "fields": "title,abstract,paperId", "sort": "publicationDate:desc"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.config.SEMANTIC_SCHOLAR_TIMEOUT)
                data = response.json()

                if 'data' in data:
                    papers = data['data'][:max_results] if data['data'] else []
                    if papers:
                        return papers
                    # 如果返回空列表，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                        print(f"获取最新论文返回空数据，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
                else:
                    # 响应中没有'data'字段，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)
                        print(f"获取最新论文响应格式异常，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                    print(f"获取最新论文超时，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取最新论文最终失败: 超时")
                    return []
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避
                    print(f"获取最新论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取最新论文最终失败: {e}")
                    return []
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    print(f"获取最新论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取最新论文最终失败: {e}")
                    return []

        return []

    def get_highly_cited_paper(self, query: str, max_results: Optional[int] = None, max_retries: Optional[int] = None) -> List[Dict]:
        """获取高引用论文"""
        max_results = max_results or self.config.MAX_PAPERS_PER_QUERY
        max_retries = max_retries or self.config.SEMANTIC_SCHOLAR_MAX_RETRIES

        url = "http://api.semanticscholar.org/graph/v1/paper/search/bulk"
        params = {"query": query, "fields": "title,abstract,paperId", "sort": "citationCount:desc"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.config.SEMANTIC_SCHOLAR_TIMEOUT)
                data = response.json()

                if 'data' in data:
                    papers = data['data'][:max_results] if data['data'] else []
                    if papers:
                        return papers
                    # 如果返回空列表，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                        print(f"获取高引用论文返回空数据，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
                else:
                    # 响应中没有'data'字段，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)
                        print(f"获取高引用论文响应格式异常，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                    print(f"获取高引用论文超时，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取高引用论文最终失败: 超时")
                    return []
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避
                    print(f"获取高引用论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取高引用论文最终失败: {e}")
                    return []
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    print(f"获取高引用论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取高引用论文最终失败: {e}")
                    return []

        return []

    def get_relevant_paper(self, query: str, max_results: Optional[int] = None, max_retries: Optional[int] = None) -> List[Dict]:
        """获取相关论文"""
        max_results = max_results or self.config.MAX_PAPERS_PER_QUERY
        max_retries = max_retries or self.config.SEMANTIC_SCHOLAR_MAX_RETRIES

        url = "http://api.semanticscholar.org/graph/v1/paper/search"
        params = {"query": query, "fields": "title,abstract,paperId"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.config.SEMANTIC_SCHOLAR_TIMEOUT)
                data = response.json()

                if 'data' in data:
                    papers = data['data'][:max_results] if data['data'] else []
                    if papers:
                        return papers
                    # 如果返回空列表，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                        print(f"获取相关论文返回空数据，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
                else:
                    # 响应中没有'data'字段，继续重试
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 5)
                        print(f"获取相关论文响应格式异常，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    continue
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避，最多5秒
                    print(f"获取相关论文超时，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取相关论文最终失败: 超时")
                    return []
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # 指数退避
                    print(f"获取相关论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取相关论文最终失败: {e}")
                    return []
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    print(f"获取相关论文失败: {e}，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取相关论文最终失败: {e}")
                    return []

        return []

    def merge_and_deduplicate(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """融合和去重论文"""
        seen_ids = set()
        all_papers = []

        for paper_list in results.values():
            for paper in paper_list:
                paper_id = paper.get('paperId') or paper.get('title', '')
                if paper_id and paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    all_papers.append(paper)

        return all_papers

    def rerank_by_similarity(self, papers: List[Dict], background_embedding: np.ndarray, background_text: str) -> List[Dict]:
        """基于语义相似度重排序论文"""
        if not self.embedding_client or len(papers) == 0:
            return papers

        try:
            # 为每篇论文计算embedding
            paper_texts = []
            for paper in papers:
                abstract = paper.get('abstract', '') or ''
                title = paper.get('title', '') or ''
                text = f"{title} {abstract}".strip()
                paper_texts.append(text if text else " ")

            # 批量计算embedding（通过API）
            paper_embeddings = self.embedding_client.encode(paper_texts, show_progress_bar=False)
            
            # 确保是2D数组
            if paper_embeddings.ndim == 1:
                paper_embeddings = paper_embeddings.reshape(1, -1)

            # 计算相似度
            similarities = []
            for paper_emb in paper_embeddings:
                similarity = np.dot(background_embedding, paper_emb) / (
                    np.linalg.norm(background_embedding) * np.linalg.norm(paper_emb) + 1e-8
                )
                similarities.append(similarity)

            # 按相似度排序
            sorted_papers = sorted(
                zip(papers, similarities),
                key=lambda x: x[1],
                reverse=True
            )

            return [paper for paper, _ in sorted_papers]

        except Exception as e:
            print(f"⚠️  语义重排序失败: {e}，返回原始顺序")
            return papers

    def hybrid_retrieve(self, expanded_background: str, keywords: List[str]) -> List[Dict]:
        """
        混合检索策略 - 仅使用Semantic Scholar API
        """
        # 构造查询字符串
        if len(keywords) == 1:
            query = keywords[0]
        else:
            query = " | ".join(f'"{item}"' for item in keywords)

        print(f"🔍 检索关键词: {query}")

        # 1. 并行检索三类论文（即使部分失败也继续）
        import concurrent.futures

        newest_papers = []
        highly_cited_papers = []
        relevant_papers = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_newest = executor.submit(self.get_newest_paper, query)
            future_highly_cited = executor.submit(self.get_highly_cited_paper, query)
            future_relevant = executor.submit(self.get_relevant_paper, query)

            # 获取结果，即使失败也继续
            try:
                newest_papers = future_newest.result(timeout=120)  # 最多等待2分钟
            except Exception as e:
                print(f"⚠️  获取最新论文失败: {e}")
                newest_papers = []

            try:
                highly_cited_papers = future_highly_cited.result(timeout=120)
            except Exception as e:
                print(f"⚠️  获取高引用论文失败: {e}")
                highly_cited_papers = []

            try:
                relevant_papers = future_relevant.result(timeout=120)
            except Exception as e:
                print(f"⚠️  获取相关论文失败: {e}")
                relevant_papers = []

        # 2. 融合和去重
        results = {
            "newest_papers": newest_papers or [],
            "highly_cited_papers": highly_cited_papers or [],
            "relevant_papers": relevant_papers or []
        }
        all_papers = self.merge_and_deduplicate(results)

        print(f"📚 检索到 {len(all_papers)} 篇论文（去重后）")

        # 如果没有检索到任何论文，返回空列表
        if not all_papers:
            print("⚠️  未检索到任何论文")
            return []

        # 3. 使用embedding客户端计算语义相似度并重排序
        if self.embedding_client:
            try:
                background_embedding = self.embedding_client.encode(expanded_background, show_progress_bar=False)
                if background_embedding is not None and len(background_embedding) > 0:
                    all_papers = self.rerank_by_similarity(all_papers, background_embedding, expanded_background)
                    print(f"✅ 语义重排序完成")
                else:
                    print(f"⚠️  Embedding生成失败，跳过语义重排序")
            except Exception as e:
                print(f"⚠️  语义重排序失败: {e}，使用原始顺序")

        # 4. 返回top-k
        return all_papers[:self.config.MAX_TOTAL_PAPERS]

