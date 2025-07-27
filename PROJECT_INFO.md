# 项目信息

## 项目名称
**AliyunCVE_Crawler** - 阿里云漏洞库CVE数据爬虫工具

## 项目描述
一个专业的阿里云漏洞库CVE数据爬虫工具，提供命令行和图形界面两种使用方式。

## 主要特性
- 🚀 批量爬取CVE数据
- ⚡ 增量更新支持
- 🎨 现代化GUI界面
- 📊 数据可视化展示
- ⚙️ 灵活的配置管理
- 📄 多格式数据导出

## 项目结构
```
AliyunCVE_Crawler/
├── main.py                 # 核心爬虫模块
├── gui.py                  # GUI界面
├── run_gui.py             # GUI启动器
├── create_shortcut.py     # 快捷方式创建工具
├── test_imports.py        # 模块导入测试
├── requirements.txt       # 项目依赖
├── requirements-dev.txt   # 开发依赖
├── setup.py              # 安装脚本
├── Makefile              # 项目管理工具
├── config.example.json   # 配置示例
├── gui_config.example.json # GUI配置示例
├── docs/                 # 文档目录
│   ├── API.md           # API参考文档
│   └── GUI_USAGE.md     # GUI使用指南
├── examples/            # 示例代码
│   ├── basic_usage.py   # 基本使用示例
│   └── monitoring_service.py # 监控服务示例
└── tests/               # 测试代码
    └── test_crawler.py  # 爬虫测试
```

## 快速开始

### 1. 图形界面（推荐）
```bash
python run_gui.py
```

### 2. 命令行使用
```bash
# 爬取前10页数据
python main.py --pages 10

# 增量爬取
python main.py --incremental --days 7
```

### 3. Python API
```python
import asyncio
from main import crawl_aliyun_cves

async def main():
    cves = await crawl_aliyun_cves(max_pages=5)
    print(f"获得 {len(cves)} 个CVE")

asyncio.run(main())
```

## 技术栈
- **Python 3.8+**
- **Playwright** - 浏览器自动化
- **ttkbootstrap** - 现代化GUI框架
- **asyncio** - 异步编程
- **loguru** - 日志记录

## 许可证
MIT License

## 版本历史
- v1.0.0 - 初始版本，包含完整的爬虫功能和GUI界面

## 联系方式
- 项目主页: https://github.com/vistaminc/AliyunCVE_Crawler
- 问题反馈: https://github.com/vistaminc/AliyunCVE_Crawler/issues

## 贡献
欢迎提交Issue和Pull Request！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---
*最后更新: 2025-01-27*
