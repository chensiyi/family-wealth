#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理临时文件脚本
用于清理根目录下的临时演示文件和网页文件
"""

import os
import sys
from pathlib import Path

def cleanup_temp_files():
    """清理临时文件"""
    temp_files = [
        'financial_analysis_dashboard.html',
        'flowchart_demo.html',
        'sandbox_dashboard.html',
        'launch_sandbox.bat',
        'temp_visual_demo.md',
        'flowchart_style_summary.md',
        'CONTENT_ENHANCEMENT_SUMMARY.md',
        'DEPRECATED_DATA_COLLECTOR_CLEANUP_PLAN.md'
    ]
    
    print("开始清理临时文件...")
    cleaned_count = 0
    
    for filename in temp_files:
        filepath = Path('.') / filename
        if filepath.exists():
            try:
                os.remove(filepath)
                print(f"✓ 已删除: {filename}")
                cleaned_count += 1
            except Exception as e:
                print(f"✗ 删除失败: {filename} - {e}")
        else:
            print(f"○ 不存在: {filename}")
    
    print(f"\n清理完成: {cleaned_count}/{len(temp_files)} 个文件")
    return cleaned_count

if __name__ == "__main__":
    cleanup_temp_files()
