# 阿里云漏洞库爬虫 (AliyunCVE_Crawler)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个高效的阿里云漏洞库爬虫工具，用于自动化爬取和处理CVE（Common Vulnerabilities and Exposures）数据。

## 🚀 功能特性

- **批量爬取**: 支持批量爬取阿里云漏洞库的CVE数据
- **增量更新**: 支持增量爬取，只获取指定日期后的新漏洞
- **详细信息**: 提取完整的CVE详情，包括描述、解决方案、CVSS评分等
- **数据标准化**: 自动转换为标准CVEInfo格式，便于后续处理
- **并发处理**: 支持异步并发爬取，提高效率
- **智能重试**: 内置错误处理和重试机制
- **数据持久化**: 自动保存爬取结果到JSON文件
- **性能监控**: 提供详细的爬取统计和性能指标
- **🎨 现代GUI**: 基于ttkbootstrap的现代化图形界面
- **📊 数据可视化**: 实时统计和结果展示
- **⚙️ 可视化配置**: 直观的参数设置和管理
- **⏹️ 安全停止**: 支持爬取过程中的安全中断和停止

## 📋 系统要求

- Python 3.8+
- Windows/Linux/macOS
- 至少 2GB 可用内存
- 稳定的网络连接

## 🛠️ 安装

### 1. 克隆项目

```bash
git clone https://github.com/vistaminc/AliyunCVE_Crawler.git
cd AliyunCVE_Crawler
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装浏览器驱动

```bash
playwright install chromium
```

## 📖 快速开始

### 🎨 图形界面（推荐）

```bash
# 启动现代化GUI界面
python run_gui.py
```

![GUI界面截图](src/界面.png)

GUI界面提供：
- 🖱️ 直观的点击操作
- 📊 实时数据展示
- ⚙️ 可视化配置管理
- 📈 爬取进度监控
- 💾 一键导出功能

详细使用说明请参考：[GUI使用指南](docs/GUI_USAGE.md)

### 💻 命令行使用

```bash
# 爬取前10页数据
python main.py --pages 10

# 从第5页开始爬取10页
python main.py --pages 10 --start-page 5

# 增量爬取最近7天的数据
python main.py --incremental --days 7

# 显示浏览器界面（调试模式）
python main.py --pages 5 --no-headless
```

### 🐍 Python API

```python
import asyncio
from main import crawl_aliyun_cves

async def main():
    # 爬取前5页的CVE数据
    cve_infos = await crawl_aliyun_cves(max_pages=5)
    print(f"成功爬取 {len(cve_infos)} 个CVE")

asyncio.run(main())
```

## 🔧 高级用法

### 自定义配置

```python
from main import AliyunCVECrawler, CrawlConfig

# 创建自定义配置
config = CrawlConfig(
    max_pages=20,
    delay_range=(2, 5),  # 请求间隔2-5秒
    timeout=60,          # 页面超时60秒
    headless=False,      # 显示浏览器
    data_dir="./custom_data"  # 自定义数据目录
)

# 使用自定义配置
async def custom_crawl():
    async with AliyunCVECrawler(config) as crawler:
        cve_infos = await crawler.crawl_all(start_page=1, max_pages=10)
        return cve_infos
```

### 增量爬取

```python
from datetime import datetime, timedelta
from main import AliyunCVECrawler

async def incremental_crawl():
    # 爬取最近3天的数据
    since_date = datetime.now() - timedelta(days=3)
    
    async with AliyunCVECrawler() as crawler:
        new_cves = await crawler.crawl_incremental(since_date)
        print(f"发现 {len(new_cves)} 个新CVE")
        return new_cves
```

## 📊 数据格式

### CVE详情数据结构

```python
{
    "cve_id": "CVE-2024-1234",
    "title": "漏洞标题",
    "description": "漏洞描述",
    "solution": "解决方案",
    "references": ["http://example.com/ref1"],
    "cvss_score": "7.5",
    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
    "cwe_info": [
        {"id": "CWE-79", "description": "Cross-site Scripting"}
    ],
    "disclosure_date": "2024-01-15",
    "patch_status": "已修复",
    "exploit_status": "无公开利用",
    "aliyun_products": ["云安全中心", "WAF"]
}
```

### 标准CVEInfo格式

```python
{
    "cve_id": "CVE-2024-1234",
    "description": "漏洞描述",
    "severity": "HIGH",
    "cvss_score": 7.5,
    "published_date": "2024-01-15T00:00:00",
    "modified_date": "2024-01-15T00:00:00",
    "references": ["http://example.com/ref1"],
    "affected_products": ["云安全中心", "WAF"],
    "cwe_ids": ["CWE-79"]
}
```

## 📁 输出文件

爬虫会在指定的数据目录中生成以下文件：

- `cve_details_YYYYMMDD_HHMMSS.json`: 原始CVE详情数据
- `cve_infos_YYYYMMDD_HHMMSS.json`: 标准化CVE信息
- `crawl_stats_YYYYMMDD_HHMMSS.json`: 爬取统计信息

## ⚙️ 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_pages` | int | 100 | 最大爬取页数 |
| `page_size` | int | 30 | 每页条目数 |
| `delay_range` | tuple | (1, 3) | 请求间隔范围（秒） |
| `timeout` | int | 30 | 页面加载超时（秒） |
| `headless` | bool | True | 是否无头模式 |
| `data_dir` | str | "./data/aliyun_cve" | 数据存储目录 |

## 🚨 注意事项

1. **请求频率**: 请合理设置请求间隔，避免对目标网站造成过大压力
2. **网络稳定性**: 确保网络连接稳定，避免爬取过程中断
3. **存储空间**: 大量数据爬取需要足够的磁盘空间
4. **法律合规**: 请确保爬取行为符合相关法律法规和网站使用条款

## 🐛 故障排除

### 常见问题

1. **浏览器启动失败**
   ```bash
   # 重新安装浏览器驱动
   playwright install chromium
   ```

2. **页面加载超时**
   ```python
   # 增加超时时间
   config = CrawlConfig(timeout=60)
   ```

3. **内存不足**
   ```python
   # 减少并发数或分批处理
   config = CrawlConfig(max_pages=5)
   ```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: https://github.com/vistaminc/AliyunCVE_Crawler
- 问题反馈: https://github.com/vistaminc/AliyunCVE_Crawler/issues
- 

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=vistaminc/AliyunCVE_Crawler&type=Date)](https://www.star-history.com/#)

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 提供强大的浏览器自动化能力
- [Loguru](https://github.com/Delgan/loguru) - 优雅的日志记录
- [aiofiles](https://github.com/Tinche/aiofiles) - 异步文件操作
