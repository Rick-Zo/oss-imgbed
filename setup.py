from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aliyun-oss-image-bed",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于阿里云OSS的Markdown图床解决方案",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aliyun-oss-image-bed",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "oss-image=oss_image_bed.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
