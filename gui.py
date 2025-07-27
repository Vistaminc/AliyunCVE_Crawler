#!/usr/bin/env python3
"""
AliyunCVE_Crawler GUI界面

使用ttkbootstrap构建的现代化图形用户界面
"""

import asyncio
import json
import os
import sys
import threading
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    AliyunCVECrawler,
    CrawlConfig,
    crawl_aliyun_cves,
    crawl_aliyun_cves_incremental,
    CVEInfo
)


class CVECrawlerGUI:
    """CVE爬虫GUI主类"""
    
    def __init__(self):
        """初始化GUI"""
        # 创建主窗口
        self.root = ttk_bs.Window(
            title="AliyunCVE_Crawler - 阿里云CVE爬虫",
            themename="superhero",  # 使用现代主题
            size=(1200, 800),
            resizable=(True, True)
        )
        
        # 设置窗口图标和居中
        self.center_window()
        
        # 初始化变量
        self.crawler_thread = None
        self.is_crawling = False
        self.stop_requested = False
        self.current_config = CrawlConfig()
        self.crawl_results: List[CVEInfo] = []
        self.current_crawler = None
        
        # 创建界面
        self.create_widgets()
        self.load_config()
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk_bs.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 创建标题
        title_frame = ttk_bs.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk_bs.Label(
            title_frame,
            text="Aliyun_CVE阿里云CVE爬虫",
            font=("Microsoft YaHei", 20, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk_bs.Label(
            title_frame,
            text="专业的漏洞数据采集工具",
            font=("Microsoft YaHei", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack()
        
        # 创建Notebook（标签页）
        self.notebook = ttk_bs.Notebook(main_frame, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)
        
        # 创建各个标签页
        self.create_crawl_tab()
        self.create_config_tab()
        self.create_results_tab()
        self.create_monitor_tab()
        
        # 创建状态栏
        self.create_status_bar(main_frame)
    
    def create_crawl_tab(self):
        """创建爬取标签页"""
        crawl_frame = ttk_bs.Frame(self.notebook, padding=20)
        self.notebook.add(crawl_frame, text="🚀 数据爬取")
        
        # 爬取模式选择
        mode_frame = ttk_bs.LabelFrame(crawl_frame, text="爬取模式", padding=15)
        mode_frame.pack(fill=X, pady=(0, 15))
        
        self.crawl_mode = tk.StringVar(value="normal")
        
        normal_radio = ttk_bs.Radiobutton(
            mode_frame,
            text="🔄 常规爬取",
            variable=self.crawl_mode,
            value="normal",
            bootstyle="primary",
            command=self.on_mode_change
        )
        normal_radio.pack(anchor=W, pady=2)
        
        incremental_radio = ttk_bs.Radiobutton(
            mode_frame,
            text="⚡ 增量爬取",
            variable=self.crawl_mode,
            value="incremental",
            bootstyle="success",
            command=self.on_mode_change
        )
        incremental_radio.pack(anchor=W, pady=2)
        
        # 爬取参数
        params_frame = ttk_bs.LabelFrame(crawl_frame, text="爬取参数", padding=15)
        params_frame.pack(fill=X, pady=(0, 15))
        
        # 常规爬取参数
        self.normal_params_frame = ttk_bs.Frame(params_frame)
        self.normal_params_frame.pack(fill=X)
        
        # 页数设置
        pages_frame = ttk_bs.Frame(self.normal_params_frame)
        pages_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(pages_frame, text="爬取页数:", width=12).pack(side=LEFT)
        self.max_pages_var = tk.StringVar(value="10")
        pages_spinbox = ttk_bs.Spinbox(
            pages_frame,
            from_=1,
            to=100,
            textvariable=self.max_pages_var,
            width=10,
            bootstyle="primary"
        )
        pages_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # 起始页设置
        start_frame = ttk_bs.Frame(self.normal_params_frame)
        start_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(start_frame, text="起始页:", width=12).pack(side=LEFT)
        self.start_page_var = tk.StringVar(value="1")
        start_spinbox = ttk_bs.Spinbox(
            start_frame,
            from_=1,
            to=1000,
            textvariable=self.start_page_var,
            width=10,
            bootstyle="primary"
        )
        start_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # 增量爬取参数
        self.incremental_params_frame = ttk_bs.Frame(params_frame)
        
        days_frame = ttk_bs.Frame(self.incremental_params_frame)
        days_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(days_frame, text="爬取天数:", width=12).pack(side=LEFT)
        self.days_var = tk.StringVar(value="7")
        days_spinbox = ttk_bs.Spinbox(
            days_frame,
            from_=1,
            to=30,
            textvariable=self.days_var,
            width=10,
            bootstyle="success"
        )
        days_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # 高级选项
        advanced_frame = ttk_bs.LabelFrame(crawl_frame, text="高级选项", padding=15)
        advanced_frame.pack(fill=X, pady=(0, 15))
        
        # 无头模式
        self.headless_var = tk.BooleanVar(value=True)
        headless_check = ttk_bs.Checkbutton(
            advanced_frame,
            text="🔇 无头模式（后台运行）",
            variable=self.headless_var,
            bootstyle="primary-round-toggle"
        )
        headless_check.pack(anchor=W, pady=2)
        
        # 显示浏览器
        self.show_browser_var = tk.BooleanVar(value=False)
        browser_check = ttk_bs.Checkbutton(
            advanced_frame,
            text="🌐 显示浏览器（调试模式）",
            variable=self.show_browser_var,
            bootstyle="warning-round-toggle"
        )
        browser_check.pack(anchor=W, pady=2)
        
        # 控制按钮
        control_frame = ttk_bs.Frame(crawl_frame)
        control_frame.pack(fill=X, pady=(0, 15))
        
        self.start_button = ttk_bs.Button(
            control_frame,
            text="🚀 开始爬取",
            command=self.start_crawling,
            bootstyle="success",
            width=15
        )
        self.start_button.pack(side=LEFT, padx=(0, 10))
        
        self.stop_button = ttk_bs.Button(
            control_frame,
            text="⏹️ 停止爬取",
            command=self.stop_crawling,
            bootstyle="danger",
            width=15,
            state=DISABLED
        )
        self.stop_button.pack(side=LEFT, padx=(0, 10))
        
        self.clear_button = ttk_bs.Button(
            control_frame,
            text="🗑️ 清空日志",
            command=self.clear_log,
            bootstyle="secondary",
            width=15
        )
        self.clear_button.pack(side=LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk_bs.Progressbar(
            crawl_frame,
            variable=self.progress_var,
            bootstyle="success-striped",
            mode='indeterminate'
        )
        self.progress_bar.pack(fill=X, pady=(0, 15))
        
        # 日志输出
        log_frame = ttk_bs.LabelFrame(crawl_frame, text="实时日志", padding=10)
        log_frame.pack(fill=BOTH, expand=True)
        
        self.log_text = ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=BOTH, expand=True)
        
        # 初始化显示模式
        self.on_mode_change()
    
    def create_config_tab(self):
        """创建配置标签页"""
        config_frame = ttk_bs.Frame(self.notebook, padding=20)
        self.notebook.add(config_frame, text="⚙️ 配置设置")
        
        # 创建左右分栏
        left_frame = ttk_bs.Frame(config_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk_bs.Frame(config_frame)
        right_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        # 基本配置
        basic_frame = ttk_bs.LabelFrame(left_frame, text="基本配置", padding=15)
        basic_frame.pack(fill=X, pady=(0, 15))
        
        # 超时设置
        timeout_frame = ttk_bs.Frame(basic_frame)
        timeout_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(timeout_frame, text="页面超时(秒):", width=15).pack(side=LEFT)
        self.timeout_var = tk.StringVar(value="30")
        timeout_entry = ttk_bs.Entry(
            timeout_frame,
            textvariable=self.timeout_var,
            width=10,
            bootstyle="primary"
        )
        timeout_entry.pack(side=LEFT, padx=(5, 0))
        
        # 延迟设置
        delay_frame = ttk_bs.Frame(basic_frame)
        delay_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(delay_frame, text="请求延迟(秒):", width=15).pack(side=LEFT)
        delay_sub_frame = ttk_bs.Frame(delay_frame)
        delay_sub_frame.pack(side=LEFT, padx=(5, 0))
        
        self.delay_min_var = tk.StringVar(value="1")
        self.delay_max_var = tk.StringVar(value="3")
        
        ttk_bs.Entry(
            delay_sub_frame,
            textvariable=self.delay_min_var,
            width=5,
            bootstyle="primary"
        ).pack(side=LEFT)
        
        ttk_bs.Label(delay_sub_frame, text=" - ").pack(side=LEFT)
        
        ttk_bs.Entry(
            delay_sub_frame,
            textvariable=self.delay_max_var,
            width=5,
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # 数据目录
        data_frame = ttk_bs.Frame(basic_frame)
        data_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(data_frame, text="数据目录:", width=15).pack(side=LEFT)
        self.data_dir_var = tk.StringVar(value="./data/aliyun_cve")
        data_entry = ttk_bs.Entry(
            data_frame,
            textvariable=self.data_dir_var,
            bootstyle="primary"
        )
        data_entry.pack(side=LEFT, fill=X, expand=True, padx=(5, 5))
        
        browse_button = ttk_bs.Button(
            data_frame,
            text="📁",
            command=self.browse_data_dir,
            bootstyle="secondary",
            width=3
        )
        browse_button.pack(side=RIGHT)
        
        # 高级配置
        advanced_config_frame = ttk_bs.LabelFrame(left_frame, text="高级配置", padding=15)
        advanced_config_frame.pack(fill=X, pady=(0, 15))
        
        # User-Agent
        ua_frame = ttk_bs.Frame(advanced_config_frame)
        ua_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(ua_frame, text="User-Agent:").pack(anchor=W)
        self.user_agent_var = tk.StringVar(
            value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        ua_entry = ttk_bs.Entry(
            ua_frame,
            textvariable=self.user_agent_var,
            bootstyle="primary"
        )
        ua_entry.pack(fill=X, pady=(5, 0))
        
        # 缓存TTL
        cache_frame = ttk_bs.Frame(advanced_config_frame)
        cache_frame.pack(fill=X, pady=5)
        
        ttk_bs.Label(cache_frame, text="缓存TTL(秒):", width=15).pack(side=LEFT)
        self.cache_ttl_var = tk.StringVar(value="86400")
        cache_entry = ttk_bs.Entry(
            cache_frame,
            textvariable=self.cache_ttl_var,
            width=10,
            bootstyle="primary"
        )
        cache_entry.pack(side=LEFT, padx=(5, 0))
        
        # 右侧控制按钮
        control_frame = ttk_bs.LabelFrame(right_frame, text="配置管理", padding=15)
        control_frame.pack(fill=X)
        
        ttk_bs.Button(
            control_frame,
            text="💾 保存配置",
            command=self.save_config,
            bootstyle="success",
            width=15
        ).pack(fill=X, pady=2)
        
        ttk_bs.Button(
            control_frame,
            text="📂 加载配置",
            command=self.load_config_file,
            bootstyle="primary",
            width=15
        ).pack(fill=X, pady=2)
        
        ttk_bs.Button(
            control_frame,
            text="🔄 重置配置",
            command=self.reset_config,
            bootstyle="warning",
            width=15
        ).pack(fill=X, pady=2)
        
        ttk_bs.Button(
            control_frame,
            text="📋 导出配置",
            command=self.export_config,
            bootstyle="info",
            width=15
        ).pack(fill=X, pady=2)
    
    def create_results_tab(self):
        """创建结果标签页"""
        results_frame = ttk_bs.Frame(self.notebook, padding=20)
        self.notebook.add(results_frame, text="📊 爬取结果")
        
        # 统计信息
        stats_frame = ttk_bs.LabelFrame(results_frame, text="统计信息", padding=15)
        stats_frame.pack(fill=X, pady=(0, 15))
        
        # 创建统计标签
        stats_grid = ttk_bs.Frame(stats_frame)
        stats_grid.pack(fill=X)
        
        # 第一行统计
        row1 = ttk_bs.Frame(stats_grid)
        row1.pack(fill=X, pady=2)
        
        self.total_cves_label = ttk_bs.Label(
            row1, text="总CVE数: 0", bootstyle="primary", font=("Microsoft YaHei", 12, "bold")
        )
        self.total_cves_label.pack(side=LEFT, padx=(0, 20))
        
        self.critical_cves_label = ttk_bs.Label(
            row1, text="严重: 0", bootstyle="danger", font=("Microsoft YaHei", 12, "bold")
        )
        self.critical_cves_label.pack(side=LEFT, padx=(0, 20))
        
        self.high_cves_label = ttk_bs.Label(
            row1, text="高危: 0", bootstyle="warning", font=("Microsoft YaHei", 12, "bold")
        )
        self.high_cves_label.pack(side=LEFT, padx=(0, 20))
        
        # 第二行统计
        row2 = ttk_bs.Frame(stats_grid)
        row2.pack(fill=X, pady=2)
        
        self.medium_cves_label = ttk_bs.Label(
            row2, text="中危: 0", bootstyle="info", font=("Microsoft YaHei", 12, "bold")
        )
        self.medium_cves_label.pack(side=LEFT, padx=(0, 20))
        
        self.low_cves_label = ttk_bs.Label(
            row2, text="低危: 0", bootstyle="success", font=("Microsoft YaHei", 12, "bold")
        )
        self.low_cves_label.pack(side=LEFT, padx=(0, 20))
        
        self.avg_cvss_label = ttk_bs.Label(
            row2, text="平均CVSS: 0.0", bootstyle="secondary", font=("Microsoft YaHei", 12, "bold")
        )
        self.avg_cvss_label.pack(side=LEFT)
        
        # 结果列表
        list_frame = ttk_bs.LabelFrame(results_frame, text="CVE列表", padding=10)
        list_frame.pack(fill=BOTH, expand=True)
        
        # 创建Treeview
        columns = ("CVE ID", "严重性", "CVSS", "发布日期", "描述")
        self.results_tree = ttk_bs.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=15,
            bootstyle="primary"
        )

        # 配置Treeview的默认样式 - 确保文字为黑色
        style = ttk_bs.Style()
        style.configure("Treeview", foreground="#000000")
        style.configure("Treeview.Heading", foreground="#000000")
        
        # 设置列标题和宽度
        self.results_tree.heading("CVE ID", text="CVE ID")
        self.results_tree.heading("严重性", text="严重性")
        self.results_tree.heading("CVSS", text="CVSS")
        self.results_tree.heading("发布日期", text="发布日期")
        self.results_tree.heading("描述", text="描述")

        self.results_tree.column("CVE ID", width=140, minwidth=120)
        self.results_tree.column("严重性", width=100, minwidth=80)
        self.results_tree.column("CVSS", width=80, minwidth=60)
        self.results_tree.column("发布日期", width=120, minwidth=100)
        self.results_tree.column("描述", width=500, minwidth=300)
        
        # 添加滚动条
        scrollbar = ttk_bs.Scrollbar(list_frame, orient=VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 结果操作按钮
        results_control_frame = ttk_bs.Frame(results_frame)
        results_control_frame.pack(fill=X, pady=(15, 0))
        
        ttk_bs.Button(
            results_control_frame,
            text="📄 导出CSV",
            command=self.export_csv,
            bootstyle="success",
            width=12
        ).pack(side=LEFT, padx=(0, 5))

        ttk_bs.Button(
            results_control_frame,
            text="📋 导出JSON",
            command=self.export_json,
            bootstyle="primary",
            width=12
        ).pack(side=LEFT, padx=(0, 5))

        ttk_bs.Button(
            results_control_frame,
            text="📝 导出TXT",
            command=self.export_txt,
            bootstyle="info",
            width=12
        ).pack(side=LEFT, padx=(0, 5))

        ttk_bs.Button(
            results_control_frame,
            text="📊 导出Excel",
            command=self.export_excel,
            bootstyle="warning",
            width=12
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk_bs.Button(
            results_control_frame,
            text="🔍 查看详情",
            command=self.view_details,
            bootstyle="info",
            width=12
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_bs.Button(
            results_control_frame,
            text="🗑️ 清空结果",
            command=self.clear_results,
            bootstyle="danger",
            width=12
        ).pack(side=LEFT)
    
    def create_monitor_tab(self):
        """创建监控标签页"""
        monitor_frame = ttk_bs.Frame(self.notebook, padding=20)
        self.notebook.add(monitor_frame, text="📈 实时监控")
        
        # 监控状态
        status_frame = ttk_bs.LabelFrame(monitor_frame, text="监控状态", padding=15)
        status_frame.pack(fill=X, pady=(0, 15))
        
        self.monitor_status_label = ttk_bs.Label(
            status_frame,
            text="🔴 监控未启动",
            font=("Microsoft YaHei", 14, "bold"),
            bootstyle="danger"
        )
        self.monitor_status_label.pack()
        
        # 监控控制
        monitor_control_frame = ttk_bs.Frame(monitor_frame)
        monitor_control_frame.pack(fill=X, pady=(0, 15))
        
        self.start_monitor_button = ttk_bs.Button(
            monitor_control_frame,
            text="🚀 启动监控",
            command=self.start_monitoring,
            bootstyle="success",
            width=15
        )
        self.start_monitor_button.pack(side=LEFT, padx=(0, 10))
        
        self.stop_monitor_button = ttk_bs.Button(
            monitor_control_frame,
            text="⏹️ 停止监控",
            command=self.stop_monitoring,
            bootstyle="danger",
            width=15,
            state=DISABLED
        )
        self.stop_monitor_button.pack(side=LEFT)
        
        # 监控日志
        monitor_log_frame = ttk_bs.LabelFrame(monitor_frame, text="监控日志", padding=10)
        monitor_log_frame.pack(fill=BOTH, expand=True)
        
        self.monitor_log_text = ScrolledText(
            monitor_log_frame,
            height=20,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.monitor_log_text.pack(fill=BOTH, expand=True)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk_bs.Frame(parent)
        status_frame.pack(fill=X, side=BOTTOM, pady=(10, 0))
        
        # 分隔线
        separator = ttk_bs.Separator(status_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(0, 5))
        
        # 状态信息
        self.status_label = ttk_bs.Label(
            status_frame,
            text="就绪",
            bootstyle="secondary"
        )
        self.status_label.pack(side=LEFT)
        
        # 时间显示
        self.time_label = ttk_bs.Label(
            status_frame,
            text="",
            bootstyle="secondary"
        )
        self.time_label.pack(side=RIGHT)
        
        # 更新时间
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def on_mode_change(self):
        """爬取模式改变时的处理"""
        if self.crawl_mode.get() == "normal":
            self.normal_params_frame.pack(fill=X)
            self.incremental_params_frame.pack_forget()
        else:
            self.normal_params_frame.pack_forget()
            self.incremental_params_frame.pack(fill=X)
    
    def log_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据级别设置颜色
        color_map = {
            "INFO": "white",
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "DEBUG": "cyan"
        }
        
        color = color_map.get(level, "white")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # 添加到日志文本框
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # 更新状态栏
        self.status_label.config(text=message[:50] + "..." if len(message) > 50 else message)
        
        # 强制更新界面
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("日志已清空", "INFO")
    
    def get_current_config(self) -> CrawlConfig:
        """获取当前配置"""
        try:
            config = CrawlConfig(
                timeout=int(self.timeout_var.get()),
                delay_range=(int(self.delay_min_var.get()), int(self.delay_max_var.get())),
                data_dir=self.data_dir_var.get(),
                user_agent=self.user_agent_var.get(),
                cache_ttl=int(self.cache_ttl_var.get()),
                headless=not self.show_browser_var.get()
            )
            return config
        except ValueError as e:
            self.log_message(f"配置参数错误: {e}", "ERROR")
            return CrawlConfig()
    
    def start_crawling(self):
        """开始爬取"""
        if self.is_crawling:
            return

        self.is_crawling = True
        self.stop_requested = False
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.progress_bar.start()

        # 获取配置
        config = self.get_current_config()

        # 在新线程中运行爬取
        self.crawler_thread = threading.Thread(
            target=self.run_crawler,
            args=(config,),
            daemon=True
        )
        self.crawler_thread.start()
    
    def run_crawler(self, config: CrawlConfig):
        """运行爬虫（在后台线程中）"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 运行可中断的爬取任务
            results = loop.run_until_complete(self._run_interruptible_crawler(config))

            # 检查是否被中断
            if self.stop_requested:
                self.root.after(0, self.on_crawl_stopped)
            else:
                # 更新结果
                self.root.after(0, self.on_crawl_complete, results)

        except Exception as e:
            if not self.stop_requested:
                self.root.after(0, self.on_crawl_error, str(e))
        finally:
            loop.close()

    async def _run_interruptible_crawler(self, config: CrawlConfig):
        """运行可中断的爬虫"""
        try:
            # 创建爬虫实例
            self.current_crawler = AliyunCVECrawler(config)

            async with self.current_crawler as crawler:
                if self.crawl_mode.get() == "normal":
                    # 常规爬取
                    max_pages = int(self.max_pages_var.get())
                    start_page = int(self.start_page_var.get())

                    self.log_message(f"开始常规爬取，页数: {max_pages}，起始页: {start_page}", "INFO")

                    # 分页爬取，每页检查是否需要停止
                    all_results = []
                    for page in range(start_page, start_page + max_pages):
                        if self.stop_requested:
                            self.log_message("收到停止请求，正在安全退出...", "WARNING")
                            break

                        try:
                            # 爬取单页
                            page_results = await crawler.crawl_all(start_page=page, max_pages=1)
                            all_results.extend(page_results)

                            # 更新进度信息
                            self.log_message(f"已完成第 {page} 页，获得 {len(page_results)} 个CVE", "INFO")

                            # 短暂延迟，给停止检查机会
                            await asyncio.sleep(0.1)

                        except Exception as e:
                            self.log_message(f"爬取第 {page} 页失败: {e}", "ERROR")
                            continue

                    return all_results

                else:
                    # 增量爬取
                    days = int(self.days_var.get())
                    self.log_message(f"开始增量爬取，天数: {days}", "INFO")

                    # 增量爬取通常较快，但仍然检查停止请求
                    if self.stop_requested:
                        return []

                    return await crawler.crawl_incremental()

        except Exception as e:
            if not self.stop_requested:
                raise e
            return []
    
    def on_crawl_complete(self, results: List[CVEInfo]):
        """爬取完成的处理"""
        self.crawl_results = results
        self.is_crawling = False
        self.stop_requested = False
        self.current_crawler = None

        self.start_button.config(state=NORMAL)
        self.stop_button.config(text="⏹️ 停止爬取", state=DISABLED)
        self.progress_bar.stop()

        self.log_message(f"爬取完成！获得 {len(results)} 个CVE", "SUCCESS")

        # 更新结果显示
        self.update_results_display()

        # 切换到结果标签页
        self.notebook.select(2)
    
    def on_crawl_error(self, error_msg: str):
        """爬取错误的处理"""
        self.is_crawling = False
        self.stop_requested = False
        self.current_crawler = None

        self.start_button.config(state=NORMAL)
        self.stop_button.config(text="⏹️ 停止爬取", state=DISABLED)
        self.progress_bar.stop()

        self.log_message(f"爬取失败: {error_msg}", "ERROR")
        Messagebox.show_error("爬取失败", f"爬取过程中发生错误:\n{error_msg}")

    def on_crawl_stopped(self):
        """爬取被停止的处理"""
        self.is_crawling = False
        self.stop_requested = False
        self.current_crawler = None

        self.start_button.config(state=NORMAL)
        self.stop_button.config(text="⏹️ 停止爬取", state=DISABLED)
        self.progress_bar.stop()

        self.log_message("爬取已被用户停止", "WARNING")
    
    def stop_crawling(self):
        """停止爬取"""
        if not self.is_crawling:
            return

        # 设置停止标志
        self.stop_requested = True
        self.log_message("正在停止爬取，请稍候...", "WARNING")

        # 更新按钮状态
        self.stop_button.config(text="⏳ 停止中...", state=DISABLED)

        # 如果有当前爬虫实例，请求停止
        if self.current_crawler:
            try:
                self.current_crawler.request_stop()
                self.log_message("已向爬虫发送停止信号", "INFO")
            except Exception as e:
                self.log_message(f"发送停止信号失败: {e}", "ERROR")
    
    def update_results_display(self):
        """更新结果显示"""
        # 清空现有数据
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not self.crawl_results:
            return
        
        # 统计信息
        total = len(self.crawl_results)
        critical = sum(1 for cve in self.crawl_results if cve.severity == "CRITICAL")
        high = sum(1 for cve in self.crawl_results if cve.severity == "HIGH")
        medium = sum(1 for cve in self.crawl_results if cve.severity == "MEDIUM")
        low = sum(1 for cve in self.crawl_results if cve.severity == "LOW")
        
        cvss_scores = [cve.cvss_score for cve in self.crawl_results if cve.cvss_score > 0]
        avg_cvss = sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0
        
        # 更新统计标签
        self.total_cves_label.config(text=f"总CVE数: {total}")
        self.critical_cves_label.config(text=f"严重: {critical}")
        self.high_cves_label.config(text=f"高危: {high}")
        self.medium_cves_label.config(text=f"中危: {medium}")
        self.low_cves_label.config(text=f"低危: {low}")
        self.avg_cvss_label.config(text=f"平均CVSS: {avg_cvss:.1f}")
        
        # 添加CVE数据到树形视图
        for cve in self.crawl_results:
            # 根据严重性设置标签
            severity_tags = {
                "CRITICAL": "critical",
                "HIGH": "high", 
                "MEDIUM": "medium",
                "LOW": "low"
            }
            
            tag = severity_tags.get(cve.severity, "")
            
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    cve.cve_id,
                    cve.severity,
                    f"{cve.cvss_score:.1f}",
                    cve.published_date.strftime("%Y-%m-%d"),
                    cve.description[:100] + "..." if len(cve.description) > 100 else cve.description
                ),
                tags=(tag,)
            )
        
        # 配置标签颜色 - 使用更深的背景色和黑色字体
        self.results_tree.tag_configure("critical", background="#ffcdd2", foreground="#000000")
        self.results_tree.tag_configure("high", background="#ffe0b2", foreground="#000000")
        self.results_tree.tag_configure("medium", background="#bbdefb", foreground="#000000")
        self.results_tree.tag_configure("low", background="#c8e6c9", foreground="#000000")
    
    def browse_data_dir(self):
        """浏览数据目录"""
        directory = filedialog.askdirectory(
            title="选择数据存储目录",
            initialdir=self.data_dir_var.get()
        )
        if directory:
            self.data_dir_var.set(directory)
    
    def save_config(self):
        """保存配置"""
        try:
            config_data = {
                "timeout": int(self.timeout_var.get()),
                "delay_min": int(self.delay_min_var.get()),
                "delay_max": int(self.delay_max_var.get()),
                "data_dir": self.data_dir_var.get(),
                "user_agent": self.user_agent_var.get(),
                "cache_ttl": int(self.cache_ttl_var.get())
            }
            
            config_file = Path("gui_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.log_message("配置已保存", "SUCCESS")
            Messagebox.show_info("保存成功", "配置已保存到 gui_config.json")
            
        except Exception as e:
            self.log_message(f"保存配置失败: {e}", "ERROR")
            Messagebox.show_error("保存失败", f"保存配置时发生错误:\n{e}")
    
    def load_config(self):
        """加载配置"""
        try:
            config_file = Path("gui_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self.timeout_var.set(str(config_data.get("timeout", 30)))
                self.delay_min_var.set(str(config_data.get("delay_min", 1)))
                self.delay_max_var.set(str(config_data.get("delay_max", 3)))
                self.data_dir_var.set(config_data.get("data_dir", "./data/aliyun_cve"))
                self.user_agent_var.set(config_data.get("user_agent", "Mozilla/5.0..."))
                self.cache_ttl_var.set(str(config_data.get("cache_ttl", 86400)))
                
                self.log_message("配置已加载", "SUCCESS")
        except Exception as e:
            self.log_message(f"加载配置失败: {e}", "WARNING")
    
    def load_config_file(self):
        """从文件加载配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新界面
                if "crawler" in config_data:
                    crawler_config = config_data["crawler"]
                    self.timeout_var.set(str(crawler_config.get("timeout", 30)))
                    self.data_dir_var.set(crawler_config.get("data_dir", "./data/aliyun_cve"))
                    
                    delay_range = crawler_config.get("delay_range", [1, 3])
                    self.delay_min_var.set(str(delay_range[0]))
                    self.delay_max_var.set(str(delay_range[1]))
                
                self.log_message(f"从 {file_path} 加载配置成功", "SUCCESS")
                Messagebox.show_info("加载成功", "配置文件加载成功")
                
            except Exception as e:
                self.log_message(f"加载配置文件失败: {e}", "ERROR")
                Messagebox.show_error("加载失败", f"加载配置文件时发生错误:\n{e}")
    
    def reset_config(self):
        """重置配置"""
        if Messagebox.show_question("重置配置", "确定要重置所有配置到默认值吗？"):
            self.timeout_var.set("30")
            self.delay_min_var.set("1")
            self.delay_max_var.set("3")
            self.data_dir_var.set("./data/aliyun_cve")
            self.user_agent_var.set("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            self.cache_ttl_var.set("86400")
            
            self.log_message("配置已重置", "INFO")
    
    def export_config(self):
        """导出配置"""
        file_path = filedialog.asksaveasfilename(
            title="导出配置",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                config_data = {
                    "crawler": {
                        "timeout": int(self.timeout_var.get()),
                        "delay_range": [int(self.delay_min_var.get()), int(self.delay_max_var.get())],
                        "data_dir": self.data_dir_var.get(),
                        "user_agent": self.user_agent_var.get(),
                        "cache_ttl": int(self.cache_ttl_var.get())
                    }
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                self.log_message(f"配置已导出到 {file_path}", "SUCCESS")
                Messagebox.show_info("导出成功", "配置已成功导出")
                
            except Exception as e:
                self.log_message(f"导出配置失败: {e}", "ERROR")
                Messagebox.show_error("导出失败", f"导出配置时发生错误:\n{e}")
    
    def export_csv(self):
        """导出CSV"""
        if not self.crawl_results:
            Messagebox.show_warning("无数据", "没有可导出的数据")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    
                    # 写入标题
                    writer.writerow(["CVE ID", "严重性", "CVSS分数", "发布日期", "描述", "参考链接"])
                    
                    # 写入数据
                    for cve in self.crawl_results:
                        writer.writerow([
                            cve.cve_id,
                            cve.severity,
                            cve.cvss_score,
                            cve.published_date.strftime("%Y-%m-%d"),
                            cve.description,
                            "; ".join(cve.references)
                        ])
                
                self.log_message(f"CSV已导出到 {file_path}", "SUCCESS")
                Messagebox.show_info("导出成功", "CSV文件已成功导出")
                
            except Exception as e:
                self.log_message(f"导出CSV失败: {e}", "ERROR")
                Messagebox.show_error("导出失败", f"导出CSV时发生错误:\n{e}")
    
    def export_json(self):
        """导出JSON"""
        if not self.crawl_results:
            Messagebox.show_warning("无数据", "没有可导出的数据")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                data = {
                    "export_time": datetime.now().isoformat(),
                    "total_count": len(self.crawl_results),
                    "cves": [cve.to_dict() for cve in self.crawl_results]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                self.log_message(f"JSON已导出到 {file_path}", "SUCCESS")
                Messagebox.show_info("导出成功", "JSON文件已成功导出")
                
            except Exception as e:
                self.log_message(f"导出JSON失败: {e}", "ERROR")
                Messagebox.show_error("导出失败", f"导出JSON时发生错误:\n{e}")

    def export_txt(self):
        """导出TXT"""
        if not self.crawl_results:
            Messagebox.show_warning("无数据", "没有可导出的数据")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 写入标题
                    f.write("=" * 80 + "\n")
                    f.write("AliyunCVE_Crawler 爬取结果\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"总计CVE数量: {len(self.crawl_results)}\n")
                    f.write("=" * 80 + "\n\n")

                    # 写入CVE数据
                    for i, cve in enumerate(self.crawl_results, 1):
                        f.write(f"{i}. {cve.cve_id}\n")
                        f.write(f"   严重性: {cve.severity}\n")
                        f.write(f"   CVSS分数: {cve.cvss_score}\n")
                        f.write(f"   发布日期: {cve.published_date.strftime('%Y-%m-%d')}\n")
                        f.write(f"   描述: {cve.description}\n")
                        if cve.references:
                            f.write(f"   参考链接: {'; '.join(cve.references[:3])}{'...' if len(cve.references) > 3 else ''}\n")
                        f.write("-" * 60 + "\n\n")

                self.log_message(f"TXT已导出到 {file_path}", "SUCCESS")
                Messagebox.show_info("导出成功", "TXT文件已成功导出")

            except Exception as e:
                self.log_message(f"导出TXT失败: {e}", "ERROR")
                Messagebox.show_error("导出失败", f"导出TXT时发生错误:\n{e}")

    def export_excel(self):
        """导出Excel"""
        if not self.crawl_results:
            Messagebox.show_warning("无数据", "没有可导出的数据")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # 尝试导入pandas和openpyxl
                try:
                    import pandas as pd
                except ImportError:
                    Messagebox.show_error("缺少依赖", "导出Excel需要安装pandas库:\npip install pandas openpyxl")
                    return

                # 准备数据
                data = []
                for cve in self.crawl_results:
                    data.append({
                        'CVE ID': cve.cve_id,
                        '严重性': cve.severity,
                        'CVSS分数': cve.cvss_score,
                        '发布日期': cve.published_date.strftime('%Y-%m-%d'),
                        '修改日期': cve.modified_date.strftime('%Y-%m-%d'),
                        '描述': cve.description,
                        '受影响产品': '; '.join(cve.affected_products),
                        'CWE ID': '; '.join(cve.cwe_ids),
                        '参考链接': '; '.join(cve.references[:5])  # 限制前5个链接
                    })

                # 创建DataFrame
                df = pd.DataFrame(data)

                # 导出到Excel
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='CVE数据', index=False)

                    # 获取工作表
                    worksheet = writer.sheets['CVE数据']

                    # 调整列宽
                    column_widths = {
                        'A': 15,  # CVE ID
                        'B': 10,  # 严重性
                        'C': 10,  # CVSS分数
                        'D': 12,  # 发布日期
                        'E': 12,  # 修改日期
                        'F': 50,  # 描述
                        'G': 30,  # 受影响产品
                        'H': 15,  # CWE ID
                        'I': 40   # 参考链接
                    }

                    for col, width in column_widths.items():
                        worksheet.column_dimensions[col].width = width

                self.log_message(f"Excel已导出到 {file_path}", "SUCCESS")
                Messagebox.show_info("导出成功", "Excel文件已成功导出")

            except Exception as e:
                self.log_message(f"导出Excel失败: {e}", "ERROR")
                Messagebox.show_error("导出失败", f"导出Excel时发生错误:\n{e}")

    def view_details(self):
        """查看CVE详情"""
        selection = self.results_tree.selection()
        if not selection:
            Messagebox.show_warning("未选择", "请先选择一个CVE条目")
            return
        
        item = self.results_tree.item(selection[0])
        cve_id = item['values'][0]
        
        # 查找对应的CVE对象
        cve = next((c for c in self.crawl_results if c.cve_id == cve_id), None)
        if not cve:
            return
        
        # 创建详情窗口
        self.show_cve_details(cve)
    
    def show_cve_details(self, cve: CVEInfo):
        """显示CVE详情窗口"""
        detail_window = ttk_bs.Toplevel(self.root)
        detail_window.title(f"CVE详情 - {cve.cve_id}")
        detail_window.geometry("800x600")
        detail_window.resizable(True, True)
        
        # 创建滚动文本框
        detail_text = ScrolledText(
            detail_window,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 11),
            padding=20
        )
        detail_text.pack(fill=BOTH, expand=True)
        
        # 构建详情内容
        details = f"""CVE详情信息

CVE ID: {cve.cve_id}
严重性: {cve.severity}
CVSS分数: {cve.cvss_score}
发布日期: {cve.published_date.strftime('%Y-%m-%d %H:%M:%S')}
修改日期: {cve.modified_date.strftime('%Y-%m-%d %H:%M:%S')}

描述:
{cve.description}

受影响产品:
{', '.join(cve.affected_products) if cve.affected_products else '无'}

CWE ID:
{', '.join(cve.cwe_ids) if cve.cwe_ids else '无'}

参考链接:
"""
        
        for ref in cve.references:
            details += f"• {ref}\n"
        
        detail_text.insert(tk.END, details)
        detail_text.config(state=DISABLED)
    
    def clear_results(self):
        """清空结果"""
        if Messagebox.show_question("清空结果", "确定要清空所有爬取结果吗？"):
            self.crawl_results = []
            self.update_results_display()
            self.log_message("结果已清空", "INFO")
    
    def start_monitoring(self):
        """启动监控"""
        self.start_monitor_button.config(state=DISABLED)
        self.stop_monitor_button.config(state=NORMAL)
        self.monitor_status_label.config(text="🟢 监控运行中", bootstyle="success")
        
        self.monitor_log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 监控服务已启动\n")
        self.monitor_log_text.see(tk.END)
    
    def stop_monitoring(self):
        """停止监控"""
        self.start_monitor_button.config(state=NORMAL)
        self.stop_monitor_button.config(state=DISABLED)
        self.monitor_status_label.config(text="🔴 监控未启动", bootstyle="danger")
        
        self.monitor_log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 监控服务已停止\n")
        self.monitor_log_text.see(tk.END)
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = CVECrawlerGUI()
        app.run()
    except Exception as e:
        print(f"启动GUI失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
