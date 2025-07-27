#!/usr/bin/env python3
"""
CVE监控服务示例

本示例展示如何构建一个持续监控CVE的服务，
包括定时检查、邮件通知、数据存储等功能。
"""

import asyncio
import json
import smtplib
import sys
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import crawl_aliyun_cves_incremental, CVEInfo
from loguru import logger


class CVEMonitoringService:
    """CVE监控服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化监控服务"""
        self.config = config
        self.data_dir = Path(config.get('data_dir', './monitoring_data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        log_file = self.data_dir / "monitoring.log"
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
        # 监控状态
        self.last_check_file = self.data_dir / "last_check.json"
        self.alerts_file = self.data_dir / "alerts.json"
        
        logger.info("CVE监控服务初始化完成")
    
    async def run_monitoring_cycle(self):
        """运行一次监控周期"""
        try:
            logger.info("开始CVE监控检查...")
            
            # 获取上次检查时间
            last_check = self._get_last_check_time()
            
            # 计算检查天数
            if last_check:
                days_since = (datetime.now() - last_check).days + 1
                days_since = max(1, min(days_since, 7))  # 限制在1-7天
            else:
                days_since = 1  # 首次运行检查1天
            
            logger.info(f"检查最近 {days_since} 天的CVE数据")
            
            # 爬取新CVE
            new_cves = await crawl_aliyun_cves_incremental(days=days_since)
            
            if new_cves:
                logger.info(f"发现 {len(new_cves)} 个新CVE")
                
                # 分析CVE
                analysis = self._analyze_cves(new_cves)
                
                # 保存数据
                await self._save_cves(new_cves, analysis)
                
                # 检查是否需要发送警报
                if self._should_send_alert(analysis):
                    await self._send_alert(new_cves, analysis)
                
                # 生成报告
                await self._generate_report(new_cves, analysis)
                
            else:
                logger.info("没有发现新CVE")
            
            # 更新最后检查时间
            self._update_last_check_time()
            
            logger.info("CVE监控检查完成")
            
        except Exception as e:
            logger.error(f"监控检查失败: {e}")
            raise
    
    def _get_last_check_time(self) -> datetime:
        """获取上次检查时间"""
        try:
            if self.last_check_file.exists():
                with open(self.last_check_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_check'])
        except Exception as e:
            logger.warning(f"读取上次检查时间失败: {e}")
        
        return None
    
    def _update_last_check_time(self):
        """更新最后检查时间"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"更新检查时间失败: {e}")
    
    def _analyze_cves(self, cves: List[CVEInfo]) -> Dict[str, Any]:
        """分析CVE数据"""
        analysis = {
            'total_count': len(cves),
            'severity_distribution': {},
            'cvss_stats': {},
            'high_risk_count': 0,
            'critical_count': 0,
            'recent_critical': [],
            'top_cvss': []
        }
        
        # 严重性分布
        for cve in cves:
            severity = cve.severity
            analysis['severity_distribution'][severity] = \
                analysis['severity_distribution'].get(severity, 0) + 1
            
            if severity == 'CRITICAL':
                analysis['critical_count'] += 1
                analysis['recent_critical'].append({
                    'cve_id': cve.cve_id,
                    'cvss_score': cve.cvss_score,
                    'description': cve.description[:100] + '...'
                })
            elif severity in ['HIGH', 'CRITICAL']:
                analysis['high_risk_count'] += 1
        
        # CVSS统计
        cvss_scores = [cve.cvss_score for cve in cves if cve.cvss_score > 0]
        if cvss_scores:
            analysis['cvss_stats'] = {
                'average': sum(cvss_scores) / len(cvss_scores),
                'max': max(cvss_scores),
                'min': min(cvss_scores),
                'count': len(cvss_scores)
            }
            
            # 最高CVSS分数的CVE
            analysis['top_cvss'] = sorted(
                [{'cve_id': cve.cve_id, 'cvss_score': cve.cvss_score, 
                  'description': cve.description[:100] + '...'} 
                 for cve in cves if cve.cvss_score > 0],
                key=lambda x: x['cvss_score'],
                reverse=True
            )[:5]
        
        return analysis
    
    async def _save_cves(self, cves: List[CVEInfo], analysis: Dict[str, Any]):
        """保存CVE数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存CVE数据
        cve_file = self.data_dir / f"cves_{timestamp}.json"
        cve_data = {
            'timestamp': timestamp,
            'count': len(cves),
            'analysis': analysis,
            'cves': [cve.to_dict() for cve in cves]
        }
        
        with open(cve_file, 'w', encoding='utf-8') as f:
            json.dump(cve_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"CVE数据已保存到: {cve_file}")
    
    def _should_send_alert(self, analysis: Dict[str, Any]) -> bool:
        """判断是否需要发送警报"""
        alert_config = self.config.get('alerts', {})
        
        # 检查严重漏洞数量
        if analysis['critical_count'] >= alert_config.get('critical_threshold', 1):
            return True
        
        # 检查高危漏洞数量
        if analysis['high_risk_count'] >= alert_config.get('high_risk_threshold', 5):
            return True
        
        # 检查平均CVSS分数
        cvss_stats = analysis.get('cvss_stats', {})
        if cvss_stats.get('average', 0) >= alert_config.get('cvss_threshold', 8.0):
            return True
        
        return False
    
    async def _send_alert(self, cves: List[CVEInfo], analysis: Dict[str, Any]):
        """发送警报"""
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                logger.info("邮件通知未启用，跳过发送警报")
                return
            
            # 构建邮件内容
            subject = f"CVE安全警报 - 发现 {analysis['critical_count']} 个严重漏洞"
            body = self._build_alert_email(analysis)
            
            # 发送邮件
            await self._send_email(subject, body, email_config)
            
            # 记录警报
            await self._log_alert(analysis)
            
            logger.info("安全警报已发送")
            
        except Exception as e:
            logger.error(f"发送警报失败: {e}")
    
    def _build_alert_email(self, analysis: Dict[str, Any]) -> str:
        """构建警报邮件内容"""
        content = f"""
CVE安全监控警报

检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 概览 ===
总计新CVE: {analysis['total_count']}
严重漏洞: {analysis['critical_count']}
高危漏洞: {analysis['high_risk_count']}

=== 严重性分布 ===
"""
        
        for severity, count in analysis['severity_distribution'].items():
            content += f"{severity}: {count}\n"
        
        if analysis.get('cvss_stats'):
            stats = analysis['cvss_stats']
            content += f"""
=== CVSS统计 ===
平均分数: {stats['average']:.2f}
最高分数: {stats['max']}
最低分数: {stats['min']}
"""
        
        if analysis['recent_critical']:
            content += "\n=== 严重漏洞详情 ===\n"
            for cve in analysis['recent_critical'][:5]:
                content += f"- {cve['cve_id']} (CVSS: {cve['cvss_score']})\n"
                content += f"  {cve['description']}\n\n"
        
        content += "\n请及时关注和处理相关安全风险。"
        
        return content
    
    async def _send_email(self, subject: str, body: str, email_config: Dict[str, Any]):
        """发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = ', '.join(email_config['to'])
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            if email_config.get('use_tls', True):
                server.starttls()
            
            if email_config.get('username') and email_config.get('password'):
                server.login(email_config['username'], email_config['password'])
            
            server.send_message(msg)
    
    async def _log_alert(self, analysis: Dict[str, Any]):
        """记录警报"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'alert_type': 'cve_security_alert'
        }
        
        # 读取现有警报
        alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    alerts = json.load(f)
            except:
                pass
        
        # 添加新警报
        alerts.append(alert_data)
        
        # 保持最近100条警报
        alerts = alerts[-100:]
        
        # 保存警报
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2, default=str)
    
    async def _generate_report(self, cves: List[CVEInfo], analysis: Dict[str, Any]):
        """生成监控报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.data_dir / f"report_{timestamp}.md"
        
        report_content = f"""# CVE监控报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- **总计新CVE**: {analysis['total_count']}
- **严重漏洞**: {analysis['critical_count']}
- **高危漏洞**: {analysis['high_risk_count']}

## 严重性分布

"""
        
        for severity, count in analysis['severity_distribution'].items():
            percentage = (count / analysis['total_count']) * 100
            report_content += f"- **{severity}**: {count} ({percentage:.1f}%)\n"
        
        if analysis.get('cvss_stats'):
            stats = analysis['cvss_stats']
            report_content += f"""
## CVSS统计

- **平均分数**: {stats['average']:.2f}
- **最高分数**: {stats['max']}
- **最低分数**: {stats['min']}
- **有效评分数**: {stats['count']}
"""
        
        if analysis['top_cvss']:
            report_content += "\n## 高分CVE (Top 5)\n\n"
            for i, cve in enumerate(analysis['top_cvss'][:5], 1):
                report_content += f"{i}. **{cve['cve_id']}** (CVSS: {cve['cvss_score']})\n"
                report_content += f"   {cve['description']}\n\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"监控报告已生成: {report_file}")


async def run_monitoring_service():
    """运行监控服务"""
    
    # 监控配置
    config = {
        'data_dir': './monitoring_data',
        'alerts': {
            'critical_threshold': 1,      # 严重漏洞警报阈值
            'high_risk_threshold': 3,     # 高危漏洞警报阈值
            'cvss_threshold': 8.0         # CVSS分数警报阈值
        },
        'email': {
            'enabled': False,  # 设置为True启用邮件通知
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'from': 'your-email@gmail.com',
            'to': ['admin@company.com'],
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
    }
    
    # 创建监控服务
    service = CVEMonitoringService(config)
    
    # 运行监控
    await service.run_monitoring_cycle()


async def run_continuous_monitoring():
    """持续监控模式"""
    print("启动CVE持续监控服务...")
    print("按 Ctrl+C 停止监控")
    
    config = {
        'data_dir': './monitoring_data',
        'alerts': {
            'critical_threshold': 1,
            'high_risk_threshold': 3,
            'cvss_threshold': 8.0
        },
        'email': {
            'enabled': False  # 根据需要启用
        }
    }
    
    service = CVEMonitoringService(config)
    
    try:
        while True:
            await service.run_monitoring_cycle()
            
            # 等待4小时后再次检查
            print("等待4小时后进行下次检查...")
            await asyncio.sleep(4 * 3600)
            
    except KeyboardInterrupt:
        print("\n监控服务已停止")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CVE监控服务")
    parser.add_argument("--continuous", action="store_true", help="持续监控模式")
    
    args = parser.parse_args()
    
    if args.continuous:
        asyncio.run(run_continuous_monitoring())
    else:
        asyncio.run(run_monitoring_service())
