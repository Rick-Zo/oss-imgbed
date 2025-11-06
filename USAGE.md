# 使用指南

## 📋 快速开始

### 第一步：配置阿里云OSS

你已经购买了阿里云OSS并创建了用户，现在需要填写配置信息。

#### 1. 编辑配置文件

打开项目根目录的 `config.yaml` 文件，填写以下信息：

```yaml
aliyun:
  # 填写你的 AccessKey ID
  access_key_id: "你的AccessKey ID"
  
  # 填写你的 AccessKey Secret
  access_key_secret: "你的AccessKey Secret"
  
  # OSS区域节点（已为你配置为广州）
  endpoint: "oss-cn-guangzhou.aliyuncs.com"
  
  # Bucket名称（已为你配置）
  bucket_name: "rickzo"
```

**在哪里找到 AccessKey？**

1. 登录 [阿里云控制台](https://ram.console.aliyun.com/users)
2. 进入 RAM 访问控制 → 用户管理
3. 找到你创建的用户，点击用户名
4. 选择"认证管理"标签
5. 查看或创建 AccessKey

#### 2. 配置 Bucket 权限

确保你的 Bucket 具有以下权限设置：

- **读写权限**：公共读（推荐）或 私有（需要签名URL）
- **跨域设置**（如果需要在网页中使用）：
  - 来源：`*`
  - 允许 Methods：`GET, POST, PUT`
  - 允许 Headers：`*`

你可以在这里配置：https://oss.console.aliyun.com/bucket/oss-cn-guangzhou/rickzo/permission/acl

### 第二步：测试连接

配置完成后，测试 OSS 连接是否正常：

```bash
cd /Users/rick/Documents/AI产品开发/aliyun-oss-image-bed
oss-image config test
```

如果显示 ✅ 连接成功，说明配置正确！

### 第三步：开始使用

#### 上传单张图片

```bash
# 上传图片并获取 Markdown 链接
oss-image upload /path/to/your/image.png

# 输出示例：
# ✅ 上传成功！
# 📍 URL: https://rickzo.oss-cn-guangzhou.aliyuncs.com/images/2025/11/xxx.png
# 📋 Markdown: ![image](https://rickzo.oss-cn-guangzhou.aliyuncs.com/images/2025/11/xxx.png)
# ✨ Markdown链接已复制到剪贴板
```

#### 批量上传图片

```bash
# 上传整个文件夹的图片
oss-image upload-batch /path/to/images/

# 递归上传（包含子文件夹）
oss-image upload-batch /path/to/images/ --recursive
```

#### 处理 Markdown 文档

自动上传 Markdown 文档中的本地图片并替换为图床链接：

```bash
# 处理单个文件
oss-image convert README.md

# 处理整个文件夹
oss-image convert docs/
```

**处理前的 Markdown：**
```markdown
![本地图片](./images/screenshot.png)
```

**处理后的 Markdown：**
```markdown
![本地图片](https://rickzo.oss-cn-guangzhou.aliyuncs.com/images/2025/11/xxx.png)
```

### 第四步：在 Python 中使用

你也可以在 Python 代码中使用：

```python
from oss_image_bed import ConfigManager, ImageUploader, MarkdownProcessor

# 初始化（会自动查找项目根目录的 config.yaml）
config = ConfigManager()
uploader = ImageUploader(config)

# 上传图片
result = uploader.upload_single('screenshot.png')
if result['success']:
    print(f"URL: {result['url']}")
    print(f"Markdown: {result['markdown']}")

# 处理 Markdown 文档
processor = MarkdownProcessor(uploader)
report = processor.process_file('README.md')
print(f"处理了 {report['processed_images']} 张图片")
```

## 🔧 高级配置

### 自定义上传路径

编辑 `config.yaml`：

```yaml
upload:
  # 使用日期分类
  path_prefix: "images/{year}/{month}/"
  
  # 或按类型分类
  path_prefix: "blog/tech/"
  
  # 或存储到根目录
  path_prefix: ""
```

### 自定义文件命名

```yaml
upload:
  # UUID命名（推荐，避免冲突）
  naming_rule: "uuid"
  
  # 时间戳命名
  naming_rule: "timestamp"
  
  # 保持原文件名
  naming_rule: "original"
```

### 启用 MD5 去重

避免重复上传相同的图片：

```yaml
upload:
  enable_md5_check: true  # 相同图片不会重复上传
```

### 使用自定义域名

如果你为 OSS Bucket 绑定了自定义域名：

```yaml
aliyun:
  custom_domain: "https://img.yourdomain.com"
```

## 📚 常用命令

```bash
# 查看配置
oss-image config show

# 测试连接
oss-image config test

# 列出已上传的文件
oss-image list-files

# 列出特定前缀的文件
oss-image list-files --prefix "images/2025/"

# 删除文件
oss-image delete images/2025/11/xxx.png

# 查看帮助
oss-image --help
oss-image upload --help
```

## ⚠️ 注意事项

### 1. 配置文件安全

`config.yaml` 包含敏感信息（AccessKey），请注意：

- ✅ 已添加到 `.gitignore`，不会被 git 提交
- ❌ 不要将配置文件分享给他人
- ❌ 不要上传到公开的代码仓库

### 2. 费用控制

阿里云 OSS 按量计费，建议：

- 设置费用预警
- 定期清理不用的图片
- 考虑开启 CDN 加速降低流量费用

个人博客预计费用：**1-5 元/月**

### 3. Bucket 权限设置

- **公共读**：图片可直接访问（推荐）
- **私有**：需要通过签名 URL 访问（更安全，但链接有时效）

### 4. 图片备份

建议定期备份重要图片，可以使用：

```bash
# 使用 ossutil 工具下载
ossutil cp -r oss://rickzo/images/ ./backup/
```

## 🐛 常见问题

### Q1: 提示 "配置文件不存在"

**原因**：配置文件路径不正确

**解决**：
1. 确保在项目根目录运行命令
2. 或者使用绝对路径指定配置文件：
   ```bash
   oss-image --config /path/to/config.yaml upload image.png
   ```

### Q2: 上传失败 "权限不足"

**原因**：AccessKey 权限不足

**解决**：
1. 在阿里云 RAM 控制台检查用户权限
2. 确保用户有 OSS 读写权限
3. 检查 Bucket 的访问控制设置

### Q3: 图片链接无法访问

**原因**：Bucket 权限设置为私有

**解决**：
1. 将 Bucket 权限改为"公共读"
2. 或在代码中生成签名 URL（暂不支持）

### Q4: Markdown 链接被复制但无法粘贴

**原因**：未安装剪贴板工具

**解决**：
```bash
pip install pyperclip
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件：`logs/app.log`
2. 使用 `--help` 查看命令帮助
3. 查看 [PRD 文档](docs/PRD.md)

## 🎉 下一步

现在你可以：

1. ✅ 开始上传图片到 OSS
2. ✅ 将本地 Markdown 文档转换为图床链接
3. ✅ 在你的博客中使用稳定的图片链接
4. ✅ 享受低成本、高可靠的图床服务

祝你使用愉快！ 🚀

