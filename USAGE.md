# 使用文档

## 目录
- [快速开始](#快速开始)
- [基本用法](#基本用法)
- [高级配置](#高级配置)
- [API参考](#api参考)
- [示例代码](#示例代码)
- [最佳实践](#最佳实践)

## 快速开始

### 1. 环境准备

确保您的系统满足以下要求：
- Python 3.8 或更高版本
- 至少 2GB 可用内存
- 稳定的网络连接

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/vistaminc/aliyun-cve-crawler.git
cd aliyun-cve-crawler

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装浏览器驱动
playwright install chromium
```

### 3. 第一次运行

```bash
# 爬取前3页数据进行测试
python main.py --pages 3
```

## 基本用法

### 命令行接口

```bash
# 基本爬取
python main.py --pages 10                    # 爬取前10页
python main.py --pages 5 --start-page 3      # 从第3页开始爬取5页

# 增量爬取
python main.py --incremental                 # 爬取最近7天数据
python main.py --incremental --days 3        # 爬取最近3天数据

# 调试模式
python main.py --pages 3 --no-headless       # 显示浏览器界面
```

### Python API

#### 简单爬取

```python
import asyncio
from main import crawl_aliyun_cves

async def simple_crawl():
    # 爬取前5页数据
    cve_infos = await crawl_aliyun_cves(max_pages=5)
    
    print(f"成功爬取 {len(cve_infos)} 个CVE")
    
    # 显示前3个结果
    for i, cve in enumerate(cve_infos[:3]):
        print(f"\n{i+1}. {cve.cve_id}")
        print(f"   严重性: {cve.severity}")
        print(f"   CVSS: {cve.cvss_score}")
        print(f"   描述: {cve.description[:100]}...")

# 运行
asyncio.run(simple_crawl())
```

#### 增量爬取

```python
import asyncio
from datetime import datetime, timedelta
from main import crawl_aliyun_cves_incremental

async def incremental_crawl():
    # 爬取最近7天的数据
    new_cves = await crawl_aliyun_cves_incremental(days=7)
    
    if new_cves:
        print(f"发现 {len(new_cves)} 个新CVE")
        
        # 按严重性分类
        critical = [cve for cve in new_cves if cve.severity == "CRITICAL"]
        high = [cve for cve in new_cves if cve.severity == "HIGH"]
        
        print(f"严重: {len(critical)}, 高危: {len(high)}")
    else:
        print("没有发现新的CVE")

asyncio.run(incremental_crawl())
```

## 高级配置

### 自定义爬虫配置

```python
from main import AliyunCVECrawler, CrawlConfig

# 创建自定义配置
config = CrawlConfig(
    # 爬取设置
    max_pages=50,              # 最大页数
    delay_range=(2, 5),        # 请求间隔2-5秒
    timeout=60,                # 页面超时60秒
    
    # 浏览器设置
    headless=True,             # 无头模式
    user_agent="Custom-Agent", # 自定义User-Agent
    
    # 存储设置
    data_dir="./my_data",      # 自定义数据目录
    cache_ttl=3600             # 缓存1小时
)

async def custom_crawl():
    async with AliyunCVECrawler(config) as crawler:
        # 爬取数据
        cve_infos = await crawler.crawl_all(start_page=1, max_pages=10)
        
        # 获取统计信息
        metrics = crawler.get_metrics()
        print(f"爬取统计: {metrics}")
        
        return cve_infos
```

### 错误处理和重试

```python
import asyncio
from main import AliyunCVECrawler, CrawlConfig

async def robust_crawl():
    config = CrawlConfig(
        max_pages=20,
        delay_range=(3, 6),  # 增加延迟减少被限制的可能
        timeout=90           # 增加超时时间
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with AliyunCVECrawler(config) as crawler:
                cve_infos = await crawler.crawl_all()
                print(f"成功爬取 {len(cve_infos)} 个CVE")
                return cve_infos
                
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                print("等待30秒后重试...")
                await asyncio.sleep(30)
            else:
                print("所有重试都失败了")
                raise

asyncio.run(robust_crawl())
```

## API参考

### CrawlConfig 类

配置爬虫行为的参数类。

```python
@dataclass
class CrawlConfig:
    base_url: str = "https://avd.aliyun.com"
    list_url: str = "https://avd.aliyun.com/nvd/list"
    detail_url_template: str = "https://avd.aliyun.com/detail?id={}"
    
    # 爬取配置
    max_pages: int = 100        # 最大爬取页数
    page_size: int = 30         # 每页条目数
    delay_range: tuple = (1, 3) # 请求间隔范围（秒）
    timeout: int = 30           # 页面加载超时
    
    # 浏览器配置
    headless: bool = True       # 是否无头模式
    user_agent: str = "..."     # User-Agent字符串
    
    # 数据存储
    data_dir: str = "./data/aliyun_cve"  # 数据目录
    cache_ttl: int = 86400      # 缓存TTL（秒）
```

### AliyunCVECrawler 类

主要的爬虫类。

#### 方法

- `crawl_all(start_page, max_pages)`: 爬取所有CVE数据
- `crawl_incremental(since_date)`: 增量爬取
- `get_metrics()`: 获取爬取统计信息

#### 使用示例

```python
async with AliyunCVECrawler(config) as crawler:
    # 全量爬取
    all_cves = await crawler.crawl_all(start_page=1, max_pages=10)
    
    # 增量爬取
    since_date = datetime.now() - timedelta(days=7)
    new_cves = await crawler.crawl_incremental(since_date)
    
    # 获取统计
    stats = crawler.get_metrics()
```

### 便捷函数

#### crawl_aliyun_cves()

```python
async def crawl_aliyun_cves(max_pages: int = 10, 
                           start_page: int = 1,
                           headless: bool = True) -> List[CVEInfo]
```

快速爬取CVE数据的便捷函数。

#### crawl_aliyun_cves_incremental()

```python
async def crawl_aliyun_cves_incremental(days: int = 7) -> List[CVEInfo]
```

快速进行增量爬取的便捷函数。

## 示例代码

### 示例1：批量爬取并分析

```python
import asyncio
from collections import Counter
from main import crawl_aliyun_cves

async def analyze_cves():
    # 爬取数据
    cves = await crawl_aliyun_cves(max_pages=10)
    
    # 统计分析
    severity_count = Counter(cve.severity for cve in cves)
    print("严重性分布:")
    for severity, count in severity_count.items():
        print(f"  {severity}: {count}")
    
    # 找出高危漏洞
    high_risk = [cve for cve in cves if cve.cvss_score >= 7.0]
    print(f"\n高危漏洞 (CVSS >= 7.0): {len(high_risk)}")
    
    # 显示最新的5个高危漏洞
    high_risk.sort(key=lambda x: x.published_date, reverse=True)
    print("\n最新高危漏洞:")
    for cve in high_risk[:5]:
        print(f"  {cve.cve_id} - {cve.severity} - CVSS: {cve.cvss_score}")

asyncio.run(analyze_cves())
```

### 示例2：定期监控

```python
import asyncio
import schedule
import time
from datetime import datetime
from main import crawl_aliyun_cves_incremental

async def daily_monitor():
    """每日监控新漏洞"""
    print(f"[{datetime.now()}] 开始每日CVE监控...")
    
    try:
        new_cves = await crawl_aliyun_cves_incremental(days=1)
        
        if new_cves:
            critical_cves = [cve for cve in new_cves if cve.severity == "CRITICAL"]
            
            print(f"发现 {len(new_cves)} 个新CVE")
            if critical_cves:
                print(f"⚠️  发现 {len(critical_cves)} 个严重漏洞!")
                for cve in critical_cves:
                    print(f"  - {cve.cve_id}: {cve.description[:100]}...")
        else:
            print("没有发现新CVE")
            
    except Exception as e:
        print(f"监控失败: {e}")

def run_monitor():
    """运行监控任务"""
    asyncio.run(daily_monitor())

# 设置定时任务
schedule.every().day.at("09:00").do(run_monitor)

print("CVE监控服务已启动，每天09:00执行检查...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 最佳实践

### 1. 合理设置爬取频率

```python
# 推荐配置
config = CrawlConfig(
    delay_range=(2, 5),  # 2-5秒随机延迟
    timeout=60,          # 足够的超时时间
    max_pages=20         # 适中的页数
)
```

### 2. 错误处理

```python
async def safe_crawl():
    try:
        cves = await crawl_aliyun_cves(max_pages=10)
        return cves
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        # 可以选择返回空列表或重新抛出异常
        return []
```

### 3. 数据验证

```python
def validate_cve_data(cves):
    """验证CVE数据质量"""
    valid_cves = []
    
    for cve in cves:
        if (cve.cve_id and 
            cve.description and 
            cve.cvss_score > 0):
            valid_cves.append(cve)
        else:
            print(f"无效CVE数据: {cve.cve_id}")
    
    return valid_cves
```

### 4. 内存管理

```python
async def memory_efficient_crawl():
    """内存高效的爬取方式"""
    config = CrawlConfig(max_pages=5)  # 分批处理
    
    all_cves = []
    for batch_start in range(1, 21, 5):  # 每次5页，总共20页
        batch_cves = await crawl_aliyun_cves(
            max_pages=5, 
            start_page=batch_start
        )
        all_cves.extend(batch_cves)
        
        # 可选：保存中间结果
        print(f"已处理 {len(all_cves)} 个CVE")
    
    return all_cves
```

### 5. 日志记录

```python
from loguru import logger

# 配置日志
logger.add("crawl.log", rotation="1 day", retention="30 days")

async def logged_crawl():
    logger.info("开始CVE爬取任务")
    
    try:
        cves = await crawl_aliyun_cves(max_pages=10)
        logger.success(f"成功爬取 {len(cves)} 个CVE")
        return cves
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        raise
```

这些示例和最佳实践可以帮助您更好地使用阿里云CVE爬虫工具。根据您的具体需求调整配置和使用方式。
