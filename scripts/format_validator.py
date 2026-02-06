#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档格式和结构合规性检查器
验证Markdown文档的格式规范和结构完整性
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class FormatValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.format_issues = []
        self.structure_issues = []
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict:
        """加载验证规则"""
        return {
            'required_headers': ['## 目录', '## 核心理念', '## 导航与关联'],
            'forbidden_patterns': [
                r'TODO:',  # 未完成标记
                r'FIXME:', # 需要修复标记
                r'XXX:',   # 注意标记
            ],
            'required_patterns': [
                r'^#\s+.+',           # 必须有标题
                r'\[.*?\]\(.*?\)',    # 链接格式
            ],
            'structure_patterns': {
                'navigation_section': r'## 导航与关联',
                'change_log': r'>\s*变更记录',
                'core_summary': r'>\s*\*\*核心摘要\*\*'
            }
        }
    
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        exclude_dirs = {'.git', 'node_modules', 'scripts'}
        
        for file_path in self.project_root.rglob("*.md"):
            if not any(part in exclude_dirs for part in file_path.parts):
                # 排除日志和临时文件
                if 'logs/' not in str(file_path) or file_path.name in ['CHANGE_LOG.md']:
                    md_files.append(file_path)
        
        return sorted(md_files)
    
    def validate_file_format(self, file_path: Path):
        """验证单个文件的格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 基本格式检查
            self._check_basic_format(file_path, content, lines)
            
            # 结构完整性检查
            self._check_structure_integrity(file_path, content, lines)
            
            # 内容质量检查
            self._check_content_quality(file_path, content, lines)
            
        except Exception as e:
            self.format_issues.append({
                'file': file_path,
                'issue': f'文件读取错误: {e}',
                'severity': 'high'
            })
    
    def _check_basic_format(self, file_path: Path, content: str, lines: List[str]):
        """检查基本格式"""
        # 检查是否有标题
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            self.format_issues.append({
                'file': file_path,
                'issue': '缺少文档标题',
                'severity': 'high'
            })
        
        # 检查编码和特殊字符
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            self.format_issues.append({
                'file': file_path,
                'issue': '文件包含非法字符或编码问题',
                'severity': 'high'
            })
        
        # 检查行长度（超过120字符的行）
        for i, line in enumerate(lines, 1):
            if len(line) > 120 and not line.startswith('    ') and 'http' not in line:
                self.format_issues.append({
                    'file': file_path,
                    'line': i,
                    'issue': f'行长度过长 ({len(line)} 字符)',
                    'severity': 'low'
                })
    
    def _check_structure_integrity(self, file_path: Path, content: str, lines: List[str]):
        """检查结构完整性"""
        filename = file_path.name
        
        # 检查核心文档的必需结构
        if re.match(r'^\d{2}-.*\.md$', filename):
            # 检查导航与关联部分
            if not re.search(self.validation_rules['structure_patterns']['navigation_section'], content):
                self.structure_issues.append({
                    'file': file_path,
                    'issue': '缺少"导航与关联"部分',
                    'severity': 'medium'
                })
            
            # 检查变更记录
            if not re.search(self.validation_rules['structure_patterns']['change_log'], content):
                self.structure_issues.append({
                    'file': file_path,
                    'issue': '缺少变更记录部分',
                    'severity': 'low'
                })
            
            # 检查核心摘要
            if not re.search(self.validation_rules['structure_patterns']['core_summary'], content):
                self.structure_issues.append({
                    'file': file_path,
                    'issue': '缺少核心摘要部分',
                    'severity': 'low'
                })
        
        # 检查目录结构
        if filename == 'README.md':
            if not re.search(r'## 目录', content):
                self.structure_issues.append({
                    'file': file_path,
                    'issue': 'README缺少目录部分',
                    'severity': 'high'
                })
    
    def _check_content_quality(self, file_path: Path, content: str, lines: List[str]):
        """检查内容质量"""
        # 检查禁止的标记
        for pattern in self.validation_rules['forbidden_patterns']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.format_issues.append({
                    'file': file_path,
                    'line': line_num,
                    'issue': f'发现禁止标记: {match.group()}',
                    'severity': 'medium'
                })
        
        # 检查链接格式
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for text, url in links:
            # 检查空链接文本
            if not text.strip():
                line_num = content.find(f']({url})') // len(content.split('\n')[0]) + 1
                self.format_issues.append({
                    'file': file_path,
                    'line': line_num,
                    'issue': '链接文本为空',
                    'severity': 'low'
                })
            
            # 检查相对链接的有效性
            if url.startswith('./') or url.startswith('../'):
                # 这里可以添加更详细的链接验证逻辑
                pass
    
    def validate_all_files(self):
        """验证所有文件"""
        print("[INFO] 开始验证文档格式和结构...")
        
        md_files = self.find_markdown_files()
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        for md_file in md_files:
            self.validate_file_format(md_file)
        
        self._print_results()
    
    def _print_results(self):
        """打印验证结果"""
        all_issues = self.format_issues + self.structure_issues
        
        # 按严重程度分类
        high_severity = [issue for issue in all_issues if issue.get('severity') == 'high']
        medium_severity = [issue for issue in all_issues if issue.get('severity') == 'medium']
        low_severity = [issue for issue in all_issues if issue.get('severity') == 'low']
        
        print(f"\n[RESULT] 格式验证完成:")
        print(f"   高严重性问题: {len(high_severity)}")
        print(f"   中严重性问题: {len(medium_severity)}")
        print(f"   低严重性问题: {len(low_severity)}")
        print(f"   总问题数: {len(all_issues)}")
        
        if all_issues:
            print(f"\n[LIST] 问题详情 (显示前15个):")
            for i, issue in enumerate(all_issues[:15], 1):
                rel_file = issue['file'].relative_to(self.project_root)
                line_info = f":{issue['line']}" if 'line' in issue else ""
                severity_icon = {'high': '[HIGH]', 'medium': '[MEDIUM]', 'low': '[LOW]'}[issue.get('severity', 'low')]
                
                print(f"   {i}. {severity_icon} {rel_file}{line_info}")
                print(f"      问题: {issue['issue']}")
                print()
            
            if len(all_issues) > 15:
                print(f"   ... 还有 {len(all_issues) - 15} 个问题")
        else:
            print("\n[SUCCESS] 所有文档格式都符合规范!")
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("# 文档格式验证报告")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"项目根目录: {self.project_root}")
        report.append("")
        
        all_issues = self.format_issues + self.structure_issues
        high_severity = [issue for issue in all_issues if issue.get('severity') == 'high']
        medium_severity = [issue for issue in all_issues if issue.get('severity') == 'medium']
        low_severity = [issue for issue in all_issues if issue.get('severity') == 'low']
        
        report.append("## 统计信息")
        report.append(f"- 检查文件数: {len(self.find_markdown_files())}")
        report.append(f"- 高严重性问题: {len(high_severity)}")
        report.append(f"- 中严重性问题: {len(medium_severity)}")
        report.append(f"- 低严重性问题: {len(low_severity)}")
        report.append(f"- 总问题数: {len(all_issues)}")
        report.append("")
        
        if all_issues:
            report.append("## 问题详情")
            for issue in all_issues:
                rel_file = issue['file'].relative_to(self.project_root)
                line_info = f":{issue.get('line', '')}" if issue.get('line') else ""
                report.append(f"- **文件**: {rel_file}{line_info}")
                report.append(f"  - **严重性**: {issue.get('severity', 'unknown')}")
                report.append(f"  - **问题**: {issue['issue']}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    validator = FormatValidator(project_root)
    validator.validate_all_files()
    
    # 生成报告文件
    report_content = validator.generate_report()
    report_file = Path(project_root) / "tmp" / "format_validation_report.md"
    
    try:
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[FILE] 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n[WARNING] 无法保存报告文件: {e}")

if __name__ == "__main__":
    main()