# 阿里云OSS图床系统

> 基于阿里云OSS的Markdown图床解决方案，一键将本地图片转换为图床链接

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

## ✨ 特性

- 🚀 **一键上传**：将本地图片快速上传到阿里云OSS
- 📝 **自动转换**：自动将Markdown文档中的本地图片转换为图床链接
- 🔄 **批量处理**：支持批量上传和批量文档处理
- 💰 **成本低廉**：阿里云OSS按量计费，个人使用月费约1-5元
- 🔒 **安全可靠**：配置文件加密存储，支持MD5去重
- 🎨 **命令行工具**：提供友好的CLI命令，操作简单

## 📦 安装

```bash
# 克隆项目
git clone https://github.com/xxx/aliyun-oss-image-bed.git
cd aliyun-oss-image-bed

# 安装依赖
pip install -r requirements.txt

# 安装命令行工具（可选）
pip install -e .
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd aliyun-oss-image-bed
pip install -r requirements.txt
pip install -e .
```

### 2. 配置 OSS 信息

编辑项目根目录的 `config.yaml` 文件，填写你的阿里云 AccessKey：

```bash
vim config.yaml
```

填写以下必填项：
- `aliyun.access_key_id` - 你的 AccessKey ID
- `aliyun.access_key_secret` - 你的 AccessKey Secret

其他配置（endpoint, bucket_name）已为你预设好。

📖 详细配置步骤请查看：[快速配置指南.md](快速配置指南.md)

### 3. 测试连接

```bash
# 方式1：使用命令行工具
oss-image config test

# 方式2：运行测试脚本
python example_test.py
```

### 4. 开始使用

```bash
# 上传单张图片
oss-image upload /path/to/image.png

# 批量上传
oss-image upload-batch /path/to/images/

# 处理Markdown文档（自动上传本地图片并替换链接）
oss-image convert README.md

# 处理整个文件夹
oss-image convert docs/
```

## 📖 文档

- [快速配置指南](快速配置指南.md) - ⭐ 5分钟快速上手
- [使用指南](USAGE.md) - 详细使用说明
- [PRD文档](docs/PRD.md) - 产品需求文档
- [项目结构](docs/PROJECT_STRUCTURE.md) - 项目架构说明

## 🎯 使用场景

### 场景1：上传单张图片获取链接

```bash
$ oss-image upload screenshot.png

✅ 上传成功！
URL: https://your-bucket.oss-cn-beijing.aliyuncs.com/images/2025/11/xxxx.png
Markdown: ![image](https://your-bucket.oss-cn-beijing.aliyuncs.com/images/2025/11/xxxx.png)

📋 Markdown链接已复制到剪贴板
```

### 场景2：批量处理Markdown文档

```bash
$ oss-image convert docs/

🔍 扫描文档...
📁 找到 5 个Markdown文件

处理 docs/README.md...
  ✅ 上传 3 张图片
  
处理 docs/guide.md...
  ✅ 上传 5 张图片
  
✨ 完成！共处理 8 张图片
```

### 场景3：Python SDK使用

```python
from oss_image_bed import OSSImageBed

# 初始化
client = OSSImageBed(config_path='~/.oss_image_bed/config.yaml')

# 上传图片
result = client.upload_image('screenshot.png')
print(result['markdown'])  # ![image](https://...)

# 处理Markdown文档
report = client.process_markdown('README.md')
print(f"处理完成：{report['processed_images']} 张图片")
```

## 🛠️ 项目结构

```
aliyun-oss-image-bed/
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── setup.py              # 安装脚本
├── docs/                 # 文档目录
│   └── PRD.md           # 产品需求文档
├── src/                  # 源代码
│   ├── __init__.py
│   ├── uploader.py      # 图片上传模块
│   ├── processor.py     # Markdown处理模块
│   ├── config.py        # 配置管理
│   └── cli.py           # 命令行工具
├── config/               # 配置文件模板
│   └── config.yaml.template
├── scripts/              # 辅助脚本
│   └── install.sh
└── tests/               # 测试代码
    ├── test_uploader.py
    └── test_processor.py
```

## 💡 配置说明

配置文件位于项目根目录 `config.yaml`

**必填配置：**
```yaml
aliyun:
  access_key_id: "your-access-key-id"      # 在阿里云 RAM 控制台获取
  access_key_secret: "your-access-key-secret"  # 在阿里云 RAM 控制台获取
  endpoint: "oss-cn-guangzhou.aliyuncs.com"    # 已配置
  bucket_name: "rickzo"                         # 已配置
```

**可选配置：**
```yaml
upload:
  path_prefix: "images/{year}/{month}/"  # 上传路径
  naming_rule: "uuid"                     # 文件命名规则
  enable_md5_check: true                  # MD5去重
  concurrent_limit: 5                     # 并发数
```

详细配置说明请查看 [USAGE.md](USAGE.md#高级配置)

## 📊 费用说明

阿里云OSS费用由存储、流量和请求次数组成：

| 使用场景 | 存储量 | 月访问量 | 预估月费用 |
|---------|--------|----------|-----------|
| 个人博客 | 100MB | 1000次 | 1-2元 |
| 技术博主 | 500MB | 5000次 | 5-6元 |
| 团队使用 | 2GB | 20000次 | 20-30元 |

详细费用估算请查看 [PRD文档](docs/PRD.md#9-费用估算)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [阿里云OSS](https://www.aliyun.com/product/oss) - 提供稳定的对象存储服务
- [Click](https://click.palletsprojects.com/) - 优秀的CLI框架
- 感谢所有贡献者

## 📮 联系方式

- 项目主页：https://github.com/xxx/aliyun-oss-image-bed
- 问题反馈：https://github.com/xxx/aliyun-oss-image-bed/issues

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
