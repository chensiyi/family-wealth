#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目质量检查统一入口
执行所有自动化验证工具并生成综合报告
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_tool(script_name: str, description: str) -> bool:
    """运行单个验证工具"""
    print(f"\n{'='*50}")
    print(f"[TOOL] 正在运行: {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([
            sys.executable, 
            f"scripts/{script_name}"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("[OK] 执行成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("[FAIL] 执行失败")
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] 执行异常: {e}")
        return False

def main():
    """主函数"""
    print("[START] 开始项目质量综合检查")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保在项目根目录
    project_root = Path(".")
    
    # 要执行的工具列表
    tools = [
        ("link_checker.py", "链接有效性检查"),
        ("term_validator.py", "术语使用一致性验证"),
        ("format_validator.py", "文档格式规范检查")
    ]
    
    # 执行所有工具
    results = []
    for script_name, description in tools:
        success = run_tool(script_name, description)
        results.append((description, success))
    
    # 生成综合报告
    print(f"\n{'='*60}")
    print("[SUMMARY] 综合检查结果汇总")
    print(f"{'='*60}")
    
    successful_tools = sum(1 for _, success in results if success)
    total_tools = len(results)
    
    print(f"总工具数: {total_tools}")
    print(f"成功执行: {successful_tools}")
    print(f"执行失败: {total_tools - successful_tools}")
    print()
    
    print("[DETAIL] 详细结果:")
    for description, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        print(f"  {status} {description}")
    
    # 生成综合报告文件
    generate_summary_report(results, project_root)
    
    print(f"\n[END] 质量检查完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def generate_summary_report(results: list, project_root: Path):
    """生成综合报告"""
    report_lines = []
    report_lines.append("# 项目质量综合检查报告")
    report_lines.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # 执行摘要
    successful_tools = sum(1 for _, success in results if success)
    total_tools = len(results)
    
    report_lines.append("## 执行摘要")
    report_lines.append(f"- 总工具数: {total_tools}")
    report_lines.append(f"- 成功执行: {successful_tools}")
    report_lines.append(f"- 执行失败: {total_tools - successful_tools}")
    report_lines.append("")
    
    # 详细结果
    report_lines.append("## 工具执行详情")
    for description, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        report_lines.append(f"- {status} {description}")
    report_lines.append("")
    
    # 各工具报告汇总
    report_lines.append("## 各工具详细报告")
    
    report_files = [
        ("link_check_report.md", "🔗 链接检查详细报告"),
        ("term_validation_report.md", "📚 术语验证详细报告"),
        ("format_validation_report.md", "📝 格式验证详细报告")
    ]
    
    for filename, title in report_files:
        report_path = project_root / "tmp" / filename
        if report_path.exists():
            report_lines.append(f"### {title}")
            report_lines.append(f"详见: [{filename}](../tmp/{filename})")
            report_lines.append("")
        else:
            report_lines.append(f"### {title}")
            report_lines.append("*报告文件未生成*")
            report_lines.append("")
    
    # 写入报告文件
    report_content = "\n".join(report_lines)
    report_file = project_root / "tmp" / "quality_check_summary.md"
    
    try:
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[REPORT] 综合报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n[WARN] 无法保存综合报告: {e}")

if __name__ == "__main__":
    main()