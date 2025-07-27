# 阿里云CVE爬虫 Makefile

.PHONY: help install install-dev test lint format clean crawl monitor

# 默认目标
help:
	@echo "可用命令:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  gui          - 启动图形界面"
	@echo "  test         - 运行测试"
	@echo "  test-stop    - 测试停止功能"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  crawl        - 运行爬虫（5页）"
	@echo "  crawl-full   - 运行完整爬虫（20页）"
	@echo "  monitor      - 运行监控服务"

# 安装依赖
install:
	pip install -r requirements.txt
	playwright install chromium

# 安装开发依赖
install-dev: install
	pip install -r requirements-dev.txt

# 启动图形界面
gui:
	python run_gui.py

# 运行测试
test:
	pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov:
	pytest tests/ -v --cov=main --cov-report=html

# 测试停止功能
test-stop:
	python test_stop_functionality.py

# 代码检查
lint:
	flake8 main.py examples/ tests/
	mypy main.py --ignore-missing-imports

# 代码格式化
format:
	black main.py examples/ tests/
	isort main.py examples/ tests/

# 清理临时文件
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# 运行爬虫（测试）
crawl:
	python main.py --pages 5

# 运行完整爬虫
crawl-full:
	python main.py --pages 20

# 增量爬取
crawl-incremental:
	python main.py --incremental --days 7

# 运行监控服务
monitor:
	python examples/monitoring_service.py

# 持续监控
monitor-continuous:
	python examples/monitoring_service.py --continuous

# 构建包
build:
	python setup.py sdist bdist_wheel

# 安装本地包
install-local:
	pip install -e .

# 检查代码质量
quality: lint test

# 完整的开发环境设置
setup-dev: install-dev
	@echo "开发环境设置完成！"
	@echo "运行 'make crawl' 测试爬虫功能"

# 项目初始化
init: setup-dev
	mkdir -p data/aliyun_cve
	mkdir -p monitoring_data
	mkdir -p logs
	cp config.example.json config.json
	@echo "项目初始化完成！"
	@echo "请根据需要修改 config.json 配置文件"
