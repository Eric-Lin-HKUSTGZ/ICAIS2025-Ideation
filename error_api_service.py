import os
import json
import time
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import Config
from llm_client import LLMClient
from retriever import PaperRetriever
from idea_generator import IdeaGenerator


def load_env_file(env_file: str):
    """加载环境变量文件"""
    # 如果路径不是绝对路径，则基于当前文件所在目录查找
    if not os.path.isabs(env_file):
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(current_dir, env_file)
    
    if os.path.exists(env_file):
        print(f"✓ 找到 .env 文件: {env_file}")
        loaded_count = 0
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    loaded_count += 1
        print(f"✓ 成功加载 {loaded_count} 个环境变量")
    else:
        print(f"⚠️  警告: 未找到 .env 文件: {env_file}")


# 加载环境变量（使用基于当前文件所在目录的路径）
try:
    load_env_file(".env")
except Exception as e:
    print(f"⚠️  加载 .env 文件时出错: {e}")

app = FastAPI(title="ICAIS2025-Ideation API", version="1.0.0")

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"📥 收到请求: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        print(f"📤 发送响应: {request.method} {request.url.path} - {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ 请求处理错误: {e}")
        raise

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IdeationRequest(BaseModel):
    query: str


def format_sse_data(data: dict) -> str:
    """生成SSE格式的数据"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def generate_ideation_stream(query: str) -> AsyncGenerator[str, None]:
    """生成Idea的流式输出生成器"""
    start_time = time.time()
    
    try:
        # 发送开始信息
        yield format_sse_data({
            "type": "start",
            "message": "# 开始生成研究Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 验证配置
        await asyncio.sleep(0)  # 让出控制权
        try:
            config_valid = Config.validate_config()
            if not config_valid:
                yield format_sse_data({
                    "type": "error",
                    "message": "## 错误\n\n配置验证失败，请检查环境变量设置\n\n"
                })
                return
        except Exception as e:
            yield format_sse_data({
                "type": "error",
                "message": f"## 错误\n\n配置验证异常: {e}\n\n"
            })
            return
        
        # 创建LLM客户端
        try:
            client = await asyncio.to_thread(LLMClient)
            await asyncio.sleep(0)  # 让出控制权
            yield format_sse_data({
                "type": "info",
                "message": "LLM客户端初始化成功\n\n"
            })
            await asyncio.sleep(0)  # 让出控制权
        except Exception as e:
            yield format_sse_data({
                "type": "error",
                "message": f"## 错误\n\nLLM客户端初始化失败: {e}\n\n"
            })
            return
        
        # 创建论文检索器
        try:
            retriever = await asyncio.to_thread(PaperRetriever)
            await asyncio.sleep(0)  # 让出控制权
            yield format_sse_data({
                "type": "info",
                "message": "论文检索器初始化成功\n\n"
            })
            await asyncio.sleep(0)  # 让出控制权
        except Exception as e:
            yield format_sse_data({
                "type": "error",
                "message": f"## 错误\n\n论文检索器初始化失败: {e}\n\n"
            })
            return
        
        # 检测用户输入的语言
        language = await asyncio.to_thread(IdeaGenerator.detect_language, query)
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "info",
            "message": f"检测到语言: **{'中文' if language == 'zh' else 'English'}**\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 创建Idea生成器
        generator = IdeaGenerator(client, language=language)
        
        # 步骤1: 提取关键词
        yield format_sse_data({
            "type": "step",
            "step": 1,
            "message": "## 步骤1: 提取关键词\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权，确保流式输出
        step_start = time.time()
        keywords = await asyncio.to_thread(generator.extract_keywords, query)
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 1,
            "message": f"**提取到的关键词**: {', '.join(keywords)}\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤2: 扩展背景
        yield format_sse_data({
            "type": "step",
            "step": 2,
            "message": "## 步骤2: 扩展背景\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        expanded_background = await asyncio.to_thread(generator.expand_background, query, keywords)
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 2,
            "message": "背景扩展完成\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤3: 混合检索论文
        yield format_sse_data({
            "type": "step",
            "step": 3,
            "message": "## 步骤3: 混合检索论文\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        papers = await asyncio.to_thread(retriever.hybrid_retrieve, expanded_background, keywords)
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 3,
            "message": f"检索到 **{len(papers)}** 篇论文\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        if not papers:
            yield format_sse_data({
                "type": "error",
                "message": "## 错误\n\n未检索到相关论文，程序终止\n\n"
            })
            return
        
        # 步骤4: Brainstorm生成
        yield format_sse_data({
            "type": "step",
            "step": 4,
            "message": "## 步骤4: 生成Brainstorm\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        brainstorm = await asyncio.to_thread(generator.generate_brainstorm, expanded_background)
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 4,
            "message": "Brainstorm生成完成\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤5: 多源Inspiration生成
        yield format_sse_data({
            "type": "step",
            "step": 5,
            "message": "## 步骤5: 生成多源Inspiration\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        inspirations = await asyncio.to_thread(
            generator.generate_multi_inspirations,
            expanded_background, query, papers
        )
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 5,
            "message": f"生成了 **{len(inspirations['paper_inspirations'])}** 个论文Inspiration和**1**个全局Inspiration\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤6: 生成多个Idea
        yield format_sse_data({
            "type": "step",
            "step": 6,
            "message": "## 步骤6: 生成多个Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        initial_ideas = await asyncio.to_thread(
            generator.generate_ideas,
            expanded_background, inspirations, brainstorm, query
        )
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 6,
            "message": f"生成了 **{len(initial_ideas)}** 个Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        if not initial_ideas:
            yield format_sse_data({
                "type": "error",
                "message": "## 错误\n\n未生成任何Idea，程序终止\n\n"
            })
            return
        
        # 步骤7: 迭代优化Idea
        yield format_sse_data({
            "type": "step",
            "step": 7,
            "message": "## 步骤7: 迭代优化Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        refined_ideas = await asyncio.to_thread(
            generator.iterative_refine_ideas,
            expanded_background, papers, initial_ideas
        )
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 7,
            "message": f"优化了 **{len(refined_ideas)}** 个Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤8: Idea评估与筛选
        yield format_sse_data({
            "type": "step",
            "step": 8,
            "message": "## 步骤8: 评估与筛选最优Idea\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        best_idea, score = await asyncio.to_thread(
            generator.evaluate_and_select_best_idea,
            expanded_background, refined_ideas
        )
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        
        # 清理best_idea格式
        best_idea_clean = best_idea.strip()
        best_idea_clean = best_idea_clean.replace('**', '')
        
        yield format_sse_data({
            "type": "step_result",
            "step": 8,
            "message": f"### 最优Idea\n\n{best_idea_clean}\n\n**得分**:\n- 可行性: {score['feasibility']:.2f}/5\n- 创新性: {score['novelty']:.2f}/5\n- 总分: {score['total']:.2f}/10\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 步骤9: 生成研究计划
        yield format_sse_data({
            "type": "step",
            "step": 9,
            "message": "## 步骤9: 生成研究计划\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        step_start = time.time()
        research_plan = await asyncio.to_thread(
            generator.generate_research_plan,
            query, papers, best_idea, inspirations["global_inspiration"]
        )
        step_time = time.time() - step_start
        await asyncio.sleep(0)  # 让出控制权
        yield format_sse_data({
            "type": "step_result",
            "step": 9,
            "message": "研究计划生成完成\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 输出最终结果（只输出研究计划，不包含无关信息）
        yield format_sse_data({
            "type": "final",
            "message": f"{research_plan}\n\n"
        })
        await asyncio.sleep(0)  # 让出控制权
        
        # 发送完成信号
        # yield format_sse_data({
        #     "type": "done",
        #     "message": "所有步骤完成",
        #     "markdown": ""
        # })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        yield format_sse_data({
            "type": "error",
            "message": f"## 错误\n\n程序执行失败: {e}\n\n```\n{error_trace}\n```\n\n"
        })


@app.post("/ideation")
async def ideation(request: IdeationRequest):
    """
    Idea生成API端点
    
    接收JSON格式的查询，返回SSE流式输出（Markdown格式）
    
    Request Body:
    {
        "query": "Please help me come up with an innovative idea for spatiotemporal data prediction using LLM technology."
    }
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        return EventSourceResponse(
            generate_ideation_stream(request.query),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ API端点错误: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health():
    """健康检查端点"""
    print("✓ Health check endpoint called")  # 调试日志
    return {"status": "ok", "service": "ICAIS2025-Ideation API"}


@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "ICAIS2025-Ideation API",
        "version": "1.0.0",
        "endpoints": {
            "POST /ideation": "生成研究Idea（SSE流式输出）",
            "GET /health": "健康检查",
            "GET /docs": "API文档"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 FastAPI 服务...")
    print(f"📍 监听地址: 0.0.0.0:3000")
    print(f"📝 访问地址: http://localhost:3000")
    print(f"📚 API 文档: http://localhost:3000/docs")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        log_level="info",
        access_log=True
    )