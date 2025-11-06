"""
工具函数模块
提供通用的辅助函数
"""

import hashlib
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def calculate_md5(file_path: str) -> str:
    """
    计算文件的MD5值
    
    Args:
        file_path: 文件路径
    
    Returns:
        MD5哈希值（十六进制字符串）
    """
    md5_hash = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        # 分块读取，避免大文件占用过多内存
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    return md5_hash.hexdigest()


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节）
    """
    return os.path.getsize(file_path)


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名（包含点号）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件扩展名，例如 '.png'
    """
    return Path(file_path).suffix.lower()


def is_image_file(file_path: str, allowed_formats: list = None) -> bool:
    """
    检查文件是否为支持的图片格式
    
    Args:
        file_path: 文件路径
        allowed_formats: 允许的格式列表，例如 ['.png', '.jpg']
    
    Returns:
        是否为支持的图片格式
    """
    if allowed_formats is None:
        allowed_formats = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp']
    
    ext = get_file_extension(file_path)
    return ext in allowed_formats


def generate_oss_key(
    local_path: str,
    naming_rule: str = 'uuid',
    path_prefix: str = ''
) -> str:
    """
    生成OSS对象键（存储路径）
    
    Args:
        local_path: 本地文件路径
        naming_rule: 命名规则，可选 'uuid', 'timestamp', 'original'
        path_prefix: 路径前缀，支持变量 {year}, {month}, {day}
    
    Returns:
        OSS对象键
    """
    # 处理路径前缀中的日期变量
    now = datetime.now()
    prefix = path_prefix.format(
        year=now.strftime('%Y'),
        month=now.strftime('%m'),
        day=now.strftime('%d')
    )
    
    # 获取文件扩展名
    ext = get_file_extension(local_path)
    
    # 根据命名规则生成文件名
    if naming_rule == 'uuid':
        filename = f"{uuid.uuid4().hex}{ext}"
    elif naming_rule == 'timestamp':
        timestamp = now.strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{timestamp}{ext}"
    elif naming_rule == 'original':
        filename = Path(local_path).name
    else:
        # 默认使用UUID
        filename = f"{uuid.uuid4().hex}{ext}"
    
    # 拼接完整路径
    oss_key = f"{prefix}{filename}"
    
    return oss_key


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读的格式
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的大小字符串，例如 '1.5 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"


def ensure_dir_exists(dir_path: str):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    Path(dir_path).expanduser().mkdir(parents=True, exist_ok=True)


def expand_path(path: str) -> Path:
    """
    展开路径，处理 ~ 和相对路径
    
    Args:
        path: 路径字符串
    
    Returns:
        Path对象
    """
    return Path(path).expanduser().resolve()

