# 项目结构说明

## 📁 目录结构

```
aliyun-oss-image-bed/
├── .gitignore                    # Git忽略文件配置
├── README.md                     # 项目说明文档
├── LICENSE                       # 开源许可证
├── requirements.txt              # Python依赖列表
├── setup.py                      # 项目安装配置
│
├── docs/                         # 📚 文档目录
│   ├── PRD.md                   # 产品需求文档
│   ├── PROJECT_STRUCTURE.md     # 项目结构说明（本文件）
│   ├── API.md                   # API使用文档（待创建）
│   ├── CONFIGURATION.md         # 配置指南（待创建）
│   └── FAQ.md                   # 常见问题（待创建）
│
├── config/                       # ⚙️ 配置文件目录
│   └── config.yaml.template     # 配置文件模板
│
├── src/                          # 💻 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── uploader.py              # 图片上传模块
│   ├── processor.py             # Markdown处理模块
│   ├── config.py                # 配置管理模块
│   ├── cli.py                   # 命令行工具
│   ├── utils.py                 # 工具函数
│   └── exceptions.py            # 自定义异常
│
├── scripts/                      # 🔧 辅助脚本目录
│   ├── install.sh               # 安装脚本
│   └── migrate.py               # 数据迁移脚本
│
└── tests/                        # 🧪 测试代码目录
    ├── __init__.py
    ├── test_uploader.py         # 上传模块测试
    ├── test_processor.py        # 处理模块测试
    ├── test_config.py           # 配置模块测试
    └── fixtures/                # 测试数据
        ├── test_images/         # 测试图片
        └── test_markdown/       # 测试Markdown文件
```

## 📄 核心文件说明

### 项目根目录

| 文件 | 说明 |
|------|------|
| README.md | 项目主要说明文档，包含快速开始、使用示例等 |
| requirements.txt | Python依赖包列表，用于`pip install -r requirements.txt` |
| setup.py | Python包安装配置，支持`pip install -e .`开发模式安装 |
| .gitignore | Git版本控制忽略文件配置 |
| LICENSE | 开源许可证（MIT） |

### docs/ 文档目录

| 文件 | 说明 | 状态 |
|------|------|------|
| PRD.md | 产品需求文档，详细描述功能需求和技术方案 | ✅ 已完成 |
| PROJECT_STRUCTURE.md | 项目结构说明文档 | ✅ 已完成 |
| API.md | Python SDK API使用文档 | 📋 待创建 |
| CONFIGURATION.md | 详细配置说明和最佳实践 | 📋 待创建 |
| FAQ.md | 常见问题解答 | 📋 待创建 |

### src/ 源代码目录

#### src/__init__.py
包初始化文件，导出主要API

```python
from .uploader import ImageUploader
from .processor import MarkdownProcessor
from .config import Config

__version__ = "1.0.0"
__all__ = ["ImageUploader", "MarkdownProcessor", "Config"]
```

#### src/uploader.py
图片上传核心模块

**主要类和方法**：
```python
class ImageUploader:
    def __init__(self, config)
    def upload_single(self, local_path: str) -> dict
    def upload_batch(self, image_paths: List[str]) -> List[dict]
    def delete_image(self, oss_key: str) -> bool
    def list_images(self, prefix: str = "") -> List[dict]
```

#### src/processor.py
Markdown文档处理模块

**主要类和方法**：
```python
class MarkdownProcessor:
    def __init__(self, uploader: ImageUploader)
    def process_file(self, md_path: str) -> dict
    def process_directory(self, dir_path: str) -> dict
    def _extract_local_images(self, content: str) -> List[str]
    def _replace_image_links(self, content: str, replacements: dict) -> str
```

#### src/config.py
配置管理模块

**主要类和方法**：
```python
class Config:
    def __init__(self, config_path: str = None)
    def load(self) -> dict
    def save(self, config: dict) -> None
    def get(self, key: str, default=None)
    def set(self, key: str, value) -> None
    def validate(self) -> bool
```

#### src/cli.py
命令行工具入口

**主要命令**：
- `oss-image init` - 初始化配置
- `oss-image upload <path>` - 上传图片
- `oss-image upload-batch <dir>` - 批量上传
- `oss-image convert <file>` - 处理Markdown
- `oss-image config` - 配置管理
- `oss-image list` - 列出图片
- `oss-image stats` - 查看统计

#### src/utils.py
工具函数模块

**主要函数**：
```python
def calculate_md5(file_path: str) -> str
def generate_uuid_filename(original_name: str) -> str
def is_image_file(file_path: str) -> bool
def format_file_size(size_bytes: int) -> str
def ensure_dir(dir_path: str) -> None
```

#### src/exceptions.py
自定义异常类

```python
class OSSImageBedException(Exception):
    """基础异常类"""

class ConfigError(OSSImageBedException):
    """配置错误"""

class UploadError(OSSImageBedException):
    """上传失败"""

class ProcessError(OSSImageBedException):
    """处理失败"""
```

### config/ 配置目录

| 文件 | 说明 |
|------|------|
| config.yaml.template | 配置文件模板，包含所有配置项的说明 |

实际使用时，配置文件位于：`~/.oss_image_bed/config.yaml`

### scripts/ 脚本目录

| 文件 | 说明 | 用途 |
|------|------|------|
| install.sh | 安装脚本 | 一键安装和配置 |
| migrate.py | 迁移脚本 | 数据迁移和升级 |

### tests/ 测试目录

| 文件/目录 | 说明 |
|----------|------|
| test_uploader.py | 上传模块单元测试 |
| test_processor.py | 处理模块单元测试 |
| test_config.py | 配置模块单元测试 |
| fixtures/ | 测试数据和资源 |

## 🔄 数据流转

### 图片上传流程

```
本地图片
    ↓
ImageUploader.upload_single()
    ↓
计算MD5 → 检查缓存
    ↓
生成OSS Key
    ↓
调用OSS SDK上传
    ↓
返回图片URL和Markdown链接
```

### Markdown处理流程

```
Markdown文件
    ↓
MarkdownProcessor.process_file()
    ↓
提取本地图片路径
    ↓
ImageUploader批量上传
    ↓
替换图片链接
    ↓
保存更新后的文件
```

## 🔌 扩展点

### 1. 支持新的云存储服务

在`src/uploader.py`中实现新的上传器类：

```python
class TencentCOSUploader(BaseUploader):
    """腾讯云COS上传器"""
    pass

class QiniuUploader(BaseUploader):
    """七牛云上传器"""
    pass
```

### 2. 添加图片处理功能

在`src/processor.py`中添加图片处理：

```python
class ImageProcessor:
    """图片处理器"""
    
    def compress(self, image_path: str) -> str:
        """压缩图片"""
        pass
    
    def watermark(self, image_path: str, text: str) -> str:
        """添加水印"""
        pass
```

### 3. Web界面

创建`src/web/`目录，使用Flask/FastAPI构建Web管理界面

## 📦 打包发布

### 本地开发安装

```bash
# 开发模式安装（可编辑）
pip install -e .

# 运行测试
pytest tests/

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/
```

### 打包发布到PyPI

```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 上传到PyPI（需要账号）
twine upload dist/*
```

## 🛠️ 开发指南

### 添加新功能

1. 在相应模块中实现功能
2. 编写单元测试
3. 更新文档
4. 提交Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 使用type hints类型注解
- 编写清晰的docstring文档
- 保持函数简洁（不超过50行）

### 提交规范

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建/工具变动
```

## 📚 相关文档

- [产品需求文档](PRD.md)
- [阿里云OSS文档](https://help.aliyun.com/document_detail/31883.html)
- [Click框架文档](https://click.palletsprojects.com/)
- [Python打包指南](https://packaging.python.org/)

---

最后更新：2025-11-05
