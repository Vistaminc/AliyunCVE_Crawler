# API 参考文档

## 概述

本文档详细描述了阿里云CVE爬虫的所有API接口和类。

## 核心类

### CrawlConfig

爬虫配置类，用于设置爬虫的各种参数。

```python
@dataclass
class CrawlConfig:
    """爬虫配置"""
    base_url: str = "https://avd.aliyun.com"
    list_url: str = "https://avd.aliyun.com/nvd/list"
    detail_url_template: str = "https://avd.aliyun.com/detail?id={}"
    
    # 爬取配置
    max_pages: int = 100
    page_size: int = 30
    delay_range: tuple = (1, 3)
    timeout: int = 30
    
    # 浏览器配置
    headless: bool = True
    user_agent: str = "Mozilla/5.0 ..."
    
    # 数据存储
    data_dir: str = "./data/aliyun_cve"
    cache_ttl: int = 86400
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | "https://avd.aliyun.com" | 阿里云漏洞库基础URL |
| `list_url` | str | "https://avd.aliyun.com/nvd/list" | CVE列表页面URL |
| `detail_url_template` | str | "https://avd.aliyun.com/detail?id={}" | CVE详情页面URL模板 |
| `max_pages` | int | 100 | 最大爬取页数 |
| `page_size` | int | 30 | 每页条目数 |
| `delay_range` | tuple | (1, 3) | 请求间隔范围（秒） |
| `timeout` | int | 30 | 页面加载超时（秒） |
| `headless` | bool | True | 是否使用无头浏览器 |
| `user_agent` | str | "Mozilla/5.0 ..." | 浏览器User-Agent |
| `data_dir` | str | "./data/aliyun_cve" | 数据存储目录 |
| `cache_ttl` | int | 86400 | 缓存生存时间（秒） |

### CVEListItem

CVE列表项数据类。

```python
@dataclass
class CVEListItem:
    """CVE列表项"""
    cve_id: str
    title: str
    cwe_type: str
    disclosure_date: str
    cvss_score: str
    detail_url: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
```

#### 属性说明

- `cve_id`: CVE编号
- `title`: 漏洞标题
- `cwe_type`: CWE类型
- `disclosure_date`: 披露日期
- `cvss_score`: CVSS评分
- `detail_url`: 详情页面URL

### CVEDetail

CVE详细信息数据类。

```python
@dataclass
class CVEDetail:
    """CVE详细信息"""
    cve_id: str
    title: str
    description: str
    solution: str
    references: List[str] = field(default_factory=list)
    cvss_score: str = ""
    cvss_vector: str = ""
    cwe_info: List[Dict[str, str]] = field(default_factory=list)
    disclosure_date: str = ""
    patch_status: str = ""
    exploit_status: str = ""
    aliyun_products: List[str] = field(default_factory=list)
    
    def to_cve_info(self) -> CVEInfo:
        """转换为标准CVEInfo格式"""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
```

#### 方法说明

- `to_cve_info()`: 转换为标准CVEInfo格式，用于与其他系统集成
- `to_dict()`: 转换为字典格式，便于序列化

### AliyunCVECrawler

主要的爬虫类。

```python
class AliyunCVECrawler:
    """阿里云CVE爬虫"""
    
    def __init__(self, config: Optional[CrawlConfig] = None):
        """初始化爬虫"""
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
    
    async def crawl_all(self, start_page: int = 1, max_pages: Optional[int] = None) -> List[CVEInfo]:
        """爬取所有CVE数据"""
    
    async def crawl_incremental(self, since_date: Optional[datetime] = None) -> List[CVEInfo]:
        """增量爬取"""
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取爬取指标"""
```

#### 方法详解

##### `__init__(config)`

初始化爬虫实例。

**参数:**
- `config` (Optional[CrawlConfig]): 爬虫配置，如果为None则使用默认配置

**示例:**
```python
config = CrawlConfig(max_pages=10, headless=False)
crawler = AliyunCVECrawler(config)
```

##### `crawl_all(start_page, max_pages)`

爬取所有CVE数据。

**参数:**
- `start_page` (int): 起始页码，默认为1
- `max_pages` (Optional[int]): 最大页数，如果为None则使用配置中的值

**返回:**
- `List[CVEInfo]`: CVE信息列表

**异常:**
- `Exception`: 爬取过程中的各种异常

**示例:**
```python
async with AliyunCVECrawler() as crawler:
    cves = await crawler.crawl_all(start_page=1, max_pages=5)
```

##### `crawl_incremental(since_date)`

增量爬取指定日期之后的CVE。

**参数:**
- `since_date` (Optional[datetime]): 起始日期，如果为None则默认为7天前

**返回:**
- `List[CVEInfo]`: 新的CVE信息列表

**示例:**
```python
from datetime import datetime, timedelta

since_date = datetime.now() - timedelta(days=3)
async with AliyunCVECrawler() as crawler:
    new_cves = await crawler.crawl_incremental(since_date)
```

##### `get_metrics()`

获取爬取统计指标。

**返回:**
- `Dict[str, Any]`: 包含以下指标的字典
  - `pages_crawled`: 已爬取页数
  - `cves_found`: 发现的CVE数量
  - `cves_detailed`: 获取详情的CVE数量
  - `errors`: 错误数量
  - `start_time`: 开始时间
  - `end_time`: 结束时间

## 便捷函数

### crawl_aliyun_cves()

快速爬取CVE数据的便捷函数。

```python
async def crawl_aliyun_cves(max_pages: int = 10, 
                           start_page: int = 1,
                           headless: bool = True) -> List[CVEInfo]:
    """便捷的CVE爬取函数"""
```

**参数:**
- `max_pages` (int): 最大页数，默认10
- `start_page` (int): 起始页，默认1
- `headless` (bool): 是否无头模式，默认True

**返回:**
- `List[CVEInfo]`: CVE信息列表

**示例:**
```python
# 爬取前5页数据
cves = await crawl_aliyun_cves(max_pages=5)

# 从第3页开始爬取5页
cves = await crawl_aliyun_cves(max_pages=5, start_page=3)

# 显示浏览器界面
cves = await crawl_aliyun_cves(max_pages=3, headless=False)
```

### crawl_aliyun_cves_incremental()

快速进行增量爬取的便捷函数。

```python
async def crawl_aliyun_cves_incremental(days: int = 7) -> List[CVEInfo]:
    """便捷的增量CVE爬取函数"""
```

**参数:**
- `days` (int): 爬取最近几天的数据，默认7天

**返回:**
- `List[CVEInfo]`: 新的CVE信息列表

**示例:**
```python
# 爬取最近3天的数据
new_cves = await crawl_aliyun_cves_incremental(days=3)

# 爬取最近1天的数据
new_cves = await crawl_aliyun_cves_incremental(days=1)
```

```python
@dataclass
class CVEInfo:
    cve_id: str
    description: str
    severity: str
    cvss_score: float
    published_date: datetime
    modified_date: datetime
    references: List[str] = field(default_factory=list)
    affected_products: List[str] = field(default_factory=list)
    cwe_ids: List[str] = field(default_factory=list)
```

#### 严重性等级

- `CRITICAL`: 严重 (CVSS >= 9.0)
- `HIGH`: 高危 (CVSS >= 7.0)
- `MEDIUM`: 中危 (CVSS >= 4.0)
- `LOW`: 低危 (CVSS < 4.0)

## 异常处理

### 常见异常

1. **浏览器启动失败**
   ```python
   try:
       async with AliyunCVECrawler() as crawler:
           cves = await crawler.crawl_all()
   except Exception as e:
       if "browser" in str(e).lower():
           print("浏览器启动失败，请检查Playwright安装")
   ```

2. **网络超时**
   ```python
   config = CrawlConfig(timeout=60)  # 增加超时时间
   ```

3. **页面解析失败**
   ```python
   # 爬虫会自动跳过解析失败的页面，并在日志中记录
   ```

## 性能优化

### 并发控制

爬虫内置了并发控制机制，默认最多同时处理5个详情页面。

### 内存管理

对于大量数据的爬取，建议分批处理：

```python
async def batch_crawl():
    all_cves = []
    for batch_start in range(1, 101, 10):  # 每次10页
        batch_cves = await crawl_aliyun_cves(
            max_pages=10, 
            start_page=batch_start
        )
        all_cves.extend(batch_cves)
        # 可选：保存中间结果
    return all_cves
```

### 缓存机制

爬虫会自动缓存已爬取的数据，避免重复爬取。缓存TTL可通过配置调整。

## 日志记录

爬虫使用loguru进行日志记录，支持以下日志级别：

- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

可以通过以下方式配置日志：

```python
from loguru import logger

# 添加文件日志
logger.add("crawler.log", rotation="1 day", retention="30 days")

# 设置日志级别
logger.remove()
logger.add(sys.stderr, level="INFO")
```
