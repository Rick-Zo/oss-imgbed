"""
配置管理模块
负责读取和管理配置文件
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果不指定，会按以下顺序查找：
                1. 当前目录的 config.yaml
                2. 项目根目录的 config.yaml
                3. ~/.oss_image_bed/config.yaml（用户主目录）
        """
        if config_path is None:
            config_path = self._find_config_file()
        
        self.config_path = Path(config_path).expanduser().resolve()
        self.project_root = self._get_project_root()
        self.config = self._load_config()
    
    def _find_config_file(self) -> Path:
        """
        查找配置文件
        按优先级顺序查找：当前目录 -> 项目根目录 -> 用户主目录
        
        Returns:
            配置文件路径
        """
        # 1. 当前工作目录
        current_dir_config = Path.cwd() / "config.yaml"
        if current_dir_config.exists():
            return current_dir_config
        
        # 2. 项目根目录（如果从包中调用）
        try:
            # 获取当前文件所在的包根目录的上两级（src/oss_image_bed -> src -> 项目根）
            package_root = Path(__file__).parent.parent.parent
            project_config = package_root / "config.yaml"
            if project_config.exists():
                return project_config
        except:
            pass
        
        # 3. 用户主目录（兼容旧版本）
        user_config = Path.home() / ".oss_image_bed" / "config.yaml"
        if user_config.exists():
            return user_config
        
        # 如果都不存在，返回项目根目录路径（供后续创建）
        try:
            return Path(__file__).parent.parent.parent / "config.yaml"
        except:
            return Path.cwd() / "config.yaml"
    
    def _get_project_root(self) -> Path:
        """
        获取项目根目录
        
        Returns:
            项目根目录路径
        """
        # 如果配置文件在项目中，使用配置文件所在目录作为项目根目录
        if self.config_path.name == "config.yaml":
            return self.config_path.parent
        
        # 否则使用当前工作目录
        return Path.cwd()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: 配置文件格式错误
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请先运行 'oss-image init' 创建配置文件"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 验证必填配置
            self._validate_config(config)
            
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件格式错误: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """
        验证配置文件必填项
        
        Args:
            config: 配置字典
        
        Raises:
            ValueError: 缺少必填配置项
        """
        required_fields = [
            ('aliyun', 'access_key_id'),
            ('aliyun', 'access_key_secret'),
            ('aliyun', 'endpoint'),
            ('aliyun', 'bucket_name'),
        ]
        
        for section, field in required_fields:
            if section not in config:
                raise ValueError(f"配置文件缺少 '{section}' 部分")
            
            value = config[section].get(field, "")
            if not value or value.startswith("your-"):
                raise ValueError(
                    f"请在配置文件中填写 '{section}.{field}'\n"
                    f"配置文件位置: {self.config_path}"
                )
    
    def get(self, *keys, default=None):
        """
        获取配置值，支持多级键
        
        Args:
            *keys: 配置键路径，例如 get('aliyun', 'access_key_id')
            default: 默认值
        
        Returns:
            配置值
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_aliyun_config(self) -> Dict[str, str]:
        """
        获取阿里云OSS配置
        
        Returns:
            包含access_key_id, access_key_secret, endpoint, bucket_name的字典
        """
        return {
            'access_key_id': self.get('aliyun', 'access_key_id'),
            'access_key_secret': self.get('aliyun', 'access_key_secret'),
            'endpoint': self.get('aliyun', 'endpoint'),
            'bucket_name': self.get('aliyun', 'bucket_name'),
            'custom_domain': self.get('aliyun', 'custom_domain', default=''),
        }
    
    def get_upload_config(self) -> Dict[str, Any]:
        """
        获取上传配置
        
        Returns:
            上传配置字典
        """
        return self.config.get('upload', {})
    
    def get_markdown_config(self) -> Dict[str, Any]:
        """
        获取Markdown处理配置
        
        Returns:
            Markdown配置字典
        """
        return self.config.get('markdown', {})
    
    def reload(self):
        """重新加载配置文件"""
        self.config = self._load_config()
    
    def resolve_path(self, path: str) -> Path:
        """
        解析路径，支持相对路径和绝对路径
        相对路径会相对于项目根目录解析
        
        Args:
            path: 路径字符串
        
        Returns:
            解析后的绝对路径
        """
        path_obj = Path(path).expanduser()
        
        # 如果是绝对路径，直接返回
        if path_obj.is_absolute():
            return path_obj
        
        # 相对路径，相对于项目根目录
        return (self.project_root / path_obj).resolve()

