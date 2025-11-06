"""
图片上传模块
负责将本地图片上传到阿里云OSS
"""

import os
import oss2
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .config import ConfigManager
from .utils import (
    calculate_md5,
    get_file_size,
    is_image_file,
    generate_oss_key,
    format_size,
)


class ImageUploader:
    """图片上传器"""
    
    def __init__(self, config: ConfigManager):
        """
        初始化图片上传器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config
        
        # 获取配置
        aliyun_config = config.get_aliyun_config()
        upload_config = config.get_upload_config()
        
        # 初始化OSS客户端
        auth = oss2.Auth(
            aliyun_config['access_key_id'],
            aliyun_config['access_key_secret']
        )
        
        self.bucket = oss2.Bucket(
            auth,
            aliyun_config['endpoint'],
            aliyun_config['bucket_name']
        )
        
        self.endpoint = aliyun_config['endpoint']
        self.bucket_name = aliyun_config['bucket_name']
        self.custom_domain = aliyun_config.get('custom_domain', '')
        
        # 上传配置
        self.path_prefix = upload_config.get('path_prefix', '')
        self.naming_rule = upload_config.get('naming_rule', 'uuid')
        self.enable_md5_check = upload_config.get('enable_md5_check', True)
        self.concurrent_limit = upload_config.get('concurrent_limit', 5)
        self.retry_times = upload_config.get('retry_times', 3)
        self.allowed_formats = upload_config.get('allowed_formats', [])
        self.max_size_mb = upload_config.get('max_size_mb', 10)
        
        # MD5缓存，用于去重
        self._md5_cache: Dict[str, str] = {}
    
    def upload_single(self, local_path: str, alt_text: str = "image") -> Dict:
        """
        上传单张图片
        
        Args:
            local_path: 本地图片路径
            alt_text: 图片描述文本
        
        Returns:
            上传结果字典:
            {
                'success': True/False,
                'local_path': '本地路径',
                'oss_key': 'OSS对象键',
                'url': 'https://...',
                'markdown': '![image](https://...)',
                'md5': 'xxx',
                'size': 文件大小（字节）,
                'error': '错误信息（如果失败）'
            }
        """
        result = {
            'success': False,
            'local_path': local_path,
            'oss_key': '',
            'url': '',
            'markdown': '',
            'md5': '',
            'size': 0,
            'error': ''
        }
        
        try:
            # 检查文件是否存在
            if not os.path.exists(local_path):
                result['error'] = f"文件不存在: {local_path}"
                return result
            
            # 检查文件格式
            if not is_image_file(local_path, self.allowed_formats):
                result['error'] = f"不支持的文件格式: {Path(local_path).suffix}"
                return result
            
            # 检查文件大小
            file_size = get_file_size(local_path)
            if file_size > self.max_size_mb * 1024 * 1024:
                result['error'] = (
                    f"文件大小超过限制: {format_size(file_size)} "
                    f"(最大 {self.max_size_mb} MB)"
                )
                return result
            
            result['size'] = file_size
            
            # 计算MD5
            file_md5 = calculate_md5(local_path)
            result['md5'] = file_md5
            
            # 检查是否已上传（去重）
            if self.enable_md5_check and file_md5 in self._md5_cache:
                oss_key = self._md5_cache[file_md5]
                url = self._generate_url(oss_key)
                result.update({
                    'success': True,
                    'oss_key': oss_key,
                    'url': url,
                    'markdown': f"![{alt_text}]({url})",
                })
                return result
            
            # 生成OSS存储路径
            oss_key = generate_oss_key(
                local_path,
                naming_rule=self.naming_rule,
                path_prefix=self.path_prefix
            )
            
            # 上传文件（带重试）
            for attempt in range(self.retry_times):
                try:
                    self.bucket.put_object_from_file(oss_key, local_path)
                    break
                except Exception as e:
                    if attempt == self.retry_times - 1:
                        raise
                    continue
            
            # 生成URL
            url = self._generate_url(oss_key)
            
            # 缓存MD5
            if self.enable_md5_check:
                self._md5_cache[file_md5] = oss_key
            
            result.update({
                'success': True,
                'oss_key': oss_key,
                'url': url,
                'markdown': f"![{alt_text}]({url})",
            })
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def upload_batch(
        self,
        image_paths: List[str],
        show_progress: bool = True
    ) -> List[Dict]:
        """
        批量上传图片
        
        Args:
            image_paths: 图片路径列表
            show_progress: 是否显示进度条
        
        Returns:
            上传结果列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.concurrent_limit) as executor:
            # 提交所有上传任务
            future_to_path = {
                executor.submit(self.upload_single, path): path
                for path in image_paths
            }
            
            # 使用进度条显示进度
            if show_progress:
                progress = tqdm(
                    total=len(image_paths),
                    desc="上传图片",
                    unit="张"
                )
            
            # 收集结果
            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)
                
                if show_progress:
                    progress.update(1)
            
            if show_progress:
                progress.close()
        
        return results
    
    def upload_from_directory(
        self,
        directory: str,
        recursive: bool = True
    ) -> List[Dict]:
        """
        从目录中上传所有图片
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
        
        Returns:
            上传结果列表
        """
        # 扫描目录中的图片文件
        image_paths = []
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"目录不存在: {directory}")
        
        # 扫描文件
        pattern = '**/*' if recursive else '*'
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and is_image_file(str(file_path), self.allowed_formats):
                image_paths.append(str(file_path))
        
        if not image_paths:
            print(f"⚠️  在目录 {directory} 中未找到图片文件")
            return []
        
        print(f"📁 找到 {len(image_paths)} 张图片")
        
        # 批量上传
        return self.upload_batch(image_paths)
    
    def _generate_url(self, oss_key: str) -> str:
        """
        生成图片访问URL
        
        Args:
            oss_key: OSS对象键
        
        Returns:
            完整的访问URL
        """
        # 如果配置了自定义域名，使用自定义域名
        if self.custom_domain:
            domain = self.custom_domain.rstrip('/')
            return f"{domain}/{oss_key}"
        
        # 否则使用默认的OSS域名
        # 格式：https://{bucket}.{endpoint}/{key}
        return f"https://{self.bucket_name}.{self.endpoint}/{oss_key}"
    
    def check_connection(self) -> bool:
        """
        检查OSS连接是否正常
        
        Returns:
            连接是否成功
        """
        try:
            # 尝试列出bucket信息
            self.bucket.get_bucket_info()
            return True
        except Exception:
            return False
    
    def list_objects(self, prefix: str = '', max_keys: int = 100) -> List[Dict]:
        """
        列出OSS中的对象
        
        Args:
            prefix: 对象前缀
            max_keys: 最大返回数量
        
        Returns:
            对象信息列表
        """
        try:
            objects = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=max_keys):
                objects.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'url': self._generate_url(obj.key)
                })
            return objects
        except Exception as e:
            print(f"❌ 列出对象失败: {e}")
            return []
    
    def delete_object(self, oss_key: str) -> bool:
        """
        删除OSS中的对象
        
        Args:
            oss_key: OSS对象键
        
        Returns:
            是否删除成功
        """
        try:
            self.bucket.delete_object(oss_key)
            return True
        except Exception as e:
            print(f"❌ 删除对象失败: {e}")
            return False

