#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
术语使用一致性验证器
检查项目中术语使用的一致性和规范性
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class TermValidator:
    def __init__(self, project_root: str = ".", glossary_file: str = "TERMINOLOGY_GLOSSARY.md"):
        self.project_root = Path(project_root)
        self.glossary_file = Path(glossary_file)
        self.terms_dict = {}
        self.term_usage = defaultdict(list)
        self.inconsistencies = []
        self.unrecognized_terms = []
        
    def load_glossary(self) -> bool:
        """加载术语词汇表"""
        try:
            glossary_path = self.project_root / self.glossary_file
            if not glossary_path.exists():
                print(f"❌ 术语词汇表文件不存在: {glossary_path}")
                return False
            
            with open(glossary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析术语词汇表
            # 匹配术语定义格式: #### 术语名称 (English Name)
            term_pattern = r'####\s+(.+?)\s*(?:$|\n)'
            terms = re.findall(term_pattern, content)
            
            # 提取术语及其变体
            for term_line in terms:
                # 分离中文术语和英文术语
                parts = term_line.split('(')
                chinese_term = parts[0].strip()
                english_term = None
                
                if len(parts) > 1:
                    english_term = parts[1].rstrip(')').strip()
                
                # 添加到术语字典
                self.terms_dict[chinese_term] = {
                    'english': english_term,
                    'variants': self._generate_variants(chinese_term, english_term)
                }
            
            print(f"[SUCCESS] 成功加载 {len(self.terms_dict)} 个术语定义")
            return True
            
        except Exception as e:
            print(f"[ERROR] 加载术语词汇表失败: {e}")
            return False
    
    def _generate_variants(self, chinese_term: str, english_term: str = None) -> List[str]:
        """生成术语的可能变体"""
        variants = [chinese_term]
        
        # 中文术语变体
        if len(chinese_term) > 1:
            # 添加去掉"的"、"和"等助词的变体
            cleaned = re.sub(r'[的了着过给在]', '', chinese_term)
            if cleaned != chinese_term:
                variants.append(cleaned)
        
        # 英文术语变体
        if english_term:
            variants.append(english_term.lower())
            # 添加驼峰命名和下划线命名变体
            if ' ' in english_term:
                camel_case = ''.join(word.capitalize() for word in english_term.split())
                snake_case = english_term.replace(' ', '_').lower()
                variants.extend([camel_case, snake_case])
        
        return list(set(variants))  # 去重
    
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        exclude_dirs = {'.git', 'node_modules', 'scripts', 'logs'}
        
        for file_path in self.project_root.rglob("*.md"):
            if not any(part in exclude_dirs for part in file_path.parts):
                md_files.append(file_path)
        
        return sorted(md_files)
    
    def extract_terms_from_file(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """从文件中提取可能的术语"""
        terms_found = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # 跳过代码块和链接
                if line.strip().startswith('```') or '](' in line:
                    continue
                
                # 在术语字典中查找匹配的术语
                for term, term_info in self.terms_dict.items():
                    for variant in term_info['variants']:
                        if variant in line and len(variant) > 1:  # 避免单字符匹配
                            # 检查是否是完整词汇匹配（前后不是字母数字）
                            pattern = r'(?<!\w)' + re.escape(variant) + r'(?!\w)'
                            if re.search(pattern, line):
                                terms_found.append((term, line_num, line.strip()))
                                break
            
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
        
        return terms_found
    
    def validate_term_usage(self):
        """验证术语使用一致性"""
        print("[INFO] 开始验证术语使用一致性...")
        
        if not self.load_glossary():
            return
        
        # 查找所有Markdown文件
        md_files = self.find_markdown_files()
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        # 分析每个文件中的术语使用
        for md_file in md_files:
            terms_in_file = self.extract_terms_from_file(md_file)
            
            for term, line_num, context in terms_in_file:
                self.term_usage[term].append({
                    'file': md_file,
                    'line': line_num,
                    'context': context
                })
        
        # 检查术语使用的一致性
        self._check_consistency()
        
        # 输出结果
        self._print_results()
    
    def _check_consistency(self):
        """检查术语使用的一致性问题"""
        for term, usages in self.term_usage.items():
            if len(usages) == 0:
                continue
                
            # 检查是否使用了标准术语形式
            standard_form = term
            english_form = self.terms_dict[term]['english']
            
            for usage in usages:
                context = usage['context']
                # 检查是否使用了非标准形式
                if standard_form not in context and english_form and english_form not in context:
                    self.inconsistencies.append({
                        'term': term,
                        'file': usage['file'],
                        'line': usage['line'],
                        'context': context,
                        'issue': '使用了非标准术语形式'
                    })
    
    def _print_results(self):
        """打印验证结果"""
        total_usages = sum(len(usages) for usages in self.term_usage.values())
        
        print(f"\n[RESULT] 术语使用分析完成:")
        print(f"   识别术语数: {len(self.term_usage)}")
        print(f"   总使用次数: {total_usages}")
        print(f"   一致性问题: {len(self.inconsistencies)}")
        
        if self.inconsistencies:
            print(f"\n[ERROR] 发现 {len(self.inconsistencies)} 个术语使用问题:")
            for i, issue in enumerate(self.inconsistencies[:10], 1):
                rel_file = issue['file'].relative_to(self.project_root)
                print(f"   {i}. {rel_file}:{issue['line']}")
                print(f"      术语: {issue['term']}")
                print(f"      问题: {issue['issue']}")
                print(f"      上下文: {issue['context'][:100]}...")
                print()
            
            if len(self.inconsistencies) > 10:
                print(f"   ... 还有 {len(self.inconsistencies) - 10} 个问题")
        else:
            print("\n[SUCCESS] 所有术语使用都符合规范!")
    
    def generate_report(self) -> str:
        """生成验证报告"""
        from datetime import datetime
        
        report = []
        report.append("# 术语使用一致性验证报告")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"项目根目录: {self.project_root}")
        report.append("")
        
        report.append("## 统计信息")
        report.append(f"- 术语定义数: {len(self.terms_dict)}")
        report.append(f"- 识别术语数: {len(self.term_usage)}")
        report.append(f"- 总使用次数: {sum(len(usages) for usages in self.term_usage.values())}")
        report.append(f"- 一致性问题: {len(self.inconsistencies)}")
        report.append("")
        
        if self.inconsistencies:
            report.append("## 术语使用问题详情")
            for issue in self.inconsistencies:
                rel_file = issue['file'].relative_to(self.project_root)
                report.append(f"- **文件**: {rel_file}")
                report.append(f"  - **行号**: {issue['line']}")
                report.append(f"  - **术语**: {issue['term']}")
                report.append(f"  - **问题**: {issue['issue']}")
                report.append(f"  - **上下文**: {issue['context']}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    validator = TermValidator(project_root)
    validator.validate_term_usage()
    
    # 生成报告文件
    report_content = validator.generate_report()
    report_file = Path(project_root) / "tmp" / "term_validation_report.md"
    
    try:
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[FILE] 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n[WARNING] 无法保存报告文件: {e}")

if __name__ == "__main__":
    main()