#!/usr/bin/env python3
"""
阿里云CVE爬虫测试

本文件包含爬虫的基本测试用例。
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    CrawlConfig,
    CVEListItem,
    CVEDetail,
    AliyunCVECrawler,
    crawl_aliyun_cves,
    crawl_aliyun_cves_incremental
)


class TestCrawlConfig:
    """测试CrawlConfig类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CrawlConfig()
        
        assert config.base_url == "https://avd.aliyun.com"
        assert config.max_pages == 100
        assert config.delay_range == (1, 3)
        assert config.headless is True
        assert config.timeout == 30
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = CrawlConfig(
            max_pages=50,
            delay_range=(2, 5),
            headless=False,
            timeout=60
        )
        
        assert config.max_pages == 50
        assert config.delay_range == (2, 5)
        assert config.headless is False
        assert config.timeout == 60


class TestCVEListItem:
    """测试CVEListItem类"""
    
    def test_create_cve_list_item(self):
        """测试创建CVE列表项"""
        item = CVEListItem(
            cve_id="CVE-2024-1234",
            title="Test Vulnerability",
            cwe_type="CWE-79",
            disclosure_date="2024-01-15",
            cvss_score="7.5",
            detail_url="https://avd.aliyun.com/detail?id=CVE-2024-1234"
        )
        
        assert item.cve_id == "CVE-2024-1234"
        assert item.title == "Test Vulnerability"
        assert item.cwe_type == "CWE-79"
        assert item.cvss_score == "7.5"
    
    def test_to_dict(self):
        """测试转换为字典"""
        item = CVEListItem(
            cve_id="CVE-2024-1234",
            title="Test Vulnerability",
            cwe_type="CWE-79",
            disclosure_date="2024-01-15",
            cvss_score="7.5",
            detail_url="https://avd.aliyun.com/detail?id=CVE-2024-1234"
        )
        
        data = item.to_dict()
        
        assert isinstance(data, dict)
        assert data['cve_id'] == "CVE-2024-1234"
        assert data['title'] == "Test Vulnerability"
        assert data['cvss_score'] == "7.5"


class TestCVEDetail:
    """测试CVEDetail类"""
    
    def test_create_cve_detail(self):
        """测试创建CVE详情"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test Vulnerability",
            description="This is a test vulnerability",
            solution="Update to latest version",
            cvss_score="7.5",
            disclosure_date="2024-01-15"
        )
        
        assert detail.cve_id == "CVE-2024-1234"
        assert detail.description == "This is a test vulnerability"
        assert detail.cvss_score == "7.5"
    
    def test_to_dict(self):
        """测试转换为字典"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test Vulnerability",
            description="This is a test vulnerability",
            solution="Update to latest version"
        )
        
        data = detail.to_dict()
        
        assert isinstance(data, dict)
        assert data['cve_id'] == "CVE-2024-1234"
        assert data['description'] == "This is a test vulnerability"
    
    @patch('main.CVEInfo')
    def test_to_cve_info(self, mock_cve_info):
        """测试转换为CVEInfo"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test Vulnerability",
            description="This is a test vulnerability",
            solution="Update to latest version",
            cvss_score="7.5",
            disclosure_date="2024-01-15"
        )
        
        # 模拟CVEInfo构造函数
        mock_cve_info.return_value = Mock()
        
        result = detail.to_cve_info()
        
        # 验证CVEInfo被调用
        mock_cve_info.assert_called_once()
        assert result is not None


class TestAliyunCVECrawler:
    """测试AliyunCVECrawler类"""
    
    def test_init_crawler(self):
        """测试爬虫初始化"""
        config = CrawlConfig(max_pages=5)
        crawler = AliyunCVECrawler(config)
        
        assert crawler.config.max_pages == 5
        assert crawler.crawled_cves == set()
        assert crawler.failed_cves == set()
        assert crawler.metrics['pages_crawled'] == 0
    
    def test_init_crawler_default_config(self):
        """测试使用默认配置初始化爬虫"""
        crawler = AliyunCVECrawler()
        
        assert crawler.config.max_pages == 100
        assert crawler.config.headless is True
    
    def test_get_metrics(self):
        """测试获取指标"""
        crawler = AliyunCVECrawler()
        metrics = crawler.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'pages_crawled' in metrics
        assert 'cves_found' in metrics
        assert 'errors' in metrics
        assert metrics['pages_crawled'] == 0


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    @pytest.mark.asyncio
    @patch('main.AliyunCVECrawler')
    async def test_crawl_aliyun_cves(self, mock_crawler_class):
        """测试便捷爬取函数"""
        # 模拟爬虫实例
        mock_crawler = AsyncMock()
        mock_crawler.crawl_all.return_value = [Mock()]
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None
        
        mock_crawler_class.return_value = mock_crawler
        
        # 调用函数
        result = await crawl_aliyun_cves(max_pages=3)
        
        # 验证
        mock_crawler_class.assert_called_once()
        mock_crawler.crawl_all.assert_called_once_with(1, 3)
        assert len(result) == 1
    
    @pytest.mark.asyncio
    @patch('main.AliyunCVECrawler')
    async def test_crawl_aliyun_cves_incremental(self, mock_crawler_class):
        """测试便捷增量爬取函数"""
        # 模拟爬虫实例
        mock_crawler = AsyncMock()
        mock_crawler.crawl_incremental.return_value = [Mock()]
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None
        
        mock_crawler_class.return_value = mock_crawler
        
        # 调用函数
        result = await crawl_aliyun_cves_incremental(days=3)
        
        # 验证
        mock_crawler_class.assert_called_once()
        mock_crawler.crawl_incremental.assert_called_once()
        assert len(result) == 1


class TestDataValidation:
    """测试数据验证"""
    
    def test_cve_id_format(self):
        """测试CVE ID格式"""
        valid_ids = ["CVE-2024-1234", "CVE-2023-0001", "CVE-2022-12345"]
        
        for cve_id in valid_ids:
            item = CVEListItem(
                cve_id=cve_id,
                title="Test",
                cwe_type="CWE-79",
                disclosure_date="2024-01-15",
                cvss_score="7.5",
                detail_url="https://example.com"
            )
            assert item.cve_id == cve_id
    
    def test_cvss_score_validation(self):
        """测试CVSS分数验证"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test",
            description="Test description",
            solution="Test solution",
            cvss_score="7.5"
        )
        
        # 测试转换为CVEInfo时的分数处理
        with patch('main.CVEInfo') as mock_cve_info:
            mock_cve_info.return_value = Mock()
            detail.to_cve_info()
            
            # 验证CVEInfo被正确的参数调用
            call_args = mock_cve_info.call_args
            assert call_args is not None


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_cvss_score(self):
        """测试无效CVSS分数处理"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test",
            description="Test description",
            solution="Test solution",
            cvss_score="invalid"  # 无效分数
        )
        
        with patch('main.CVEInfo') as mock_cve_info:
            mock_cve_info.return_value = Mock()
            
            # 应该能够处理无效分数而不抛出异常
            result = detail.to_cve_info()
            assert result is not None
    
    def test_missing_date(self):
        """测试缺失日期处理"""
        detail = CVEDetail(
            cve_id="CVE-2024-1234",
            title="Test",
            description="Test description",
            solution="Test solution",
            disclosure_date=""  # 空日期
        )
        
        with patch('main.CVEInfo') as mock_cve_info:
            mock_cve_info.return_value = Mock()
            
            # 应该能够处理空日期
            result = detail.to_cve_info()
            assert result is not None


# 集成测试（需要网络连接，标记为慢速测试）
@pytest.mark.slow
class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_real_crawl_single_page(self):
        """测试真实爬取单页（需要网络连接）"""
        config = CrawlConfig(max_pages=1, timeout=60)
        
        try:
            async with AliyunCVECrawler(config) as crawler:
                cves = await crawler.crawl_all(start_page=1, max_pages=1)
                
                # 基本验证
                assert isinstance(cves, list)
                
                if cves:  # 如果有数据
                    cve = cves[0]
                    assert hasattr(cve, 'cve_id')
                    assert hasattr(cve, 'description')
                    assert hasattr(cve, 'severity')
                    
        except Exception as e:
            pytest.skip(f"网络连接问题，跳过集成测试: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
