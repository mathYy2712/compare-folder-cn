"""
核心业务逻辑模块
包含文件夹比较、文件操作等核心功能
"""

import os
import logging
import traceback
from typing import List, Dict, Tuple, Set

# 配置日志
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def sanitize_path(path: str) -> str:
    """
    处理用户输入的路径
    去除首尾空格和引号，并规范化路径
    
    Args:
        path (str): 用户输入的路径字符串
        
    Returns:
        str: 规范化后的路径
    """
    return os.path.normpath(path.strip().strip('"').strip("'"))


def compare_multiple_folders(folders: List[str]) -> Tuple[List[str], Dict[Tuple[bool, ...], List[str]], List[str]]:
    """
    比较多个文件夹的内容，返回详细的文件分布矩阵
    
    Args:
        folders (List[str]): 要比较的文件夹路径列表
        
    Returns:
        Tuple[List[str], Dict[Tuple[bool, ...], List[str]], List[str]]: 
        (共有文件列表, 文件分布模式字典, 原始文件夹列表)
    """
    # 输入验证
    if not folders:
        return [], {}, []
    
    if len(folders) < 2:
        return [], {}, folders

    try:
        # 验证所有文件夹是否存在且可访问
        folder_files: Dict[str, Set[str]] = {}
        valid_folders: List[str] = []
        
        for folder in folders:
            # 检查路径是否存在
            if not os.path.exists(folder):
                logging.warning(f"文件夹不存在: {folder}")
                print(f"文件夹不存在: {folder}")
                continue
            
            # 检查是否为文件夹
            if not os.path.isdir(folder):
                logging.warning(f"路径不是文件夹: {folder}")
                print(f"路径不是文件夹: {folder}")
                continue
            
            try:
                # 尝试读取文件夹内容
                files = set(os.listdir(folder))
                folder_files[folder] = files
                valid_folders.append(folder)
            except PermissionError:
                logging.error(f"无权限访问文件夹: {folder}")
                print(f"无权限访问文件夹: {folder}")
            except Exception as e:
                logging.error(f"读取文件夹失败 {folder}: {str(e)}")
                print(f"读取文件夹失败 {folder}: {str(e)}")

        # 如果没有有效的文件夹，返回空结果
        if not folder_files:
            return [], {}, valid_folders

        # 获取所有文件的并集
        all_files: Set[str] = set()
        for files in folder_files.values():
            all_files.update(files)

        # 如果没有文件，返回空结果
        if not all_files:
            return [], {}, valid_folders

        # 分析每个文件在哪些文件夹中存在（矩阵形式）
        file_matrix: Dict[Tuple[bool, ...], List[str]] = {}
        for file in all_files:
            # 创建存在模式元组 (True/False 表示文件是否在对应文件夹中存在)
            presence_pattern = tuple(file in folder_files[folder] for folder in valid_folders)
            if presence_pattern not in file_matrix:
                file_matrix[presence_pattern] = []
            file_matrix[presence_pattern].append(file)

        # 对结果进行分类
        # 所有文件夹都存在的文件
        all_true_pattern = tuple([True] * len(valid_folders))
        common_files = sorted(file_matrix.get(all_true_pattern, []))

        # 按存在模式分类文件（排除所有文件夹都存在的文件）
        pattern_files: Dict[Tuple[bool, ...], List[str]] = {}
        for pattern, files in file_matrix.items():
            if pattern != all_true_pattern:
                pattern_files[pattern] = sorted(files)

        return common_files, pattern_files, valid_folders
    except Exception as e:
        error_msg = f"比较文件夹时出错: {str(e)}"
        logging.error(f"Error in compare_multiple_folders: {traceback.format_exc()}")
        print(f"Error in compare_multiple_folders: {traceback.format_exc()}")
        return [], {}, folders
