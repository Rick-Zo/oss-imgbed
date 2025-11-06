#!/usr/bin/env python3
"""
示例测试脚本
用于验证配置和测试基本功能
"""

from oss_image_bed import ConfigManager, ImageUploader

def main():
    print("=" * 60)
    print("阿里云 OSS 图床配置测试")
    print("=" * 60)
    
    # 1. 测试配置加载
    print("\n[1/3] 测试配置加载...")
    try:
        config = ConfigManager()
        print(f"✅ 配置文件加载成功: {config.config_path}")
        
        aliyun_config = config.get_aliyun_config()
        print(f"   - Endpoint: {aliyun_config['endpoint']}")
        print(f"   - Bucket: {aliyun_config['bucket_name']}")
        print(f"   - AccessKey ID: {aliyun_config['access_key_id'][:8]}...")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    # 2. 测试 OSS 连接
    print("\n[2/3] 测试 OSS 连接...")
    try:
        uploader = ImageUploader(config)
        
        if uploader.check_connection():
            print("✅ OSS 连接成功")
            
            # 获取 bucket 信息
            info = uploader.bucket.get_bucket_info()
            print(f"   - Bucket 名称: {info.name}")
            print(f"   - 区域: {info.location}")
            print(f"   - 创建时间: {info.creation_date}")
        else:
            print("❌ OSS 连接失败")
            return False
    except Exception as e:
        print(f"❌ OSS 连接失败: {e}")
        return False
    
    # 3. 列出已上传的文件（前5个）
    print("\n[3/3] 查看已上传文件（最近5个）...")
    try:
        objects = uploader.list_objects(prefix='', max_keys=5)
        if objects:
            print(f"✅ 找到 {len(objects)} 个文件:")
            for obj in objects:
                size_kb = obj['size'] / 1024
                print(f"   - {obj['key']} ({size_kb:.1f} KB)")
        else:
            print("   ℹ️  暂无已上传的文件")
    except Exception as e:
        print(f"⚠️  无法列出文件: {e}")
    
    print("\n" + "=" * 60)
    print("✨ 所有测试通过！配置正确，可以开始使用了！")
    print("=" * 60)
    
    print("\n💡 快速开始：")
    print("   1. 上传图片:      oss-image upload image.png")
    print("   2. 批量上传:      oss-image upload-batch ./images/")
    print("   3. 处理文档:      oss-image convert README.md")
    print("   4. 查看帮助:      oss-image --help")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        exit(1)

