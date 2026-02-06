#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
链接有效性检查器
检查项目中所有Markdown文件的内部链接有效性
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import urllib.parse

class LinkChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.markdown_files = []
        self.all_links = []
        self.broken_links = []
        self.external_links = []
        
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        for file_path in self.project_root.rglob("*.md"):
            # 排除隐藏目录和特定目录
            if not any(part.startswith('.') for part in file_path.parts[:-1]):
                if 'node_modules' not in file_path.parts and '.git' not in file_path.parts:
                    md_files.append(file_path)
        return sorted(md_files)
    
    def extract_links(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """从Markdown文件中提取链接"""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 匹配Markdown链接格式: [text](link)
            link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                text, link = match.groups()
                line_number = content[:match.start()].count('\n') + 1
                links.append((link, line_number, text))
                
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            
        return links
    
    def validate_link(self, link: str, current_file: Path) -> Tuple[bool, str]:
        """验证链接有效性"""
        # 处理相对链接
        if link.startswith('#'):
            # 锚点链接，检查当前文件内是否存在
            return True, "锚点链接"
        elif link.startswith('http'):
            # 外部链接
            self.external_links.append((current_file, link))
            return True, "外部链接"
        else:
            # 相对文件链接
            try:
                # 解析链接路径
                parsed = urllib.parse.urlparse(link)
                link_path = parsed.path
                
                # 构建完整路径
                if link_path.startswith('/'):
                    # 绝对路径（相对于项目根目录）
                    target_path = self.project_root / link_path.lstrip('/')
                else:
                    # 相对路径（相对于当前文件）
                    target_path = current_file.parent / link_path
                    
                # 检查文件是否存在
                if target_path.exists():
                    return True, str(target_path.relative_to(self.project_root))
                else:
                    return False, f"文件不存在: {target_path}"
                    
            except Exception as e:
                return False, f"链接解析错误: {e}"
    
    def check_all_links(self):
        """检查所有链接"""
        print("[INFO] 开始检查链接有效性...")
        
        # 查找所有Markdown文件
        self.markdown_files = self.find_markdown_files()
        print(f"找到 {len(self.markdown_files)} 个Markdown文件")
        
        # 提取和验证所有链接
        total_links = 0
        broken_count = 0
        
        for md_file in self.markdown_files:
            links = self.extract_links(md_file)
            total_links += len(links)
            
            for link, line_num, text in links:
                is_valid, message = self.validate_link(link, md_file)
                
                if not is_valid:
                    self.broken_links.append({
                        'file': md_file,
                        'line': line_num,
                        'link': link,
                        'text': text,
                        'error': message
                    })
                    broken_count += 1
                else:
                    self.all_links.append({
                        'file': md_file,
                        'line': line_num,
                        'link': link,
                        'text': text,
                        'target': message
                    })
        
        print(f"\n[RESULT] 检查完成:")
        print(f"   总链接数: {total_links}")
        print(f"   有效链接: {total_links - broken_count}")
        print(f"   无效链接: {broken_count}")
        print(f"   外部链接: {len(self.external_links)}")
        
        if self.broken_links:
            print(f"\n[ERROR] 发现 {len(self.broken_links)} 个无效链接:")
            for i, broken in enumerate(self.broken_links[:10], 1):  # 只显示前10个
                print(f"   {i}. {broken['file'].relative_to(self.project_root)}:{broken['line']}")
                print(f"      链接: {broken['link']}")
                print(f"      错误: {broken['error']}")
                print()
            
            if len(self.broken_links) > 10:
                print(f"   ... 还有 {len(self.broken_links) - 10} 个无效链接")
        else:
            print("\n[SUCCESS] 所有内部链接都有效!")
    
    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 链接检查报告")
        report.append(f"检查时间: {self._get_current_time()}")
        report.append(f"项目根目录: {self.project_root}")
        report.append("")
        
        report.append("## 统计信息")
        report.append(f"- Markdown文件数量: {len(self.markdown_files)}")
        report.append(f"- 总链接数: {len(self.all_links) + len(self.broken_links)}")
        report.append(f"- 有效链接: {len(self.all_links)}")
        report.append(f"- 无效链接: {len(self.broken_links)}")
        report.append(f"- 外部链接: {len(self.external_links)}")
        report.append("")
        
        if self.broken_links:
            report.append("## 无效链接详情")
            for broken in self.broken_links:
                report.append(f"- **文件**: {broken['file'].relative_to(self.project_root)}")
                report.append(f"  - **行号**: {broken['line']}")
                report.append(f"  - **链接文本**: {broken['text']}")
                report.append(f"  - **链接地址**: {broken['link']}")
                report.append(f"  - **错误信息**: {broken['error']}")
                report.append("")
        
        return "\n".join(report)
    
    def _get_current_time(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = LinkChecker(project_root)
    checker.check_all_links()
    
    # 生成报告文件
    report_content = checker.generate_report()
    report_file = Path(project_root) / "tmp" / "link_check_report.md"
    
    try:
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[FILE] 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n[WARNING] 无法保存报告文件: {e}")

if __name__ == "__main__":
    main()