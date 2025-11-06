"""
命令行工具模块
提供CLI命令接口
"""

import click
import sys
import shutil
from pathlib import Path
from tabulate import tabulate

from .config import ConfigManager
from .uploader import ImageUploader
from .processor import MarkdownProcessor
from .utils import format_size


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    阿里云OSS图床命令行工具
    
    一键将本地图片上传到阿里云OSS，并生成Markdown链接
    """
    pass


@cli.command()
@click.option('--project', is_flag=True, help='在项目目录创建配置文件')
def init(project):
    """初始化配置文件"""
    
    if project:
        # 在当前目录创建配置文件
        config_file = Path.cwd() / 'config.yaml'
    else:
        # 在用户主目录创建配置文件
        config_dir = Path.home() / '.oss_image_bed'
        config_file = config_dir / 'config.yaml'
        
        # 创建配置目录
        config_dir.mkdir(exist_ok=True)
        (config_dir / 'logs').mkdir(exist_ok=True)
        (config_dir / 'cache').mkdir(exist_ok=True)
    
    # 检查配置文件是否已存在
    if config_file.exists():
        click.echo(f"⚠️  配置文件已存在: {config_file}")
        if not click.confirm("是否覆盖现有配置？"):
            return
    
    # 尝试从多个位置查找模板文件
    template_locations = [
        # 1. 包安装目录的上两级/config
        Path(__file__).parent.parent.parent / 'config' / 'config.yaml.template',
        # 2. 当前工作目录
        Path.cwd() / 'config' / 'config.yaml.template',
        # 3. 包目录的config子目录
        Path(__file__).parent / 'config' / 'config.yaml.template',
    ]
    
    template_file = None
    for loc in template_locations:
        if loc.exists():
            template_file = loc
            break
    
    if template_file and template_file.exists():
        # 复制模板文件
        shutil.copy2(template_file, config_file)
        click.echo(f"✅ 配置文件已创建: {config_file}")
    else:
        # 如果找不到模板，直接创建一个基础配置
        _create_default_config(config_file)
        click.echo(f"✅ 配置文件已创建: {config_file}")
    
    click.echo("\n📝 请编辑配置文件，填写以下必填项：")
    click.echo("  - aliyun.access_key_id")
    click.echo("  - aliyun.access_key_secret")
    click.echo("  - aliyun.endpoint")
    click.echo("  - aliyun.bucket_name")
    click.echo(f"\n编辑命令: vim {config_file}")


def _create_default_config(config_file: Path):
    """创建默认配置文件"""
    default_config = """# 阿里云OSS图床配置文件

# ============================================
# 阿里云OSS配置（必填）
# ============================================
aliyun:
  # AccessKey ID（请填写你的AccessKey ID）
  access_key_id: "your-access-key-id"
  
  # AccessKey Secret（请填写你的AccessKey Secret）
  access_key_secret: "your-access-key-secret"
  
  # OSS服务区域节点
  # 常用区域：
  # - oss-cn-guangzhou.aliyuncs.com (华南1-广州)
  # - oss-cn-beijing.aliyuncs.com (华北2-北京)
  # - oss-cn-shanghai.aliyuncs.com (华东2-上海)
  # - oss-cn-shenzhen.aliyuncs.com (华南1-深圳)
  # - oss-cn-hangzhou.aliyuncs.com (华东1-杭州)
  endpoint: "oss-cn-guangzhou.aliyuncs.com"
  
  # Bucket名称
  bucket_name: "your-bucket-name"
  
  # 自定义域名（可选）
  custom_domain: ""

# ============================================
# 上传配置
# ============================================
upload:
  # 上传路径前缀（支持变量：{year}年份4位, {month}月份2位, {day}日期2位）
  # 默认按日期分类：20251105/
  path_prefix: "{year}{month}{day}/"
  
  # 文件命名规则：uuid(推荐) / timestamp / original
  naming_rule: "uuid"
  
  # 是否启用MD5去重
  enable_md5_check: true
  
  # 并发上传数量
  concurrent_limit: 5
  
  # 上传失败重试次数
  retry_times: 3
  
  # 支持的图片格式
  allowed_formats:
    - ".png"
    - ".jpg"
    - ".jpeg"
    - ".gif"
    - ".svg"
    - ".webp"
    - ".bmp"
  
  # 图片最大大小限制（MB）
  max_size_mb: 10

# ============================================
# Markdown处理配置
# ============================================
markdown:
  backup_original: true
  backup_suffix: ".bak"
  image_alt_text: "image"
  recursive: true
  local_image_pattern: '!\\[([^\\]]*)\\]\\((?!http)([^)]+)\\)'

# ============================================
# 日志配置
# ============================================
logging:
  level: "INFO"
  file_path: "logs/app.log"
  max_size_mb: 10
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================
# 缓存配置
# ============================================
cache:
  enabled: true
  file_path: "cache/upload_cache.db"
  expire_days: 30

# ============================================
# 代理配置
# ============================================
proxy:
  enabled: false
  http_proxy: ""
  https_proxy: ""
"""
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(default_config)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--alt', default='image', help='图片描述文本')
@click.option('--folder', default='', help='自定义文件夹名称（覆盖配置文件的path_prefix）')
@click.option('--copy/--no-copy', default=True, help='是否复制Markdown链接到剪贴板')
def upload(image_path, alt, folder, copy):
    """上传单张图片
    
    示例：
      oss-image upload image.png                    # 使用默认日期文件夹
      oss-image upload image.png --folder myblog    # 保存到 myblog/ 文件夹
      oss-image upload image.png --folder ""        # 保存到根目录
    """
    try:
        # 加载配置
        config = ConfigManager()
        uploader = ImageUploader(config)
        
        # 如果指定了文件夹，临时覆盖配置
        if folder is not None:
            # 确保文件夹名以/结尾（如果不是空字符串）
            if folder and not folder.endswith('/'):
                folder += '/'
            uploader.path_prefix = folder
        
        # 上传图片
        click.echo(f"📤 正在上传: {image_path}")
        if folder:
            click.echo(f"📁 目标文件夹: {folder}")
        
        result = uploader.upload_single(image_path, alt)
        
        if result['success']:
            click.echo(f"\n✅ 上传成功！")
            click.echo(f"📍 URL: {result['url']}")
            click.echo(f"📋 Markdown: {result['markdown']}")
            click.echo(f"💾 大小: {format_size(result['size'])}")
            
            # 复制到剪贴板
            if copy:
                try:
                    import pyperclip
                    pyperclip.copy(result['markdown'])
                    click.echo(f"\n✨ Markdown链接已复制到剪贴板")
                except ImportError:
                    click.echo(f"\n💡 提示: 安装 pyperclip 可自动复制到剪贴板 (pip install pyperclip)")
        else:
            click.echo(f"❌ 上传失败: {result['error']}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='是否递归扫描子目录')
@click.option('--folder', default='', help='自定义文件夹名称')
def upload_batch(directory, recursive, folder):
    """批量上传目录中的所有图片
    
    示例：
      oss-image upload-batch ./images/              # 使用默认日期文件夹
      oss-image upload-batch ./images/ --folder project1  # 保存到 project1/ 文件夹
    """
    try:
        # 加载配置
        config = ConfigManager()
        uploader = ImageUploader(config)
        
        # 如果指定了文件夹，临时覆盖配置
        if folder is not None:
            if folder and not folder.endswith('/'):
                folder += '/'
            uploader.path_prefix = folder
        
        # 批量上传
        click.echo(f"📁 扫描目录: {directory}")
        if folder:
            click.echo(f"📁 目标文件夹: {folder}")
        click.echo()
        
        results = uploader.upload_from_directory(directory, recursive)
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - success_count
        
        click.echo(f"\n✨ 完成！成功 {success_count} 张，失败 {failed_count} 张")
        
        # 显示失败的图片
        if failed_count > 0:
            click.echo("\n❌ 失败的图片：")
            for r in results:
                if not r['success']:
                    click.echo(f"  - {r['local_path']}: {r['error']}")
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('markdown_path', type=click.Path(exists=True))
def convert(markdown_path):
    """处理Markdown文档，将本地图片转换为图床链接"""
    try:
        # 加载配置
        config = ConfigManager()
        uploader = ImageUploader(config)
        processor = MarkdownProcessor(uploader)
        
        # 判断是文件还是目录
        path = Path(markdown_path)
        
        if path.is_file():
            # 处理单个文件
            result = processor.process_file(str(path))
            
            if not result['success']:
                click.echo(f"⚠️  {result['error']}")
        
        elif path.is_dir():
            # 处理整个目录
            processor.process_directory(str(path))
        
        else:
            click.echo(f"❌ 无效的路径: {markdown_path}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.group()
def config_cmd():
    """配置管理"""
    pass


@config_cmd.command('show')
def config_show():
    """显示当前配置"""
    try:
        config = ConfigManager()
        
        click.echo("📋 当前配置:\n")
        
        # 阿里云配置
        aliyun_config = config.get_aliyun_config()
        click.echo("【阿里云OSS配置】")
        click.echo(f"  AccessKey ID: {aliyun_config['access_key_id'][:8]}...")
        click.echo(f"  Endpoint: {aliyun_config['endpoint']}")
        click.echo(f"  Bucket: {aliyun_config['bucket_name']}")
        if aliyun_config.get('custom_domain'):
            click.echo(f"  自定义域名: {aliyun_config['custom_domain']}")
        
        # 上传配置
        upload_config = config.get_upload_config()
        click.echo("\n【上传配置】")
        click.echo(f"  路径前缀: {upload_config.get('path_prefix', '')}")
        click.echo(f"  命名规则: {upload_config.get('naming_rule', 'uuid')}")
        click.echo(f"  MD5去重: {'启用' if upload_config.get('enable_md5_check') else '禁用'}")
        click.echo(f"  并发数: {upload_config.get('concurrent_limit', 5)}")
        
        click.echo(f"\n配置文件位置: {config.config_path}")
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@config_cmd.command('test')
def config_test():
    """测试OSS连接"""
    try:
        config = ConfigManager()
        uploader = ImageUploader(config)
        
        click.echo("🔍 正在测试OSS连接...")
        
        if uploader.check_connection():
            click.echo("✅ 连接成功！")
            
            # 获取bucket信息
            info = uploader.bucket.get_bucket_info()
            click.echo(f"\n📦 Bucket信息:")
            click.echo(f"  名称: {info.name}")
            click.echo(f"  区域: {info.location}")
            click.echo(f"  创建时间: {info.creation_date}")
        else:
            click.echo("❌ 连接失败，请检查配置", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--prefix', default='', help='对象前缀')
@click.option('--limit', default=20, help='显示数量')
def list_files(prefix, limit):
    """列出OSS中的图片文件"""
    try:
        config = ConfigManager()
        uploader = ImageUploader(config)
        
        click.echo(f"📋 列出文件 (前缀: {prefix or '全部'})\n")
        
        objects = uploader.list_objects(prefix, limit)
        
        if not objects:
            click.echo("未找到文件")
            return
        
        # 格式化输出
        table_data = []
        for obj in objects:
            table_data.append([
                obj['key'][-50:],  # 只显示最后50个字符
                format_size(obj['size']),
                obj['last_modified'],
            ])
        
        headers = ['文件名', '大小', '最后修改时间']
        click.echo(tabulate(table_data, headers=headers, tablefmt='simple'))
        click.echo(f"\n共 {len(objects)} 个文件")
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('oss_key')
@click.confirmation_option(prompt='确定要删除此文件吗？')
def delete(oss_key):
    """删除OSS中的文件"""
    try:
        config = ConfigManager()
        uploader = ImageUploader(config)
        
        if uploader.delete_object(oss_key):
            click.echo(f"✅ 文件已删除: {oss_key}")
        else:
            click.echo(f"❌ 删除失败", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


# 将 config 子命令组注册到主CLI
cli.add_command(config_cmd, name='config')


def main():
    """主入口函数"""
    cli()


if __name__ == '__main__':
    main()

