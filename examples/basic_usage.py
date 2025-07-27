#!/usr/bin/env python3
"""
基本使用示例

本文件展示了阿里云CVE爬虫的基本使用方法。
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    crawl_aliyun_cves, 
    crawl_aliyun_cves_incremental,
    AliyunCVECrawler,
    CrawlConfig
)


async def example_1_simple_crawl():
    """示例1: 简单爬取"""
    print("=== 示例1: 简单爬取 ===")
    
    try:
        # 爬取前3页数据
        cve_infos = await crawl_aliyun_cves(max_pages=3)
        
        print(f"成功爬取 {len(cve_infos)} 个CVE")
        
        # 显示前3个结果
        for i, cve in enumerate(cve_infos[:3]):
            print(f"\n{i+1}. {cve.cve_id}")
            print(f"   严重性: {cve.severity}")
            print(f"   CVSS: {cve.cvss_score}")
            print(f"   发布日期: {cve.published_date.strftime('%Y-%m-%d')}")
            print(f"   描述: {cve.description[:100]}...")
            
    except Exception as e:
        print(f"爬取失败: {e}")


async def example_2_incremental_crawl():
    """示例2: 增量爬取"""
    print("\n=== 示例2: 增量爬取 ===")
    
    try:
        # 爬取最近7天的数据
        new_cves = await crawl_aliyun_cves_incremental(days=7)
        
        if new_cves:
            print(f"发现 {len(new_cves)} 个新CVE")
            
            # 按严重性分类
            severity_count = {}
            for cve in new_cves:
                severity_count[cve.severity] = severity_count.get(cve.severity, 0) + 1
            
            print("严重性分布:")
            for severity, count in severity_count.items():
                print(f"  {severity}: {count}")
                
            # 显示高危漏洞
            high_risk = [cve for cve in new_cves if cve.cvss_score >= 7.0]
            if high_risk:
                print(f"\n高危漏洞 (CVSS >= 7.0): {len(high_risk)}")
                for cve in high_risk[:3]:
                    print(f"  - {cve.cve_id}: CVSS {cve.cvss_score}")
        else:
            print("没有发现新的CVE")
            
    except Exception as e:
        print(f"增量爬取失败: {e}")


async def example_3_custom_config():
    """示例3: 自定义配置"""
    print("\n=== 示例3: 自定义配置 ===")
    
    # 创建自定义配置
    config = CrawlConfig(
        max_pages=2,               # 只爬取2页
        delay_range=(2, 4),        # 请求间隔2-4秒
        timeout=60,                # 页面超时60秒
        headless=True,             # 无头模式
        data_dir="./example_data"  # 自定义数据目录
    )
    
    try:
        async with AliyunCVECrawler(config) as crawler:
            # 爬取数据
            cve_infos = await crawler.crawl_all(start_page=1, max_pages=2)
            
            # 获取统计信息
            metrics = crawler.get_metrics()
            
            print(f"爬取完成:")
            print(f"  页面数: {metrics['pages_crawled']}")
            print(f"  CVE数量: {len(cve_infos)}")
            print(f"  错误数: {metrics['errors']}")
            
            if metrics['start_time'] and metrics['end_time']:
                duration = (metrics['end_time'] - metrics['start_time']).total_seconds()
                print(f"  耗时: {duration:.2f}秒")
                
    except Exception as e:
        print(f"自定义配置爬取失败: {e}")


async def example_4_error_handling():
    """示例4: 错误处理和重试"""
    print("\n=== 示例4: 错误处理和重试 ===")
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"第 {attempt + 1} 次尝试...")
            
            # 使用较短的超时时间来模拟可能的错误
            config = CrawlConfig(
                max_pages=1,
                timeout=30,
                delay_range=(1, 2)
            )
            
            async with AliyunCVECrawler(config) as crawler:
                cve_infos = await crawler.crawl_all()
                print(f"成功爬取 {len(cve_infos)} 个CVE")
                break
                
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10  # 递增等待时间
                print(f"等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
            else:
                print("所有重试都失败了")


async def example_5_data_analysis():
    """示例5: 数据分析"""
    print("\n=== 示例5: 数据分析 ===")
    
    try:
        # 爬取数据
        cve_infos = await crawl_aliyun_cves(max_pages=3)
        
        if not cve_infos:
            print("没有数据可分析")
            return
        
        print(f"分析 {len(cve_infos)} 个CVE:")
        
        # 1. 严重性分布
        from collections import Counter
        severity_dist = Counter(cve.severity for cve in cve_infos)
        print("\n严重性分布:")
        for severity, count in severity_dist.most_common():
            percentage = (count / len(cve_infos)) * 100
            print(f"  {severity}: {count} ({percentage:.1f}%)")
        
        # 2. CVSS分数分布
        cvss_scores = [cve.cvss_score for cve in cve_infos if cve.cvss_score > 0]
        if cvss_scores:
            avg_cvss = sum(cvss_scores) / len(cvss_scores)
            max_cvss = max(cvss_scores)
            min_cvss = min(cvss_scores)
            
            print(f"\nCVSS分数统计:")
            print(f"  平均分: {avg_cvss:.2f}")
            print(f"  最高分: {max_cvss}")
            print(f"  最低分: {min_cvss}")
        
        # 3. 最新漏洞
        recent_cves = sorted(cve_infos, key=lambda x: x.published_date, reverse=True)
        print(f"\n最新的3个漏洞:")
        for i, cve in enumerate(recent_cves[:3]):
            print(f"  {i+1}. {cve.cve_id} - {cve.published_date.strftime('%Y-%m-%d')}")
        
        # 4. 高危漏洞统计
        critical_cves = [cve for cve in cve_infos if cve.severity == "CRITICAL"]
        high_cves = [cve for cve in cve_infos if cve.severity == "HIGH"]
        
        print(f"\n风险统计:")
        print(f"  严重漏洞: {len(critical_cves)}")
        print(f"  高危漏洞: {len(high_cves)}")
        print(f"  高风险比例: {((len(critical_cves) + len(high_cves)) / len(cve_infos) * 100):.1f}%")
        
    except Exception as e:
        print(f"数据分析失败: {e}")


async def main():
    """主函数"""
    print("阿里云CVE爬虫 - 使用示例")
    print("=" * 50)
    
    # 运行所有示例
    await example_1_simple_crawl()
    await example_2_incremental_crawl()
    await example_3_custom_config()
    await example_4_error_handling()
    await example_5_data_analysis()
    
    print("\n所有示例运行完成!")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
