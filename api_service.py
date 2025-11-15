import os
import json
import time
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import signal
import sys

from config import Config
from llm_client import LLMClient
from retriever import PaperRetriever
from idea_generator import IdeaGenerator


def load_env_file(env_file: str):
    """加载环境变量文件"""
    if not os.path.isabs(env_file):
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
                    os.environ[key] = value.strip('"\'')  # 去除引号
                    loaded_count += 1
        print(f"✓ 成功加载 {loaded_count} 个环境变量")
        return True
    else:
        print(f"⚠️ 警告: 未找到 .env 文件: {env_file}")
        return False


# 加载环境变量
load_env_file(".env")

# 创建FastAPI应用 - 显式指定docs和redoc路径
app = FastAPI(
    title="ICAIS2025-Ideation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 移除可能导致阻塞的请求日志中间件
# 使用更简单的日志记录方式

@app.middleware("http")
async def simple_log_middleware(request, call_next):
    """简化的日志中间件，避免阻塞"""
    start_time = time.time()
    path = request.url.path
    
    # 只记录非健康检查的日志，避免日志过多
    if not path.startswith("/health"):
        print(f"📥 [{time.strftime('%H:%M:%S')}] {request.method} {path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        if not path.startswith("/health"):
            print(f"📤 [{time.strftime('%H:%M:%S')}] {request.method} {path} - {response.status_code} ({process_time:.3f}s)")
        return response
    except Exception as e:
        print(f"❌ [{time.strftime('%H:%M:%S')}] 错误: {request.method} {path} - {e}")
        raise

# 配置CORS - 明确设置origins而不是*
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 设置全局超时
REQUEST_TIMEOUT = 600  # 10分钟超时


class IdeationRequest(BaseModel):
    query: str


def format_sse_data(content: str) -> str:
    """生成OpenAI格式的SSE数据"""
    data = {
        "object": "chat.completion.chunk",
        "choices": [{
            "delta": {
                "content": content
            }
        }]
    }
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def format_sse_done() -> str:
    """生成SSE结束标记"""
    return "data: [DONE]\n\n"

def stream_message(message: str, chunk_size: int = 1):
    """将消息按字符流式输出（同步生成器）"""
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        yield format_sse_data(chunk)


async def _generate_ideation_internal(query: str) -> AsyncGenerator[str, None]:
    """内部生成器函数，执行实际的生成逻辑"""
    # 验证配置（不输出）
    try:
        config_valid = await asyncio.to_thread(Config.validate_config)
        if not config_valid:
            for chunk in stream_message("## ❌ 错误\n\n配置验证失败，请检查环境变量设置\n\n"):
                yield chunk
            return
    except Exception as e:
        for chunk in stream_message(f"## ❌ 错误\n\n配置验证异常: {e}\n\n"):
            yield chunk
        return
    
    # 创建组件（不输出初始化信息）
    try:
        client = LLMClient()
    except Exception as e:
        for chunk in stream_message(f"## ❌ 错误\n\nLLM客户端初始化失败: {e}\n\n"):
            yield chunk
        return
    
    try:
        retriever = PaperRetriever()
    except Exception as e:
        for chunk in stream_message(f"## ❌ 错误\n\n论文检索器初始化失败: {e}\n\n"):
            yield chunk
        return
    
    # 检测语言（不输出）
    language = await asyncio.to_thread(IdeaGenerator.detect_language, query)
    generator = IdeaGenerator(client, language=language)
    
    # 步骤1: 提取关键词（简化输出）
    keywords = await asyncio.to_thread(generator.extract_keywords, query)
    for chunk in stream_message("### 📝 步骤 1/9: 关键词提取\n\n✅ 已完成\n\n"):
        yield chunk
    
    # 步骤2: 扩展背景（简化输出）
    expanded_background = await asyncio.to_thread(generator.expand_background, query, keywords)
    for chunk in stream_message("### 🔍 步骤 2/9: 背景扩展\n\n✅ 已完成\n\n"):
        yield chunk
    
    # 步骤3: 混合检索论文（简化输出）
    papers = await asyncio.to_thread(retriever.hybrid_retrieve, expanded_background, keywords)
    for chunk in stream_message(f"### 📚 步骤 3/9: 论文检索\n\n✅ 已检索到 {len(papers)} 篇相关论文\n\n"):
        yield chunk
    
    if not papers:
        for chunk in stream_message("## ❌ 错误\n\n未检索到相关论文，程序终止\n\n"):
            yield chunk
        return
    
    # 步骤4: Brainstorm（简化输出）
    brainstorm = await asyncio.to_thread(generator.generate_brainstorm, expanded_background)
    for chunk in stream_message("### 💡 步骤 4/9: 头脑风暴\n\n✅ 已完成\n\n"):
        yield chunk
    
    # 步骤5: 多源Inspiration（简化输出）
    inspirations = await asyncio.to_thread(
        generator.generate_multi_inspirations,
        expanded_background, query, papers
    )
    for chunk in stream_message("### ✨ 步骤 5/9: 多源灵感生成\n\n✅ 已完成\n\n"):
        yield chunk
    
    # 步骤6: 生成Idea（简化输出）
    initial_ideas = await asyncio.to_thread(
        generator.generate_ideas,
        expanded_background, inspirations, brainstorm, query
    )
    for chunk in stream_message(f"### 🎯 步骤 6/9: 初始Idea生成\n\n✅ 已生成 {len(initial_ideas)} 个初始Idea\n\n"):
        yield chunk
    
    if not initial_ideas:
        for chunk in stream_message("## ❌ 错误\n\n未生成任何Idea，程序终止\n\n"):
            yield chunk
        return
    
    # 步骤7: 迭代优化（简化输出）
    refined_ideas = await asyncio.to_thread(
        generator.iterative_refine_ideas,
        expanded_background, papers, initial_ideas
    )
    for chunk in stream_message(f"### 🔧 步骤 7/9: Idea优化\n\n✅ 已优化 {len(refined_ideas)} 个Idea\n\n"):
        yield chunk
    
    # 步骤8: 评估筛选（保留关键信息，但简化格式）
    best_idea, score = await asyncio.to_thread(
        generator.evaluate_and_select_best_idea,
        expanded_background, refined_ideas
    )
    
    best_idea_clean = best_idea.strip().replace('**', '')
    for chunk in stream_message("### ⭐ 步骤 8/9: 最优Idea筛选\n\n"):
        yield chunk
    for chunk in stream_message(f"**最优Idea**:\n\n{best_idea_clean}\n\n"):
        yield chunk
    for chunk in stream_message(f"**评估得分**:\n\n- 可行性: {score['feasibility']:.2f}/5.0\n- 创新性: {score['novelty']:.2f}/5.0\n- 总分: {score['total']:.2f}/10.0\n\n"):
        yield chunk
    
    # 步骤9: 生成研究计划（完整输出）
    for chunk in stream_message("### 📋 步骤 9/9: 研究计划生成\n\n"):
        yield chunk
    research_plan = await asyncio.to_thread(
        generator.generate_research_plan,
        query, papers, best_idea, inspirations["global_inspiration"]
    )
    
    # 添加分隔线和标题，优化格式
    for chunk in stream_message("---\n\n"):
        yield chunk
    for chunk in stream_message("## 📄 研究计划\n\n"):
        yield chunk
    # 完整输出研究计划
    for chunk in stream_message(f"{research_plan}\n\n"):
        yield chunk


async def generate_ideation_stream(query: str) -> AsyncGenerator[str, None]:
    """生成Idea的流式输出生成器（带超时控制，兼容Python 3.9）"""
    start_time = time.time()
    
    try:
        # 执行生成逻辑，在每次 yield 前检查超时
        async for item in _generate_ideation_internal(query):
            # 检查是否超时
            elapsed = time.time() - start_time
            if elapsed > REQUEST_TIMEOUT:
                for chunk in stream_message(f"## ❌ 超时错误\n\n请求处理超过 {REQUEST_TIMEOUT} 秒，已自动终止\n\n"):
                    yield chunk
                yield format_sse_done()
                return
            yield item
        
        # 发送结束标记
        yield format_sse_done()
                
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ 生成器错误: {e}\n{error_trace}")
        for chunk in stream_message(f"## ❌ 错误\n\n程序执行失败: {e}\n\n```\n{error_trace}\n```\n\n"):
            yield chunk
        yield format_sse_done()


@app.post("/ideation")
async def ideation(request: IdeationRequest):
    """
    Idea生成API端点
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    return StreamingResponse(
        generate_ideation_stream(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"  # 明确允许SSE跨域
        }
    )


@app.get("/health")
async def health():
    """健康检查端点 - 轻量级响应"""
    return {"status": "ok", "service": "ICAIS2025-Ideation API", "timestamp": time.time()}


@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "ICAIS2025-Ideation API",
        "version": "1.0.0",
        "health": "http://localhost:3000/health",
        "docs": "http://localhost:3000/docs",
        "ideation": "POST /ideation"
    }


# 优雅关闭处理
def shutdown_handler(signum, frame):
    print(f"\n⚠️ 收到终止信号 {signum}，正在关闭服务...")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    import uvicorn
    
    # 验证端口可用性
    import socket
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return True
            except OSError:
                return False
    
    if not check_port(3000):
        print(f"❌ 端口3000已被占用，请检查是否有其他服务在使用")
        sys.exit(1)
    
    print("🚀 启动 FastAPI 服务...")
    print(f"📍 监听地址: http://0.0.0.0:3000")
    print(f"📝 健康检查: curl http://localhost:3000/health")
    print(f"📚 API文档: http://localhost:3000/docs")
    
    # 使用更健壮的uvicorn配置
    uvicorn.run(
        app,  # 直接传递app对象，因为app在当前模块中定义
        host="0.0.0.0",
        port=3000,
        log_level="info",
        access_log=True,
        reload=False,  # 生产环境关闭热重载
        workers=1,  # 单worker避免并发问题
        loop="asyncio",  # 明确使用asyncio循环
        timeout_keep_alive=30,  # keep-alive超时
        limit_concurrency=100,  # 限制并发数
    )
