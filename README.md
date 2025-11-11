# ICAIS2025-Ideation: 混合Idea生成系统

结合SciPIP和keyu-ideation优点的新idea生成方案，通过Semantic Scholar API检索论文，生成创新研究想法和完整研究计划。

## 核心特性

- ✅ **完全基于Semantic Scholar API**：无需维护本地数据库，实时检索最新论文
- ✅ **混合检索策略**：多维度检索（最新、高引用、相关）+ 语义重排序
- ✅ **深度论文分析**：逐篇生成Inspiration + 全局综合Inspiration
- ✅ **Brainstorm默认开启**：确保创新性
- ✅ **研究计划审查默认开启**：确保质量
- ✅ **智能筛选**：评估可行性和创新性，选择最优Idea
- ✅ **高效并行处理**：关键步骤并行化，5-6分钟内完成
- ✅ **中英文自动识别**：根据用户输入语言自动切换输出语言
- ✅ **研究计划标题生成**：自动生成一句话概括研究方案的标题

## 项目结构

```
ICAIS2025-Ideation/
├── main.py                    # 主程序入口
├── config.py                  # 配置管理（支持环境变量延迟加载）
├── llm_client.py              # LLM客户端（支持自定义API端点）
├── embedding_client.py        # Embedding客户端（API调用）
├── retriever.py               # 论文检索器（Semantic Scholar API）
├── idea_generator.py          # Idea生成器（包含所有生成、优化、评估功能）
├── prompt_template.py         # Prompt模板（支持中英文）
├── requirements.txt           # Python依赖
├── problem_fix_record.md      # 问题修复记录
└── README.md                  # 本文件
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件（在项目根目录）：

```bash
# LLM服务配置（支持新旧变量名）
SCI_MODEL_BASE_URL=http://your-api-endpoint/v1
SCI_MODEL_API_KEY=your-api-key
SCI_LLM_MODEL=deepseek-ai/DeepSeek-V3

# 或使用旧变量名（向后兼容）
# LLM_API_ENDPOINT=http://your-api-endpoint/v1
# LLM_API_KEY=your-api-key
# LLM_MODEL=deepseek-ai/DeepSeek-V3

# Embedding模型配置
SCI_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-4B
# 或使用旧变量名
# EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-4B

# 应用配置
APP_ENV=dev
DEBUG=True

# LLM请求配置
LLM_REQUEST_TIMEOUT=120  # 请求超时时间（秒）
DEFAULT_TEMPERATURE=0.6  # 默认温度
MAX_RETRIES=3            # 最大重试次数

# 论文检索配置
MAX_PAPERS_PER_QUERY=3   # 每类论文检索数量
MAX_TOTAL_PAPERS=10      # 最大总论文数
SEMANTIC_SCHOLAR_TIMEOUT=30      # Semantic Scholar API超时时间
SEMANTIC_SCHOLAR_MAX_RETRIES=10  # Semantic Scholar API最大重试次数

# 并行处理配置
MAX_WORKERS_INSPIRATION=8    # Inspiration生成并行数
MAX_WORKERS_OPTIMIZATION=3   # Idea优化并行数
INSPIRATION_TIMEOUT=30       # Inspiration生成超时时间
OPTIMIZATION_TIMEOUT=60      # Idea优化超时时间

# Idea生成配置
MAX_IDEAS_GENERATE=3     # 生成Idea数量
MAX_IDEAS_OPTIMIZE=2     # 优化Idea数量（只优化top-2）

# 功能开关
ENABLE_BRAINSTORM=True       # Brainstorm功能（默认开启）
ENABLE_PLAN_REVIEW=True      # 研究计划审查（默认开启）
```

## 使用方法

```bash
# 1. 配置环境变量（创建.env文件）
# 2. 运行主程序
python main.py
```

程序会自动：
1. 检测用户输入的语言（中文/英文）
2. 根据语言自动切换所有输出
3. 执行完整的idea生成流程
4. 输出最优Idea和完整研究计划

## 完整流程

系统执行以下9个步骤：

1. **提取关键词**：从用户查询中提取关键词（用于论文检索）
2. **扩展背景**：将简短查询扩展为详细研究背景
3. **混合检索论文**：
   - 并行检索最新、高引用、相关论文（3类）
   - 使用Semantic Scholar API
   - 语义重排序（基于embedding相似度）
   - 去重和融合
4. **Brainstorm生成**：生成创新想法（默认开启）
5. **多源Inspiration生成**：
   - 为top-8论文并行生成Inspiration
   - 生成全局综合Inspiration
6. **生成多个Idea**：
   - 并行生成基于论文Inspiration和全局Inspiration的Idea
   - 使用Brainstorm整合（默认开启）
   - 固定生成3个Idea
7. **迭代优化Idea**：
   - 只优化top-2个Idea（并行）
   - 每个Idea进行批判性审查和完善
8. **评估与筛选**：
   - 并行评估所有Idea的可行性和创新性
   - 选择总分最高的Idea作为最优Idea
9. **生成研究计划**：
   - 并行生成标题和初步研究计划
   - 研究计划审查（默认开启）
   - 完善研究计划
   - 输出包含标题的完整研究计划

## 输出格式

### 最优Idea
- 一个可行性和创新性最高的Idea
- 包含详细的创新点、工作原理、价值和创新性说明

### 研究计划
- **标题**：一句话概括研究方案
- **研究背景**：问题背景和关键发现
- **现有工作局限性**：现有方法的不足
- **研究计划**：详细的研究方案、方法论和实施步骤

## 性能优化

系统经过以下优化，确保在10分钟内完成：

### 并行化优化
- ✅ 步骤3：论文检索并行化（3类检索同时进行）
- ✅ 步骤5：论文Inspiration生成并行化（top-8论文）
- ✅ 步骤6：Idea生成并行化（论文Inspiration和全局Inspiration并行）
- ✅ 步骤7：Idea优化并行化（top-2并行优化）
- ✅ 步骤8：Idea评估并行化（所有Idea并行评估）
- ✅ 步骤9：标题和初步计划并行生成

### 数量优化
- 论文数量：最多10篇（每类3篇）
- 论文Inspiration：只对top-8生成
- 生成Idea数：固定3个
- 优化Idea数：只优化top-2

### 超时优化
- LLM请求超时：120秒（降低不必要的等待）
- 优化超时：60秒/idea
- 评估超时：60秒/idea

### 预期性能
- **总耗时**：约5-6分钟（优化后）
- **检索论文数**：最多10篇
- **生成Idea数**：3个
- **优化Idea数**：top-2
- **输出**：1个最优Idea + 1个完整研究计划

## 技术栈

- **论文检索**：Semantic Scholar API
- **LLM服务**：支持自定义API端点（兼容OpenAI格式）
- **Embedding模型**：支持API调用（默认：Qwen/Qwen3-Embedding-4B）
- **并行处理**：ThreadPoolExecutor
- **语言支持**：自动检测中英文，支持双语输出

## 关键设计

### 1. 混合检索策略
- **最新论文**：按发表时间排序
- **高引用论文**：按引用数排序
- **相关论文**：按相关性排序
- **语义重排序**：基于embedding相似度重新排序

### 2. 迭代优化机制
- **批判性审查**：识别Idea的弱点（重叠度、新颖性、可行性等）
- **完善改进**：根据审查结果改进Idea
- **容错机制**：优化失败时使用原始Idea

### 3. 评估筛选机制
- **可行性评分**：0-5分，评估Idea的实践性
- **创新性评分**：0-5分，评估Idea的创新程度
- **总分排序**：选择可行性+创新性总分最高的Idea

### 4. 语言自动识别
- 基于中文字符占比自动检测语言
- 所有LLM调用自动使用相应语言
- 确保输入输出语言一致

## 环境变量说明

### 必需配置
- `SCI_MODEL_BASE_URL` 或 `LLM_API_ENDPOINT`：LLM API端点
- `SCI_MODEL_API_KEY` 或 `LLM_API_KEY`：LLM API密钥

### 可选配置
- `SCI_LLM_MODEL` 或 `LLM_MODEL`：LLM模型名称（默认：deepseek-ai/DeepSeek-V3）
- `SCI_EMBEDDING_MODEL` 或 `EMBEDDING_MODEL_NAME`：Embedding模型名称（默认：jinaai/jina-embeddings-v3）
- 其他配置见上方配置示例

## 故障排除

### 常见问题

1. **Semantic Scholar API超时**
   - 已实现指数退避重试机制
   - 超时时间已优化为30秒
   - 使用HTTP协议减少连接时间

2. **Idea优化失败**
   - 已实现容错机制，失败时使用原始Idea
   - 优化超时已设置为60秒/idea

3. **LLM API响应格式错误**
   - 已添加完整的响应格式验证
   - 自动检测并处理异常情况

详细问题修复记录请参考：`problem_fix_record.md`

## 注意事项

1. **API限流**：代码中已添加延迟和重试机制，避免过快请求
2. **网络连接**：确保可以访问Semantic Scholar API和LLM API端点
3. **环境变量**：必须正确配置LLM API端点和密钥
4. **超时设置**：如果网络较慢，可以适当增加超时时间
5. **并行数量**：根据API服务能力调整并行数量，避免过载

## 更新日志

### 最新优化（2024）
- ✅ 步骤6 Idea生成并行化
- ✅ 步骤8 Idea评估并行化
- ✅ 步骤9 标题和初步计划并行生成
- ✅ 减少论文数量（12→10篇）
- ✅ 减少论文Inspiration数量（全部→top-8）
- ✅ 优化超时配置（180→120秒）
- ✅ 添加中英文自动识别
- ✅ 添加研究计划标题生成
- ✅ 优化Idea数量控制（固定3个）
- ✅ 优化Idea优化数量（top-3→top-2）

## 许可证

[添加许可证信息]

## 联系方式

s-lwq25@bjzgca.edu.cn
