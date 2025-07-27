# 贡献指南

感谢您对AliyunCVE_Crawler项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 🚀 快速开始

### 1. Fork 项目

点击项目页面右上角的 "Fork" 按钮，将项目复制到您的GitHub账户。

### 2. 克隆到本地

```bash
git clone https://github.com/vistaminc/AliyunCVE_Crawler.git
cd AliyunCVE_Crawler
```

### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 安装浏览器驱动
playwright install chromium
```

### 4. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b bugfix/your-bugfix-name
```

## 📋 开发规范

### 代码风格

我们使用以下工具来保持代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码检查
- **isort**: 导入排序

```bash
# 格式化代码
black main.py

# 检查代码风格
flake8 main.py

# 排序导入
isort main.py
```

### 提交规范

请使用清晰的提交信息，遵循以下格式：

```
类型(范围): 简短描述

详细描述（可选）

关闭的Issue（可选）
```

**类型说明：**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(crawler): 添加增量爬取功能

- 支持基于日期的增量爬取
- 添加缓存机制避免重复爬取
- 优化内存使用

Closes #123
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_crawler.py

# 运行测试并生成覆盖率报告
pytest --cov=main
```

### 编写测试

为新功能编写测试是必需的。测试文件应该放在 `tests/` 目录下。

```python
# tests/test_new_feature.py
import pytest
from main import AliyunCVECrawler, CrawlConfig

@pytest.mark.asyncio
async def test_new_feature():
    config = CrawlConfig(max_pages=1)
    async with AliyunCVECrawler(config) as crawler:
        result = await crawler.new_feature()
        assert result is not None
```

## 📝 文档

### 更新文档

如果您的更改影响了用户接口，请同时更新相关文档：

- `README.md`: 项目概述和基本使用
- `USAGE.md`: 详细使用说明
- 代码注释: 确保代码有适当的注释

### 文档风格

- 使用清晰、简洁的语言
- 提供实际的代码示例
- 包含必要的警告和注意事项

## 🐛 报告Bug

### Bug报告模板

请使用以下模板报告Bug：

```markdown
## Bug描述
简要描述遇到的问题

## 复现步骤
1. 执行命令 `python main.py --pages 5`
2. 等待爬取完成
3. 查看输出结果

## 期望行为
描述您期望发生的情况

## 实际行为
描述实际发生的情况

## 环境信息
- 操作系统: Windows 10
- Python版本: 3.9.0
- 项目版本: v1.0.0

## 错误日志
```
粘贴相关的错误日志
```

## 额外信息
其他可能有用的信息
```

## 💡 功能建议

### 功能请求模板

```markdown
## 功能描述
简要描述建议的新功能

## 使用场景
描述这个功能的使用场景和价值

## 建议的实现方式
如果有想法，可以描述可能的实现方式

## 替代方案
是否有其他可行的替代方案
```

## 🔄 Pull Request流程

### 1. 准备工作

- 确保您的分支是基于最新的main分支
- 运行所有测试并确保通过
- 更新相关文档

### 2. 提交PR

- 使用清晰的标题描述您的更改
- 在描述中详细说明更改内容
- 链接相关的Issue
- 添加适当的标签

### 3. PR模板

```markdown
## 更改类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

## 更改描述
详细描述您的更改内容

## 测试
- [ ] 添加了新的测试
- [ ] 所有现有测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码遵循项目风格指南
- [ ] 自我审查了代码
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 没有引入新的警告

## 相关Issue
Closes #123
```

### 4. 代码审查

- 耐心等待维护者的审查
- 积极响应审查意见
- 根据反馈进行必要的修改

## 🏷️ 发布流程

### 版本号规范

我们使用语义化版本控制 (SemVer)：

- `MAJOR.MINOR.PATCH`
- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的Bug修复

### 发布检查清单

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG已更新
- [ ] 版本号已更新

## 🤝 社区准则

### 行为准则

- 尊重所有参与者
- 使用友善和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情

### 沟通渠道

- GitHub Issues: 报告Bug和功能请求
- GitHub Discussions: 一般讨论和问题
- Pull Requests: 代码贡献

## 📚 资源

### 有用的链接

- [Python异步编程指南](https://docs.python.org/3/library/asyncio.html)
- [Playwright文档](https://playwright.dev/python/)
- [语义化版本控制](https://semver.org/lang/zh-CN/)

### 学习资源

- [Git使用指南](https://git-scm.com/book/zh/v2)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [编写好的提交信息](https://chris.beams.io/posts/git-commit/)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

如果您有任何问题，请随时通过GitHub Issues联系我们。我们很乐意帮助您开始贡献！
