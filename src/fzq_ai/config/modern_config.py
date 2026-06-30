"""
现代化配置管理系统
"""
from __future__ import annotations
import os
import json
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from dotenv import load_dotenv


@dataclass
class ProviderConfig:
    """LLM提供商配置"""
    api_key: str
    base_url: str = ""
    model: str = ""
    timeout: int = 60
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    ttl_seconds: int = 3600
    max_size: int = 1000
    redis_url: Optional[str] = None


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class PipelineConfig:
    """流水线配置"""
    max_workers: int = 4
    timeout: int = 300  # 5分钟
    retry_attempts: int = 3
    enable_metrics: bool = True
    enable_cache: bool = True


@dataclass
class AppConfig:
    """应用程序主配置"""
    # 基础配置
    app_name: str = "FZQ-AI"
    version: str = "1.0.0"
    debug: bool = False
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # LLM提供商配置
    deepseek: ProviderConfig = field(default_factory=ProviderConfig)
    openai: ProviderConfig = field(default_factory=ProviderConfig)
    qwen: ProviderConfig = field(default_factory=ProviderConfig)
    gemini: ProviderConfig = field(default_factory=ProviderConfig)
    glm: ProviderConfig = field(default_factory=ProviderConfig)
    
    # 其他配置
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    # 额外配置
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置默认值
        self.deepseek.base_url = self.deepseek.base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.deepseek.model = self.deepseek.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        self.openai.base_url = self.openai.base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.openai.model = self.openai.model or os.getenv("OPENAI_MODEL", "gpt-4o")
        
        self.qwen.base_url = self.qwen.base_url or os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.qwen.model = self.qwen.model or os.getenv("QWEN_MODEL", "qwen-max")
        
        self.gemini.base_url = self.gemini.base_url or os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.gemini.model = self.gemini.model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        self.glm.base_url = self.glm.base_url or os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.glm.model = self.glm.model or os.getenv("GLM_MODEL", "glm-4-flash")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = config_path
        self._config: Optional[AppConfig] = None
        self._load_dotenv()
        
    def _load_dotenv(self):
        """加载环境变量"""
        # 尝试在多个位置查找 .env 文件
        possible_paths = [
            Path.cwd() / ".env",
            Path(__file__).parent.parent.parent / ".env",
            Path.home() / ".fzq-ai" / ".env",
        ]
        
        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=str(path))
                break
    
    def load_from_file(self, file_path: Union[str, Path]) -> AppConfig:
        """从文件加载配置"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        elif file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")
        
        return self._dict_to_config(data)
    
    def load_from_env(self) -> AppConfig:
        """从环境变量加载配置"""
        config_data = {}
        
        # 加载基础配置
        config_data['app_name'] = os.getenv('APP_NAME', 'FZQ-AI')
        config_data['version'] = os.getenv('VERSION', '1.0.0')
        config_data['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'
        config_data['host'] = os.getenv('HOST', '0.0.0.0')
        config_data['port'] = int(os.getenv('PORT', '8000'))
        config_data['workers'] = int(os.getenv('WORKERS', '1'))
        
        # 加载提供商配置
        providers = ['deepseek', 'openai', 'qwen', 'gemini', 'glm']
        for provider in providers:
            config_data[provider] = {
                'api_key': os.getenv(f'{provider.upper()}_API_KEY', ''),
                'base_url': os.getenv(f'{provider.upper()}_BASE_URL', ''),
                'model': os.getenv(f'{provider.upper()}_MODEL', ''),
                'timeout': int(os.getenv(f'{provider.upper()}_TIMEOUT', '60')),
                'max_retries': int(os.getenv(f'{provider.upper()}_MAX_RETRIES', '3')),
                'temperature': float(os.getenv(f'{provider.upper()}_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv(f'{provider.upper()}_MAX_TOKENS', '4096')),
            }
        
        # 加载缓存配置
        config_data['cache'] = {
            'enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'ttl_seconds': int(os.getenv('CACHE_TTL_SECONDS', '3600')),
            'max_size': int(os.getenv('CACHE_MAX_SIZE', '1000')),
            'redis_url': os.getenv('REDIS_URL'),
        }
        
        # 加载日志配置
        config_data['logging'] = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file_path': os.getenv('LOG_FILE_PATH'),
            'max_bytes': int(os.getenv('LOG_MAX_BYTES', '10485760')),
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
        }
        
        # 加载流水线配置
        config_data['pipeline'] = {
            'max_workers': int(os.getenv('PIPELINE_MAX_WORKERS', '4')),
            'timeout': int(os.getenv('PIPELINE_TIMEOUT', '300')),
            'retry_attempts': int(os.getenv('PIPELINE_RETRY_ATTEMPTS', '3')),
            'enable_metrics': os.getenv('PIPELINE_ENABLE_METRICS', 'true').lower() == 'true',
            'enable_cache': os.getenv('PIPELINE_ENABLE_CACHE', 'true').lower() == 'true',
        }
        
        return self._dict_to_config(config_data)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """将字典转换为配置对象"""
        # 创建基本配置
        config = AppConfig()
        
        # 设置基础属性
        for attr in ['app_name', 'version', 'debug', 'host', 'port', 'workers']:
            if attr in data:
                setattr(config, attr, data[attr])
        
        # 设置提供商配置
        providers = ['deepseek', 'openai', 'qwen', 'gemini', 'glm']
        for provider in providers:
            if provider in data:
                provider_config = getattr(config, provider)
                provider_data = data[provider]
                
                for attr in ['api_key', 'base_url', 'model']:
                    if attr in provider_data:
                        setattr(provider_config, attr, provider_data[attr])
                
                for attr in ['timeout', 'max_retries', 'max_tokens']:
                    if attr in provider_data:
                        setattr(provider_config, attr, provider_data[attr])
                
                if 'temperature' in provider_data:
                    setattr(provider_config, 'temperature', provider_data['temperature'])
        
        # 设置其他配置
        if 'cache' in data:
            for attr, value in data['cache'].items():
                if hasattr(config.cache, attr):
                    setattr(config.cache, attr, value)
        
        if 'logging' in data:
            for attr, value in data['logging'].items():
                if hasattr(config.logging, attr):
                    setattr(config.logging, attr, value)
        
        if 'pipeline' in data:
            for attr, value in data['pipeline'].items():
                if hasattr(config.pipeline, attr):
                    setattr(config.pipeline, attr, value)
        
        return config
    
    def get_config(self) -> AppConfig:
        """获取配置实例"""
        if self._config is None:
            # 首先尝试从指定文件加载
            if self.config_path:
                self._config = self.load_from_file(self.config_path)
            else:
                # 否则从环境变量加载
                self._config = self.load_from_env()
        
        return self._config
    
    def reload_config(self) -> AppConfig:
        """重新加载配置"""
        self._config = None
        return self.get_config()


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config() -> AppConfig:
    """获取全局配置"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()


def init_config(config_path: Optional[Union[str, Path]] = None) -> AppConfig:
    """初始化配置"""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager.get_config()