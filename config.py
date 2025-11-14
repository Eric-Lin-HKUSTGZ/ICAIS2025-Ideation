import os
from typing import Optional, Any


class ConfigMeta(type):
    """元类，用于实现类级别的__getattr__"""
    
    def __getattr__(cls, name: str) -> Any:
        """动态获取配置属性"""
        return cls._get_config_value(name)


class Config(metaclass=ConfigMeta):
    """应用配置类 - 使用元类实现延迟读取环境变量"""

    @staticmethod
    def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量"""
        return os.getenv(key, default)
    
    @staticmethod
    def _get_env_with_fallback(new_key: str, old_key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量，支持新旧变量名fallback"""
        return os.getenv(new_key) or os.getenv(old_key) or default

    @classmethod
    def _get_config_value(cls, name: str) -> Any:
        """动态获取配置属性"""
        # LLM服务配置（适配新的环境变量名称）
        if name == "LLM_API_ENDPOINT":
            return cls._get_env_with_fallback("SCI_MODEL_BASE_URL", "LLM_API_ENDPOINT")
        elif name == "LLM_API_KEY":
            return cls._get_env_with_fallback("SCI_MODEL_API_KEY", "LLM_API_KEY")
        elif name == "LLM_MODEL":
            return cls._get_env_with_fallback("SCI_LLM_MODEL", "LLM_MODEL", "deepseek-ai/DeepSeek-V3")
        elif name == "LLM_REASONING_MODEL":
            reasoning_model = cls._get_env("SCI_LLM_REASONING_MODEL")
            if not reasoning_model:
                raise ValueError("SCI_LLM_REASONING_MODEL环境变量未设置，请配置推理模型")
            return reasoning_model
        elif name == "LLM_REQUEST_TIMEOUT":
            return int(cls._get_env("LLM_REQUEST_TIMEOUT", "120"))  # 降低到120秒
        
        # 应用配置
        elif name == "APP_ENV":
            return cls._get_env("APP_ENV", "dev")
        elif name == "DEBUG":
            return cls._get_env("DEBUG", "True").lower() == "true"
        
        # LLM请求配置
        elif name == "DEFAULT_TEMPERATURE":
            return float(cls._get_env("DEFAULT_TEMPERATURE", "0.6"))
        elif name == "MAX_RETRIES":
            return int(cls._get_env("MAX_RETRIES", "3"))
        
        # 论文检索配置
        elif name == "MAX_PAPERS_PER_QUERY":
            return int(cls._get_env("MAX_PAPERS_PER_QUERY", "3"))  # 减少到3
        elif name == "MAX_TOTAL_PAPERS":
            return int(cls._get_env("MAX_TOTAL_PAPERS", "10"))  # 减少到10
        elif name == "SEMANTIC_SCHOLAR_TIMEOUT":
            return int(cls._get_env("SEMANTIC_SCHOLAR_TIMEOUT", "30"))  # 增加到30秒
        elif name == "SEMANTIC_SCHOLAR_MAX_RETRIES":
            return int(cls._get_env("SEMANTIC_SCHOLAR_MAX_RETRIES", "10"))  # 减少重试次数，但增加延迟
        
        # Embedding配置（适配新的环境变量名称）
        elif name == "EMBEDDING_MODEL_NAME":
            return cls._get_env_with_fallback("SCI_EMBEDDING_MODEL", "EMBEDDING_MODEL_NAME", "jinaai/jina-embeddings-v3")
        elif name == "EMBEDDING_API_ENDPOINT":
            # 优先使用embedding专用配置，如果没有则fallback到LLM配置（向后兼容）
            embedding_url = cls._get_env("SCI_EMBEDDING_BASE_URL")
            # if embedding_url:
            #     return embedding_url
            # # Fallback到LLM配置
            # return cls._get_env_with_fallback("SCI_MODEL_BASE_URL", "LLM_API_ENDPOINT")
            return embedding_url
        elif name == "EMBEDDING_API_KEY":
            # 优先使用embedding专用配置，如果没有则fallback到LLM配置（向后兼容）
            embedding_key = cls._get_env("SCI_EMBEDDING_API_KEY")
            # if embedding_key:
            #     return embedding_key
            # # Fallback到LLM配置
            # return cls._get_env_with_fallback("SCI_MODEL_API_KEY", "LLM_API_KEY")
            return embedding_key
        elif name == "EMBEDDING_DEVICE":
            return cls._get_env("EMBEDDING_DEVICE", "cpu")
        
        # 并行处理配置
        elif name == "MAX_WORKERS_INSPIRATION":
            return int(cls._get_env("MAX_WORKERS_INSPIRATION", "8"))
        elif name == "MAX_WORKERS_OPTIMIZATION":
            return int(cls._get_env("MAX_WORKERS_OPTIMIZATION", "3"))
        elif name == "INSPIRATION_TIMEOUT":
            return int(cls._get_env("INSPIRATION_TIMEOUT", "30"))
        elif name == "OPTIMIZATION_TIMEOUT":
            return int(cls._get_env("OPTIMIZATION_TIMEOUT", "60"))
        
        # Idea生成配置
        elif name == "MAX_IDEAS_GENERATE":
            return int(cls._get_env("MAX_IDEAS_GENERATE", "3"))
        elif name == "MAX_IDEAS_OPTIMIZE":
            return int(cls._get_env("MAX_IDEAS_OPTIMIZE", "2"))
        
        # Brainstorm和研究计划审查配置（默认开启）
        elif name == "ENABLE_BRAINSTORM":
            return cls._get_env("ENABLE_BRAINSTORM", "True").lower() == "true"
        elif name == "ENABLE_PLAN_REVIEW":
            return cls._get_env("ENABLE_PLAN_REVIEW", "True").lower() == "true"
        
        # 如果属性不存在，抛出AttributeError
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否正确"""
        if not cls.LLM_API_ENDPOINT or not cls.LLM_API_KEY:
            print("❌ LLM_API_ENDPOINT 或 LLM_API_KEY 未配置")
            return False
        return True

    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏敏感信息）"""
        print("=== 当前配置 ===")
        print(f"环境: {cls.APP_ENV}")
        print(f"调试模式: {cls.DEBUG}")
        print(f"LLM端点: {cls.LLM_API_ENDPOINT}")
        
        # 检查推理模型是否配置
        reasoning_model_configured = False
        try:
            reasoning_model = cls.LLM_REASONING_MODEL
            reasoning_model_configured = True
        except (ValueError, AttributeError):
            pass
        
        # 根据实际使用情况显示模型信息
        # 普通模型用于：关键词提取、背景扩展
        # 推理模型用于：Brainstorm、Inspiration生成、Idea生成/优化/评估、研究计划生成
        if reasoning_model_configured:
            # 两个模型都会被使用，都显示
            print(f"普通模型 (用于简单任务): {cls.LLM_MODEL}")
            print(f"推理模型 (用于深度推理任务): {reasoning_model}")
        else:
            # 只显示普通模型（推理模型未配置，深度推理任务会失败）
            print(f"LLM模型: {cls.LLM_MODEL}")
            print("⚠️  推理模型未配置，深度推理任务将无法执行")
        
        print(f"请求超时: {cls.LLM_REQUEST_TIMEOUT}秒")
        print(f"默认温度: {cls.DEFAULT_TEMPERATURE}")
        print(f"最大重试: {cls.MAX_RETRIES}")
        print(f"每类论文数: {cls.MAX_PAPERS_PER_QUERY}")
        print(f"最大总论文数: {cls.MAX_TOTAL_PAPERS}")
        print(f"Brainstorm: {'开启' if cls.ENABLE_BRAINSTORM else '关闭'}")
        print(f"研究计划审查: {'开启' if cls.ENABLE_PLAN_REVIEW else '关闭'}")
        print("================")
