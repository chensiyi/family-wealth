# 自动化工具集

## 📋 工具目录

### 🔗 链接检查工具
**文件**: `link_checker.py`
**功能**: 验证项目中所有Markdown文件的内部链接有效性
**使用**: `python link_checker.py`
**输出**: 
- 控制台显示检查结果摘要
- `logs/link_check_report.md` 详细报告

### 📚 术语验证工具
**文件**: `term_validator.py`
**功能**: 检查术语使用的一致性和规范性
**使用**: `python term_validator.py`
**输出**:
- 控制台显示术语使用分析
- `logs/term_validation_report.md` 详细报告

### 📝 格式验证工具
**文件**: `format_validator.py`
**功能**: 验证Markdown文档的格式规范和结构完整性
**使用**: `python format_validator.py`
**检查内容**:
- 文档标题和基本结构
- 禁止标记(TODO/FIXME等)
- 链接格式规范性
- 行长度限制

### 🚀 统一检查入口
**文件**: `run_all_checks.py`
**功能**: 依次执行所有验证工具并生成综合报告
**使用**: `python run_all_checks.py`
**输出**:
- 依次执行所有工具
- `logs/quality_check_summary.md` 综合报告

## 🛠 使用方法

### 单独运行某个工具
```bash
# 在项目根目录下执行
python scripts/link_checker.py
python scripts/term_validator.py
python scripts/format_validator.py
```

### 运行全部检查
```bash
# 一键执行所有检查
python scripts/run_all_checks.py
```

## 📊 输出文件说明

所有工具的详细报告都会保存在 `logs/` 目录下：

- `link_check_report.md` - 链接有效性详细报告
- `term_validation_report.md` - 术语使用验证报告
- `format_validation_report.md` - 格式规范验证报告
- `quality_check_summary.md` - 综合检查汇总报告

## ⚙ 配置说明

### 链接检查器配置
- 自动排除 `.git` 和 `node_modules` 目录
- 支持相对链接和绝对链接验证
- 识别外部链接并单独统计

### 术语验证器配置
- 基于 `TERMINOLOGY_GLOSSARY.md` 文件
- 自动识别术语的多种变体形式
- 检查术语使用的标准性

### 格式验证器配置
- 检查核心文档必需结构
- 验证链接格式规范性
- 检测常见的格式问题

## 🎯 质量门禁建议

建议在以下时机运行这些工具：

1. **提交前检查**: 提交代码前运行全部检查
2. **定期维护**: 每周或每月定期运行
3. **重大修改后**: 架构调整后进行全面检查
4. **新成员入职**: 帮助新成员了解项目规范

## 🔧 扩展开发

如需添加新的验证规则：

1. 修改对应工具的验证规则配置
2. 在 `run_all_checks.py` 中注册新工具
3. 更新本文档说明

---
*这些工具旨在提高项目文档质量和维护效率*