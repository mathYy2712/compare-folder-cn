"""
核心业务逻辑模块
包含文件夹比较、文件操作等核心功能
"""

import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    filename='folder_comparison_tool.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Disable win32clipboard since it causes stability issues
HAS_WIN32 = False

def sanitize_path(path):
    """处理用户输入的路径"""
    return os.path.normpath(path.strip().strip('"').strip("'"))






def compare_multiple_folders(folders):
    """比较多个文件夹的内容，返回详细的文件分布矩阵"""
    if not folders:
        return [], {}, []

    if len(folders) < 2:
        return [], {}, folders

    try:
        # 验证所有文件夹是否存在且可访问
        folder_files = {}
        for folder in folders:
            if not os.path.exists(folder):
                print(f"文件夹不存在: {folder}")
                return [], {}, folders
            if not os.path.isdir(folder):
                print(f"路径不是文件夹: {folder}")
                return [], {}, folders
            try:
                files = set(os.listdir(folder))
                folder_files[folder] = files
            except PermissionError:
                print(f"无权限访问文件夹: {folder}")
                return [], {}, folders
            except Exception as e:
                print(f"读取文件夹失败 {folder}: {str(e)}")
                return [], {}, folders

        # 获取所有文件的并集
        if not folder_files:
            return [], {}, folders

        all_files = set()
        for files in folder_files.values():
            all_files.update(files)

        if not all_files:
            return [], {}, folders

        # 分析每个文件在哪些文件夹中存在（矩阵形式）
        file_matrix = {}
        for file in all_files:
            presence_pattern = tuple(file in folder_files[folder] for folder in folders)
            if presence_pattern not in file_matrix:
                file_matrix[presence_pattern] = []
            file_matrix[presence_pattern].append(file)

        # 对结果进行分类
        all_true_pattern = tuple([True] * len(folders))
        common_files = sorted(file_matrix.get(all_true_pattern, []))

        # 按存在模式分类文件
        pattern_files = {}
        for pattern, files in file_matrix.items():
            if pattern != all_true_pattern:
                pattern_files[pattern] = sorted(files)

        return common_files, pattern_files, folders
    except Exception as e:
        error_msg = f"比较文件夹时出错: {str(e)}"
        print(f"Error in compare_multiple_folders: {traceback.format_exc()}")
        return [], {}, folders
