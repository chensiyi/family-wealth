#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的日志工具
"""

import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """设置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger