"""
Markdown处理模块
负责处理Markdown文档中的本地图片引用
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import unquote

from .uploader import ImageUploader


class MarkdownProcessor:
    """Markdown文档处理器"""
    
    def __init__(self, uploader: ImageUploader):
        """
        初始化Markdown处理器
        
        Args:
            uploader: 图片上传器实例
        """
        self.uploader = uploader
        self.config = uploader.config
        
        # 获取Markdown配置
        md_config = self.config.get_markdown_config()
        self.backup_original = md_config.get('backup_original', True)
        self.backup_suffix = md_config.get('backup_suffix', '.bak')
        self.image_alt_text = md_config.get('image_alt_text', 'image')
        self.recursive = md_config.get('recursive', True)
        
        # 本地图片匹配正则
        # 匹配格式：![xxx](./images/xxx.png), ![xxx](../xxx.jpg) 等
        # 不匹配：![xxx](http://...), ![xxx](https://...)
        self.local_image_pattern = md_config.get(
            'local_image_pattern',
            r'!\[([^\]]*)\]\((?!http)([^)]+)\)'
        )
    
    def process_file(self, md_path: str) -> Dict:
        """
        处理单个Markdown文件
        
        Args:
            md_path: Markdown文件路径
        
        Returns:
            处理结果字典:
            {
                'success': True/False,
                'file_path': 'Markdown文件路径',
                'processed_images': 处理的图片数量,
                'failed_images': 失败的图片数量,
                'backup_path': '备份文件路径',
                'error': '错误信息（如果失败）'
            }
        """
        result = {
            'success': False,
            'file_path': md_path,
            'processed_images': 0,
            'failed_images': 0,
            'backup_path': '',
            'error': ''
        }
        
        try:
            md_path = Path(md_path).resolve()
            
            # 检查文件是否存在
            if not md_path.exists():
                result['error'] = f"文件不存在: {md_path}"
                return result
            
            # 检查是否为Markdown文件
            if md_path.suffix.lower() not in ['.md', '.markdown']:
                result['error'] = f"不是Markdown文件: {md_path}"
                return result
            
            # 读取文件内容
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取本地图片引用
            local_images = self._extract_local_images(content, md_path)
            
            if not local_images:
                result['success'] = True
                result['error'] = "未找到本地图片引用"
                return result
            
            print(f"\n📝 处理文件: {md_path.name}")
            print(f"🔍 找到 {len(local_images)} 个本地图片引用")
            
            # 上传图片并收集替换信息
            replacements = {}
            for match, alt_text, img_path in local_images:
                # 上传图片
                upload_result = self.uploader.upload_single(img_path, alt_text or self.image_alt_text)
                
                if upload_result['success']:
                    # 记录替换信息：原始Markdown语法 -> 新的Markdown语法
                    replacements[match] = upload_result['markdown']
                    result['processed_images'] += 1
                    print(f"  ✅ {Path(img_path).name} -> {upload_result['url']}")
                else:
                    result['failed_images'] += 1
                    print(f"  ❌ {Path(img_path).name}: {upload_result['error']}")
            
            # 如果有成功上传的图片，替换内容
            if replacements:
                # 备份原文件
                if self.backup_original:
                    backup_path = str(md_path) + self.backup_suffix
                    shutil.copy2(md_path, backup_path)
                    result['backup_path'] = backup_path
                
                # 替换图片链接
                new_content = self._replace_image_links(content, replacements)
                
                # 保存更新后的文件
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                result['success'] = True
                print(f"\n✨ 处理完成！成功 {result['processed_images']} 张，失败 {result['failed_images']} 张")
            else:
                result['error'] = "没有图片上传成功"
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def process_directory(self, directory: str) -> List[Dict]:
        """
        处理目录中的所有Markdown文件
        
        Args:
            directory: 目录路径
        
        Returns:
            处理结果列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"目录不存在: {directory}")
        
        # 扫描Markdown文件
        pattern = '**/*.md' if self.recursive else '*.md'
        md_files = list(dir_path.glob(pattern))
        
        if not md_files:
            print(f"⚠️  在目录 {directory} 中未找到Markdown文件")
            return []
        
        print(f"📁 找到 {len(md_files)} 个Markdown文件\n")
        
        # 处理每个文件
        results = []
        for md_file in md_files:
            result = self.process_file(str(md_file))
            results.append(result)
        
        # 输出汇总
        total_processed = sum(r['processed_images'] for r in results)
        total_failed = sum(r['failed_images'] for r in results)
        print(f"\n🎉 全部完成！共处理 {total_processed} 张图片，失败 {total_failed} 张")
        
        return results
    
    def _extract_local_images(
        self,
        content: str,
        md_path: Path
    ) -> List[Tuple[str, str, str]]:
        """
        从Markdown内容中提取本地图片引用
        
        Args:
            content: Markdown内容
            md_path: Markdown文件路径（用于解析相对路径）
        
        Returns:
            列表，每个元素为 (完整匹配字符串, alt文本, 绝对图片路径)
        """
        images = []
        
        # 使用正则提取本地图片
        for match in re.finditer(self.local_image_pattern, content):
            full_match = match.group(0)  # 完整的 ![alt](path)
            alt_text = match.group(1)    # alt文本
            img_path = match.group(2)    # 图片路径
            
            # URL解码（处理中文路径）
            img_path = unquote(img_path)
            
            # 解析为绝对路径
            if not Path(img_path).is_absolute():
                # 相对路径，相对于Markdown文件所在目录
                img_path = (md_path.parent / img_path).resolve()
            else:
                img_path = Path(img_path).resolve()
            
            # 检查文件是否存在
            if img_path.exists():
                images.append((full_match, alt_text, str(img_path)))
        
        return images
    
    def _replace_image_links(
        self,
        content: str,
        replacements: Dict[str, str]
    ) -> str:
        """
        替换Markdown内容中的图片链接
        
        Args:
            content: 原始Markdown内容
            replacements: 替换映射，{原始语法: 新语法}
        
        Returns:
            替换后的内容
        """
        new_content = content
        
        for old_syntax, new_syntax in replacements.items():
            # 转义特殊字符，避免正则冲突
            old_escaped = re.escape(old_syntax)
            new_content = re.sub(old_escaped, new_syntax, new_content)
        
        return new_content

