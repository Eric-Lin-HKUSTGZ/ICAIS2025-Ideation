# Hybrid-Ideation: 混合Idea生成系统

结合SciPIP和keyu-ideation优点的新idea生成方案。

## 特性

- ✅ **完全基于Semantic Scholar API**：无需维护本地数据库
- ✅ **混合检索策略**：多维度检索+语义重排序
- ✅ **深度论文分析**：逐篇生成Inspiration+全局综合
- ✅ **Brainstorm默认开启**：确保创新性
- ✅ **研究计划审查默认开启**：确保质量
- ✅ **智能筛选**：评估可行性和创新性，选择最优Idea
- ✅ **高效并行处理**：10分钟内完成

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建环境变量文件 `env/dev` 或 `env/prod`：

```bash
# LLM服务配置
LLM_API_ENDPOINT=http://your-api-endpoint/v1
LLM_API_KEY=your-api-key
LLM_MODEL=deepseek-ai/DeepSeek-V3

# 应用配置
APP_ENV=env
DEBUG=True
```

## 使用方法

```bash
python main.py
```

## 流程说明

1. **提取关键词**：从用户查询中提取关键词
2. **扩展背景**：将简短查询扩展为详细研究背景
3. **混合检索**：使用Semantic Scholar API检索最新、高引用、相关论文
4. **语义重排序**：使用embedding模型对检索结果重排序
5. **Brainstorm生成**：生成创新想法（默认开启）
6. **多源Inspiration生成**：为每篇论文生成Inspiration+全局Inspiration
7. **生成多个Idea**：基于Inspiration生成多个Idea，并用Brainstorm整合
8. **迭代优化**：批判性审查和完善Idea（只优化top-3）
9. **评估与筛选**：评估可行性和创新性，选择最优Idea
10. **生成研究计划**：基于最优Idea生成研究计划，并进行审查和完善

## 输出

- 一个最优Idea（可行性和创新性最高）
- 对应的完整研究计划（包含：研究背景、现有工作局限性、研究计划）

## 性能

- 总耗时：约9-10分钟
- 检索论文数：最多12篇
- 生成Idea数：3-5个
- 优化Idea数：top-3
