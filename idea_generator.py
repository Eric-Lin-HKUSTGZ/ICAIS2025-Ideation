import re
import time
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from llm_client import LLMClient
from prompt_template import get_prompt
from config import Config


class IdeaGenerator:
    """Idea生成器 - 包含所有idea生成、优化、评估功能"""

    def __init__(self, llm_client: LLMClient, language: str = 'en'):
        self.llm_client = llm_client
        self.config = Config
        self.language = language  # 'zh' for Chinese, 'en' for English
    
    @staticmethod
    def detect_language(text: str) -> str:
        """检测文本语言，返回'zh'（中文）或'en'（英文）"""
        if not text:
            return 'en'
        
        # 统计中文字符数量
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 统计总字符数量（排除空格和标点）
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
        
        if total_chars == 0:
            return 'en'
        
        # 如果中文字符占比超过30%，认为是中文
        if chinese_chars / total_chars > 0.3:
            return 'zh'
        else:
            return 'en'

    def extract_keywords(self, user_query: str) -> List[str]:
        """提取关键词"""
        prompt = get_prompt("retrieve_query", language=self.language, user_query=user_query)
        response = self.llm_client.get_response(prompt=prompt)
        
        query_list = [kw.strip() for kw in response.split(",")]
        return query_list

    def expand_background(self, brief_background: str, keywords: List[str]) -> str:
        """扩展背景"""
        keywords_str = ", ".join(keywords)
        prompt = get_prompt("expand_background", language=self.language, brief_background=brief_background, keywords=keywords_str)
        expanded = self.llm_client.get_response(prompt=prompt)
        return expanded

    def generate_brainstorm(self, background: str) -> str:
        """生成Brainstorm - 默认开启"""
        prompt = get_prompt("generate_brainstorm", language=self.language, background=background)
        brainstorm = self.llm_client.get_response(prompt=prompt)
        return brainstorm

    def generate_paper_inspiration(self, background: str, paper: Dict) -> Optional[str]:
        """为单篇论文生成Inspiration"""
        try:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '') or ''
            
            prompt = get_prompt(
                "generate_paper_inspiration",
                language=self.language,
                background=background,
                title=title,
                abstract=abstract
            )
            inspiration = self.llm_client.get_response(prompt=prompt)
            return inspiration
        except Exception as e:
            print(f"⚠️  生成论文Inspiration失败: {e}")
            return None

    def generate_global_inspiration(self, user_query: str, papers: List[Dict]) -> str:
        """生成全局Inspiration"""
        # 构造论文信息文本
        paper_text = ""
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', '')
            abstract = paper.get('abstract', '') or ''
            paper_text += f"Paper {i}:\nTitle: {title}\nAbstract: {abstract}\n\n"
        
        prompt = get_prompt("generate_global_inspiration", language=self.language, user_query=user_query, paper=paper_text)
        inspiration = self.llm_client.get_response(prompt=prompt)
        return inspiration

    def generate_multi_inspirations(self, background: str, user_query: str, papers: List[Dict]) -> Dict:
        """多源Inspiration生成 - 并行处理，只对top-8论文生成"""
        paper_inspirations = []
        
        # 只对前8篇论文生成Inspiration（论文已经按相关性排序）
        papers_to_process = papers[:8]
        
        # 1. 为每篇论文生成Inspiration（并行）
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS_INSPIRATION) as executor:
            futures = []
            for paper in papers_to_process:
                future = executor.submit(
                    self.generate_paper_inspiration,
                    background, paper
                )
                futures.append((future, paper))
            
            for future, paper in futures:
                try:
                    inspiration = future.result(timeout=self.config.INSPIRATION_TIMEOUT)
                    if inspiration:
                        paper_inspirations.append(inspiration)
                except Exception as e:
                    print(f"⚠️  论文Inspiration生成超时或失败: {e}")
        
        # 2. 生成全局Inspiration
        global_inspiration = self.generate_global_inspiration(user_query, papers)
        
        return {
            "paper_inspirations": paper_inspirations,
            "global_inspiration": global_inspiration
        }

    def extract_ideas(self, idea_str: str) -> List[str]:
        """从格式化的idea文本中提取idea列表"""
        if not idea_str or not isinstance(idea_str, str):
            return []
        
        ideas = []
        
        # 尝试多种正则表达式模式
        patterns = [
            # 模式1: **Idea 1**: 或 **Idea 1:**
            r'\*\*Idea\s+(\d+)\*\*:?\s*(.*?)(?=\*\*Idea\s+\d+\*\*:|$)',
            # 模式2: Idea 1: 或 Idea 1.
            r'(?:^|\n)\s*\*\*?Idea\s+(\d+)\*\*?:?\s*(.*?)(?=(?:^|\n)\s*\*\*?Idea\s+\d+\*\*?:?|$)',
            # 模式3: 更宽松的匹配
            r'Idea\s+(\d+)[:\.]\s*(.*?)(?=Idea\s+\d+[:\.]|$)',
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, idea_str, re.DOTALL | re.MULTILINE))
            if matches:
                for match in matches:
                    idea_num = match.group(1)
                    idea_text = match.group(2).strip()
                    if idea_text and len(idea_text) > 20:  # 确保idea内容足够长
                        # 清理idea文本，移除开头可能的多余内容
                        idea_text = re.sub(r'^[^\w]*', '', idea_text)  # 移除开头的非字母数字字符
                        ideas.append(f"**Idea {idea_num}**: {idea_text}")
                break  # 找到匹配就停止
        
        # 如果仍然没有找到，尝试按段落分割（查找明显的分隔符）
        if not ideas:
            # 查找所有"Idea X"的位置
            idea_markers = list(re.finditer(r'\*\*?Idea\s+\d+\*\*?:?', idea_str, re.IGNORECASE))
            if len(idea_markers) > 1:
                for i, marker in enumerate(idea_markers):
                    start = marker.start()
                    end = idea_markers[i + 1].start() if i + 1 < len(idea_markers) else len(idea_str)
                    idea_text = idea_str[start:end].strip()
                    if idea_text:
                        ideas.append(idea_text)
        
        # 如果还是没有找到格式化的idea，返回整个文本
        if not ideas:
            ideas = [idea_str]
        
        # 调试日志
        if len(ideas) > 1:
            print(f"✅ 成功提取 {len(ideas)} 个Idea")
        elif len(ideas) == 1 and 'Idea' in ideas[0] and ('Idea 1' in ideas[0] or 'Idea 2' in ideas[0]):
            # 如果只有一个idea但包含多个idea标记，尝试进一步分割
            print(f"⚠️  检测到单个文本包含多个Idea标记，尝试进一步分割...")
            # 使用更精确的模式重新提取
            refined_pattern = r'\*\*Idea\s+(\d+)\*\*:?\s*([^*]+?)(?=\*\*Idea\s+\d+\*\*:|$)'
            refined_matches = list(re.finditer(refined_pattern, ideas[0], re.DOTALL))
            if len(refined_matches) > 1:
                ideas = []
                for match in refined_matches:
                    idea_num = match.group(1)
                    idea_text = match.group(2).strip()
                    if idea_text:
                        ideas.append(f"**Idea {idea_num}**: {idea_text}")
                print(f"✅ 重新提取后得到 {len(ideas)} 个Idea")
        
        return ideas

    def extract_single_idea(self, idea_text: str) -> str:
        """从可能包含多个idea的文本中提取单个idea（通常是第一个）"""
        if not idea_text or not isinstance(idea_text, str):
            return idea_text
        
        # 首先尝试提取所有idea
        ideas = self.extract_ideas(idea_text)
        
        # 如果只提取到一个idea，直接返回
        if len(ideas) == 1:
            return ideas[0]
        
        # 如果提取到多个idea，返回第一个
        if len(ideas) > 1:
            print(f"⚠️  检测到文本包含 {len(ideas)} 个Idea，将使用第一个Idea")
            return ideas[0]
        
        # 如果没有提取到idea，尝试查找第一个"Idea 1"或"Idea 1:"标记
        # 提取从第一个Idea标记到第二个Idea标记之间的内容
        first_idea_pattern = r'(\*\*Idea\s+1\*\*:?\s*.*?)(?=\*\*Idea\s+2\*\*:|$)'
        match = re.search(first_idea_pattern, idea_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果都找不到，返回原始文本
        return idea_text

    def generate_ideas_from_inspirations(self, background: str, inspirations: List[str]) -> List[str]:
        """基于多源Inspiration生成Idea"""
        inspirations_text = "\n\n".join([
            f"Inspiration {i+1}:\n{insp}" for i, insp in enumerate(inspirations)
        ])
        
        prompt = get_prompt("generate_ideas_from_inspirations", language=self.language, background=background, inspirations=inspirations_text)
        response = self.llm_client.get_response(prompt=prompt)
        ideas = self.extract_ideas(response)
        return ideas[:self.config.MAX_IDEAS_GENERATE]

    def generate_idea_from_inspiration(self, background: str, inspiration: str) -> List[str]:
        """基于单个Inspiration生成Idea"""
        prompt = get_prompt("generate_idea_from_inspiration", language=self.language, background=background, inspiration=inspiration)
        response = self.llm_client.get_response(prompt=prompt)
        ideas = self.extract_ideas(response)
        return ideas[:3]  # 最多3个

    def integrate_with_brainstorm(self, background: str, brainstorm: str, ideas: List[str]) -> List[str]:
        """使用Brainstorm整合Idea - 默认开启"""
        ideas_text = "\n\n".join(ideas)
        
        prompt = get_prompt(
            "integrate_with_brainstorm",
            language=self.language,
            background=background,
            brainstorm=brainstorm,
            ideas=ideas_text
        )
        response = self.llm_client.get_response(prompt=prompt)
        integrated_ideas = self.extract_ideas(response)
        return integrated_ideas[:self.config.MAX_IDEAS_GENERATE]

    def generate_ideas(
        self,
        background: str,
        inspirations: Dict,
        brainstorm: str
    ) -> List[str]:
        """多Idea生成 - Brainstorm默认开启"""
        all_ideas = []
        
        # 1和2: 并行生成Idea（基于论文Inspiration和全局Inspiration）
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # 提交基于论文Inspiration的Idea生成任务
            if inspirations["paper_inspirations"]:
                future_papers = executor.submit(
                    self.generate_ideas_from_inspirations,
                    background,
                    inspirations["paper_inspirations"]
                )
                futures["papers"] = future_papers
            
            # 提交基于全局Inspiration的Idea生成任务
            future_global = executor.submit(
                self.generate_idea_from_inspiration,
                background,
                inspirations["global_inspiration"]
            )
            futures["global"] = future_global
            
            # 等待所有任务完成
            if "papers" in futures:
                try:
                    ideas_from_papers = futures["papers"].result(timeout=120)
                    all_ideas.extend(ideas_from_papers)
                except Exception as e:
                    print(f"⚠️  基于论文Inspiration生成Idea失败: {e}")
            
            try:
                ideas_from_global = futures["global"].result(timeout=120)
                all_ideas.extend(ideas_from_global)
            except Exception as e:
                print(f"⚠️  基于全局Inspiration生成Idea失败: {e}")
        
        # 3. 使用Brainstorm整合（默认开启）
        if self.config.ENABLE_BRAINSTORM and brainstorm:
            all_ideas = self.integrate_with_brainstorm(background, brainstorm, all_ideas)
        
        return all_ideas[:self.config.MAX_IDEAS_GENERATE]

    def critic_idea(self, background: str, papers: List[Dict], idea: str) -> str:
        """批判性审查Idea"""
        # 构造论文摘要
        papers_summary = "\n".join([
            f"- {p.get('title', '')}: {(p.get('abstract') or '')[:200]}..." 
            for p in papers[:5]  # 只取前5篇
        ])
        
        prompt = get_prompt("critic_idea", language=self.language, background=background, papers_summary=papers_summary, idea=idea)
        criticism = self.llm_client.get_response(prompt=prompt)
        
        # 检查返回值
        if not criticism or not isinstance(criticism, str):
            raise Exception(f"批判性审查返回无效结果: {criticism}")
        
        return criticism

    def refine_idea(self, background: str, idea: str, criticism: str) -> str:
        """完善Idea"""
        if not criticism:
            raise ValueError("criticism不能为空")
        
        prompt = get_prompt("refine_idea", language=self.language, background=background, idea=idea, criticism=criticism)
        refined = self.llm_client.get_response(prompt=prompt)
        
        # 检查返回值
        if not refined or not isinstance(refined, str):
            raise Exception(f"Idea完善返回无效结果: {refined}")
        
        return refined

    def refine_single_idea(self, background: str, papers: List[Dict], idea: str) -> Optional[str]:
        """优化单个Idea"""
        try:
            # 1. 批判性审查
            criticism = self.critic_idea(background, papers, idea)
            if not criticism:
                print(f"⚠️  批判性审查返回空结果，跳过优化")
                return None
            
            # 2. 完善Idea
            refined_idea = self.refine_idea(background, idea, criticism)
            if not refined_idea:
                print(f"⚠️  Idea完善返回空结果，使用原始Idea")
                return idea  # 返回原始idea而不是None
            
            return refined_idea
        except Exception as e:
            print(f"⚠️  Idea优化失败: {e}")
            import traceback
            traceback.print_exc()
            # 优化失败时返回原始idea，而不是None
            return idea

    def iterative_refine_ideas(
        self,
        background: str,
        papers: List[Dict],
        initial_ideas: List[str]
    ) -> List[str]:
        """迭代优化Idea - 只优化top-3"""
        if not initial_ideas:
            return []
        
        # 只优化前3个Idea
        ideas_to_optimize = initial_ideas[:self.config.MAX_IDEAS_OPTIMIZE]
        refined_ideas = []
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS_OPTIMIZATION) as executor:
            # 创建future到idea的映射
            future_to_idea = {}
            futures = []
            for idea in ideas_to_optimize:
                future = executor.submit(
                    self.refine_single_idea,
                    background, papers, idea
                )
                futures.append(future)
                future_to_idea[future] = idea
            
            # 计算总超时时间：每个任务的最大超时时间 + 一些缓冲
            total_timeout = self.config.OPTIMIZATION_TIMEOUT * len(ideas_to_optimize) + 60
            
            # 跟踪已处理的future
            processed_futures = set()
            
            try:
                # 使用as_completed处理已完成的任务
                for future in as_completed(futures, timeout=total_timeout):
                    processed_futures.add(future)
                    try:
                        # 每个future的结果获取不需要额外超时，因为as_completed已经等待完成
                        refined_idea = future.result()
                        if refined_idea:
                            refined_ideas.append(refined_idea)
                    except Exception as e:
                        print(f"⚠️  Idea优化失败: {e}")
                        # 使用原始idea
                        original_idea = future_to_idea.get(future)
                        if original_idea:
                            refined_ideas.append(original_idea)
            except TimeoutError:
                print(f"⚠️  Idea优化总超时（{total_timeout}秒），处理已完成的任务...")
                # 处理所有future（包括已完成和未完成的）
                for future in futures:
                    if future in processed_futures:
                        # 已经在as_completed中处理过，跳过
                        continue
                    
                    if future.done():
                        try:
                            refined_idea = future.result()
                            if refined_idea:
                                refined_ideas.append(refined_idea)
                        except Exception as e:
                            print(f"⚠️  已完成的任务处理失败: {e}")
                            original_idea = future_to_idea.get(future)
                            if original_idea:
                                refined_ideas.append(original_idea)
                    else:
                        # 未完成的任务使用原始idea
                        original_idea = future_to_idea.get(future)
                        if original_idea:
                            print(f"⚠️  任务未完成，使用原始Idea")
                            refined_ideas.append(original_idea)
        
        # 如果所有优化都失败，使用原始ideas
        if not refined_ideas:
            print(f"⚠️  所有Idea优化失败，使用原始Idea")
            refined_ideas = ideas_to_optimize.copy()
        
        # 确保refined_ideas的数量与ideas_to_optimize一致
        if len(refined_ideas) < len(ideas_to_optimize):
            # 补充缺失的原始ideas
            for i, idea in enumerate(ideas_to_optimize):
                if i >= len(refined_ideas):
                    refined_ideas.append(idea)
        
        # 其他Idea直接添加（不优化）
        refined_ideas.extend(initial_ideas[self.config.MAX_IDEAS_OPTIMIZE:])
        
        return refined_ideas

    def evaluate_idea(self, background: str, idea: str) -> Dict[str, float]:
        """评估Idea的可行性和创新性"""
        prompt = get_prompt("evaluate_idea", language=self.language, background=background, idea=idea)
        response = self.llm_client.get_response(prompt=prompt)
        
        # 解析分数
        feasibility_match = re.search(r'Feasibility:\s*(\d+(?:\.\d+)?)', response)
        novelty_match = re.search(r'Novelty:\s*(\d+(?:\.\d+)?)', response)
        
        feasibility = float(feasibility_match.group(1)) if feasibility_match else 5.0
        novelty = float(novelty_match.group(1)) if novelty_match else 5.0
        total = feasibility + novelty
        
        return {
            "feasibility": feasibility,
            "novelty": novelty,
            "total": total
        }

    def evaluate_and_select_best_idea(
        self,
        background: str,
        refined_ideas: List[str]
    ) -> Tuple[str, Dict[str, float]]:
        """评估并选择最优Idea - 并行评估"""
        scored_ideas = []
        
        # 并行评估所有ideas
        with ThreadPoolExecutor(max_workers=len(refined_ideas)) as executor:
            futures = []
            for idea in refined_ideas:
                # 先提取单个idea
                single_idea = self.extract_single_idea(idea)
                future = executor.submit(
                    self.evaluate_idea,
                    background, single_idea
                )
                futures.append((future, single_idea, idea))
            
            # 收集评估结果
            for future, single_idea, original_idea in futures:
                try:
                    score = future.result(timeout=60)  # 每个评估最多60秒
                    scored_ideas.append({
                        "idea": single_idea,
                        "original_idea": original_idea,
                        "score": score
                    })
                except Exception as e:
                    print(f"⚠️  Idea评估失败: {e}")
                    # 使用默认分数
                    scored_ideas.append({
                        "idea": single_idea,
                        "original_idea": original_idea,
                        "score": {"feasibility": 5.0, "novelty": 5.0, "total": 10.0}
                    })
        
        # 选择总分最高的Idea
        if not scored_ideas:
            raise ValueError("没有可评估的Idea")
        
        best_idea_item = max(scored_ideas, key=lambda x: x["score"]["total"])
        best_idea = best_idea_item["idea"]
        
        # 确保返回的best_idea只包含一个idea
        # 如果best_idea仍然包含多个idea标记，再次提取
        extracted_ideas = self.extract_ideas(best_idea)
        if len(extracted_ideas) > 1:
            print(f"⚠️  最优Idea仍然包含 {len(extracted_ideas)} 个Idea，将使用第一个")
            best_idea = extracted_ideas[0]
        elif len(extracted_ideas) == 1:
            best_idea = extracted_ideas[0]
        
        return best_idea, best_idea_item["score"]

    def clean_research_plan(self, research_plan: str) -> str:
        """清理研究计划中的无关语言"""
        if not research_plan or not isinstance(research_plan, str):
            return research_plan
        
        # 需要移除的无关语言模式
        patterns_to_remove = [
            # 移除开头的元语言
            r'^(Of course|Certainly|I have thoroughly revised|I have revised|Based on|According to)[^.]*\.\s*',
            r'^(Of course|Certainly|I have thoroughly revised|I have revised)[^.]*,\s*',
            # 移除常见的元语言开头
            r'^(Let me|I will|I would like to|I should|I need to)[^.]*\.\s*',
            # 移除结尾的元语言
            r'\s*(I hope|I believe|I think|I trust|I am confident)[^.]*\.\s*$',
        ]
        
        cleaned = research_plan
        
        # 移除开头的无关语言
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # 移除开头的空行和多余空格
        cleaned = cleaned.lstrip()
        
        # 如果清理后文本以"Research Background"、"1. Research Background"等开头，保留
        # 否则，尝试找到第一个实际的章节标题
        if not re.match(r'^(Research Background|1\.|#|##)', cleaned, re.IGNORECASE):
            # 查找第一个章节标题
            section_patterns = [
                r'(Research Background|Limitations of Current Work|Proposed Research Plan)',
                r'(\d+\.\s*[A-Z][^.]*:)',
                r'(#[#]?\s+[A-Z][^.]*)',
            ]
            
            for pattern in section_patterns:
                match = re.search(pattern, cleaned, re.IGNORECASE | re.MULTILINE)
                if match:
                    # 从第一个章节标题开始
                    cleaned = cleaned[match.start():]
                    break
        
        return cleaned.strip()

    def generate_research_plan_title(self, best_idea: str) -> str:
        """生成研究计划标题"""
        prompt = get_prompt("generate_research_plan_title", language=self.language, best_idea=best_idea)
        title = self.llm_client.get_response(prompt=prompt)
        # 清理标题，移除可能的引号、换行等
        title = title.strip().strip('"').strip("'").strip()
        # 如果标题包含换行，只取第一行
        if '\n' in title:
            title = title.split('\n')[0].strip()
        return title

    def construct_paper_text(self, papers: List[Dict]) -> str:
        """构造论文信息文本"""
        paper_text = ""
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', '')
            abstract = paper.get('abstract', '') or ''
            paper_text += f"Paper {i}:\nTitle: {title}\nAbstract: {abstract}\n\n"
        return paper_text

    def generate_research_plan(
        self,
        user_query: str,
        papers: List[Dict],
        best_idea: str,
        global_inspiration: str
    ) -> str:
        """生成研究计划 - 审查默认开启"""
        paper_text = self.construct_paper_text(papers)
        
        # 0和1: 并行生成标题和初步研究计划
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_title = executor.submit(self.generate_research_plan_title, best_idea)
            future_plan = executor.submit(
                self._generate_initial_research_plan,
                user_query, paper_text, global_inspiration, best_idea
            )
            
            # 等待两个任务完成
            try:
                title = future_title.result(timeout=60)
            except Exception as e:
                print(f"⚠️  标题生成失败: {e}，将使用默认标题")
                title = "Research Proposal" if self.language == 'en' else "研究计划"
            
            try:
                research_plan = future_plan.result(timeout=120)
            except Exception as e:
                print(f"⚠️  初步研究计划生成失败: {e}")
                raise
        
        # 清理初步研究计划
        research_plan = self.clean_research_plan(research_plan)
        
        # 2. 研究计划审查（默认开启）
        if self.config.ENABLE_PLAN_REVIEW:
            prompt_critic = get_prompt(
                "critic_research_plan",
                language=self.language,
                user_query=user_query,
                paper=paper_text,
                inspiration=global_inspiration,
                research_plan=research_plan
            )
            criticism = self.llm_client.get_response(prompt=prompt_critic)
            
            # 3. 完善研究计划
            prompt_refine = get_prompt(
                "refine_research_plan",
                language=self.language,
                user_query=user_query,
                research_plan=research_plan,
                criticism=criticism
            )
            final_plan = self.llm_client.get_response(prompt=prompt_refine)
            # 清理最终研究计划
            final_plan = self.clean_research_plan(final_plan)
            # 添加标题
            return f"{title}\n\n{final_plan}"
        
        # 添加标题
        return f"{title}\n\n{research_plan}"
    
    def _generate_initial_research_plan(
        self,
        user_query: str,
        paper_text: str,
        global_inspiration: str,
        best_idea: str
    ) -> str:
        """生成初步研究计划（辅助方法，用于并行调用）"""
        prompt = get_prompt(
            "generate_research_plan",
            language=self.language,
            user_query=user_query,
            paper=paper_text,
            inspiration=global_inspiration,
            best_idea=best_idea
        )
        return self.llm_client.get_response(prompt=prompt)


