import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain.llms.ollama import Ollama
from langchain_core.language_models.base import BaseLanguageModel

# Load environment variables from .env file
load_dotenv()

class BaseLLMWrapper(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """生成文本的抽象方法"""
        pass
    
    @abstractmethod
    def get_model(self) -> BaseLanguageModel:
        """获取底层LLM模型的抽象方法"""
        pass

class OpenAIWrapper(BaseLLMWrapper):
    def __init__(self, model_name: str = None, **kwargs):
        # Parse the OAI_CONFIG_LIST from environment variables
        config_str = os.getenv("OAI_CONFIG_LIST")
        if config_str is None:
            raise ValueError("OAI_CONFIG_LIST must be provided in the .env file")
        
        try:
            import json
            config = json.loads(config_str)[0]  # Get the first configuration
        except (json.JSONDecodeError, IndexError) as e:
            raise ValueError(f"Invalid OAI_CONFIG_LIST format: {e}")
        
        # Use values from config, with kwargs and defaults as fallbacks
        self.llm = ChatOpenAI(
            model_name=model_name or config.get("model", "gpt-3.5-turbo"),
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            **kwargs
        )
    
    async def generate(self, prompt: str) -> str:
        return await self.llm.ainvoke(prompt)
    
    def get_model(self) -> BaseLanguageModel:
        return self.llm

class OllamaWrapper(BaseLLMWrapper):
    def __init__(self, model_name: str = "llama2", **kwargs):
        self.llm = Ollama(
            model=model_name,
            **kwargs
        )
    
    async def generate(self, prompt: str) -> str:
        return await self.llm.ainvoke(prompt)
    
    def get_model(self) -> BaseLanguageModel:
        return self.llm

def create_llm(
    backend: str = "openai",
    model_config: Optional[Dict[str, Any]] = None
) -> BaseLLMWrapper:
    """
    工厂函数，用于创建LLM实例
    
    Args:
        backend: 后端类型，支持 "openai" 或 "ollama"
        model_config: 模型配置参数
    
    Returns:
        BaseLLMWrapper: LLM包装器实例
    """
    if model_config is None:
        model_config = {}
    
    if backend == "openai":
        return OpenAIWrapper(**model_config)
    elif backend == "ollama":
        return OllamaWrapper(**model_config)
    else:
        raise ValueError(f"Unsupported backend: {backend}") 