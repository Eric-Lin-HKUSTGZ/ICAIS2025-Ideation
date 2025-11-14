import os
import time
from config import Config
from llm_client import LLMClient
from retriever import PaperRetriever
from idea_generator import IdeaGenerator


def load_env_file(env_file: str):
    """加载环境变量文件"""
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ 已加载环境配置文件: {env_file}")
    else:
        print(f"⚠️  环境配置文件不存在: {env_file}")


def main():
    """主程序入口"""
    start_time = time.time()
    
    # 加载.env配置文件
    env_file = ".env"
    load_env_file(env_file)
    
    # 打印配置信息
    Config.print_config()
    
    # 验证配置
    if not Config.validate_config():
        print("❌ 配置验证失败，请检查环境变量设置")
        return
    
    # 创建LLM客户端
    try:
        client = LLMClient()
        print("✅ LLM客户端初始化成功")
    except Exception as e:
        print(f"❌ LLM客户端初始化失败: {e}")
        return
    
    # 创建论文检索器
    try:
        retriever = PaperRetriever()
        print("✅ 论文检索器初始化成功")
    except Exception as e:
        print(f"❌ 论文检索器初始化失败: {e}")
        return
    
    # 用户查询
    user_query = "Light-weight model backbone design for remote sensing image scene classification and detection."
    # user_query = "I want to do a research on remote sensing image scene classification."
    print(f"\n📝 用户查询: {user_query}")
    
    # 检测用户输入的语言
    language = IdeaGenerator.detect_language(user_query)
    print(f"🌐 检测到语言: {'中文' if language == 'zh' else 'English'}")
    
    # 创建Idea生成器（传入语言设置）
    generator = IdeaGenerator(client, language=language)
    
    try:
        # 步骤1: 提取关键词
        print("\n🔍 步骤1: 提取关键词...")
        step_start = time.time()
        keywords = generator.extract_keywords(user_query)
        print(f"提取到的关键词: {keywords}")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤2: 扩展背景
        print("\n📖 步骤2: 扩展背景...")
        step_start = time.time()
        expanded_background = generator.expand_background(user_query, keywords)
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤3: 混合检索论文
        print("\n📚 步骤3: 混合检索论文...")
        step_start = time.time()
        papers = retriever.hybrid_retrieve(expanded_background, keywords)
        print(f"检索到 {len(papers)} 篇论文")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        if not papers:
            print("❌ 未检索到相关论文，程序终止")
            return
        
        # 步骤4: Brainstorm生成（默认开启）
        print("\n💡 步骤4: 生成Brainstorm...")
        step_start = time.time()
        brainstorm = generator.generate_brainstorm(expanded_background)
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤5: 多源Inspiration生成
        print("\n✨ 步骤5: 生成多源Inspiration...")
        step_start = time.time()
        inspirations = generator.generate_multi_inspirations(
            expanded_background, user_query, papers
        )
        print(f"生成了 {len(inspirations['paper_inspirations'])} 个论文Inspiration和1个全局Inspiration")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤6: 生成多个Idea
        print("\n🎯 步骤6: 生成多个Idea...")
        step_start = time.time()
        initial_ideas = generator.generate_ideas(
            expanded_background, inspirations, brainstorm, user_query
        )
        print(f"生成了 {len(initial_ideas)} 个Idea")
        print(f"初始Idea: {initial_ideas}")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        if not initial_ideas:
            print("❌ 未生成任何Idea，程序终止")
            return
        
        # 步骤7: 迭代优化Idea
        print("\n🔧 步骤7: 迭代优化Idea...")
        step_start = time.time()
        refined_ideas = generator.iterative_refine_ideas(
            expanded_background, papers, initial_ideas
        )
        print(f"优化了 {len(refined_ideas)} 个Idea")
        print(f"优化后的Idea: {refined_ideas}")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤8: Idea评估与筛选
        print("\n📊 步骤8: 评估与筛选最优Idea...")
        step_start = time.time()
        best_idea, score = generator.evaluate_and_select_best_idea(
            expanded_background, refined_ideas
        )
        print("\n" + "-" * 80)
        print("📌 最优Idea:")
        print("-" * 80)
        print(best_idea)
        print("\n" + "-" * 80)
        print(f"最优Idea得分: 可行性={score['feasibility']:.2f}, 创新性={score['novelty']:.2f}, 总分={score['total']:.2f}")
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 步骤9: 生成研究计划
        print("\n📋 步骤9: 生成研究计划...")
        step_start = time.time()
        research_plan = generator.generate_research_plan(
            user_query, papers, best_idea, inspirations["global_inspiration"]
        )
        print(f"⏱️  耗时: {time.time() - step_start:.2f}秒")
        
        # 输出最终结果
        total_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("🎉 最终结果")
        print("=" * 80)
        print(f"\n⏱️  总耗时: {total_time:.2f}秒 ({total_time/60:.2f}分钟)")
        
        
        print("\n" + "-" * 80)
        print("📄 研究计划:")
        print("-" * 80)
        print(research_plan)
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

