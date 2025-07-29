"""
文件夹比较工具 - 独立启动版本
解决模块导入问题
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback

def sanitize_path(path):
    """处理用户输入的路径"""
    return os.path.normpath(path.strip().strip('"').strip("'"))

def compare_multiple_folders(folders):
    """比较多个文件夹的内容"""
    if not folders or len(folders) < 2:
        return [], {}, folders
    
    try:
        folder_files = {}
        for folder in folders:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                continue
            try:
                files = set(os.listdir(folder))
                folder_files[folder] = files
            except PermissionError:
                print(f"无权限访问文件夹: {folder}")
                continue

        if not folder_files:
            return [], {}, folders
        
        all_files = set()
        for files in folder_files.values():
            all_files.update(files)
        
        if not all_files:
            return [], {}, folders

        file_matrix = {}
        for file in all_files:
            presence_pattern = tuple(file in folder_files[folder] for folder in folders)
            if presence_pattern not in file_matrix:
                file_matrix[presence_pattern] = []
            file_matrix[presence_pattern].append(file)

        all_true_pattern = tuple([True] * len(folders))
        common_files = sorted(file_matrix.get(all_true_pattern, []))
        
        pattern_files = {}
        for pattern, files in file_matrix.items():
            if pattern != all_true_pattern:
                pattern_files[pattern] = sorted(files)

        return common_files, pattern_files, folders
    except Exception as e:
        print(f"Error in compare_multiple_folders: {traceback.format_exc()}")
        return [], {}, folders

def main():
    """主程序"""
    # 获取屏幕尺寸
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    # 计算窗口尺寸
    window_width = min(1400, int(screen_width * 0.85))
    window_height = min(1000, int(screen_height * 0.85))
    window_width = max(window_width, 1000)
    window_height = max(window_height, 700)
    pos_x = (screen_width - window_width) // 2
    pos_y = (screen_height - window_height) // 2
    
    # 创建主窗口
    window = tk.Tk()
    window.title("文件夹比较工具 - 优化版")
    window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
    window.minsize(1000, 700)
    
    # 存储文件夹列表
    folders = []
    current_path = tk.StringVar()
    
    # 窗口布局
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    
    main_frame = ttk.Frame(window)
    main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=0, minsize=int(window_width * 0.3))
    main_frame.grid_columnconfigure(1, weight=1)
    
    # 左侧面板
    left_frame = ttk.LabelFrame(main_frame, text="文件夹管理")
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
    left_frame.grid_rowconfigure(2, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    
    # 输入区域
    input_frame = ttk.Frame(left_frame)
    input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    input_frame.grid_columnconfigure(0, weight=1)
    
    ttk.Label(input_frame, text="文件夹路径:").grid(row=0, column=0, sticky='w')
    path_entry = ttk.Entry(input_frame, textvariable=current_path)
    path_entry.grid(row=1, column=0, sticky='ew', pady=(0, 5))
    
    # 按钮区域
    button_frame = ttk.Frame(input_frame)
    button_frame.grid(row=2, column=0, sticky='ew')
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    
    def add_folder_text():
        """添加文件夹"""
        try:
            path = sanitize_path(current_path.get().strip())
            if not path:
                return
            
            if not os.path.exists(path):
                messagebox.showwarning("警告", f"路径不存在: {path}")
                return
            
            if not os.path.isdir(path):
                messagebox.showwarning("警告", f"路径不是文件夹: {path}")
                return
            
            if path in folders:
                messagebox.showwarning("警告", "文件夹已存在")
                return
            
            folders.append(path)
            current_path.set("")
            update_folder_list()
            compare_and_update()
        except Exception as e:
            messagebox.showerror("错误", f"添加文件夹失败: {str(e)}")
    
    def add_folder_dialog():
        """浏览添加文件夹"""
        try:
            new_folder = filedialog.askdirectory(title="选择文件夹")
            if new_folder and new_folder not in folders:
                folders.append(new_folder)
                update_folder_list()
                compare_and_update()
        except Exception as e:
            messagebox.showerror("错误", f"添加文件夹失败: {str(e)}")
    
    def remove_folder():
        """移除选中文件夹"""
        try:
            selected = folder_listbox.curselection()
            if not selected:
                messagebox.showwarning("警告", "请选择要移除的文件夹")
                return
            
            if len(selected) > 1:
                result = messagebox.askyesno("确认", f"确定移除 {len(selected)} 个文件夹吗？")
            else:
                result = messagebox.askyesno("确认", f"确定移除文件夹吗？")
            
            if result:
                for index in reversed(selected):
                    if 0 <= index < len(folders):
                        folders.pop(index)
                update_folder_list()
                compare_and_update()
        except Exception as e:
            messagebox.showerror("错误", f"移除失败: {str(e)}")
    
    ttk.Button(button_frame, text="添加路径", command=add_folder_text).grid(row=0, column=0, sticky='ew', padx=1)
    ttk.Button(button_frame, text="浏览", command=add_folder_dialog).grid(row=0, column=1, sticky='ew', padx=1)
    ttk.Button(button_frame, text="移除", command=remove_folder).grid(row=0, column=2, sticky='ew', padx=1)
    
    # 文件夹列表
    ttk.Label(left_frame, text="已添加的文件夹:").grid(row=1, column=0, sticky='w', padx=5, pady=(5, 2))
    
    list_frame = ttk.Frame(left_frame)
    list_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)
    
    folder_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=('Consolas', 9))
    folder_listbox.grid(row=0, column=0, sticky='nsew')
    
    list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=folder_listbox.yview)
    list_scrollbar.grid(row=0, column=1, sticky='ns')
    folder_listbox.config(yscrollcommand=list_scrollbar.set)
    
    # 状态区域
    control_frame = ttk.Frame(left_frame)
    control_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    
    status_label = ttk.Label(control_frame, text="已添加文件夹: 0 个", font=('Arial', 10, 'bold'))
    status_label.pack()
    
    ttk.Button(control_frame, text="退出程序", command=window.quit).pack(pady=5, fill='x')
    
    # 右侧结果区域
    results_frame = ttk.LabelFrame(main_frame, text="比较结果")
    results_frame.grid(row=0, column=1, sticky='nsew')
    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)
    
    def update_folder_list():
        """更新文件夹列表"""
        folder_listbox.delete(0, tk.END)
        for i, folder in enumerate(folders):
            display_text = f"{i+1}. {os.path.basename(folder) or folder}"
            folder_listbox.insert(tk.END, display_text)
        status_label.config(text=f"已添加文件夹: {len(folders)} 个")
    
    def clear_results():
        """清空结果"""
        for widget in results_frame.winfo_children():
            widget.destroy()
    
    def compare_and_update():
        """比较并更新结果"""
        try:
            clear_results()
            
            if len(folders) >= 2:
                loading_label = tk.Label(results_frame, text="正在比较...", font=('Arial', 12))
                loading_label.pack(pady=50)
                window.update()
                
                common_files, pattern_files, folder_list = compare_multiple_folders(folders)
                loading_label.destroy()
                
                if common_files:
                    common_frame = ttk.LabelFrame(results_frame, text=f"共有文件 ({len(common_files)} 个)")
                    common_frame.pack(fill='both', expand=True, padx=5, pady=5)
                    
                    common_text = tk.Text(common_frame, height=6)
                    common_text.pack(fill='both', expand=True, padx=5, pady=5)
                    
                    for file in common_files:
                        common_text.insert(tk.END, file + '\n')
                    common_text.config(state='disabled')
                
                if pattern_files:
                    matrix_frame = ttk.LabelFrame(results_frame, text="文件分布")
                    matrix_frame.pack(fill='both', expand=True, padx=5, pady=5)
                    
                    canvas = tk.Canvas(matrix_frame)
                    scrollbar = ttk.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
                    scrollable_frame = ttk.Frame(canvas)
                    
                    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                    canvas.configure(yscrollcommand=scrollbar.set)
                    
                    for pattern, files in pattern_files.items():
                        if not files:
                            continue
                        
                        pattern_desc = []
                        for i, exists in enumerate(pattern):
                            if exists:
                                pattern_desc.append(f"文件夹{i+1}")
                        
                        title = f"存在于 {' 和 '.join(pattern_desc)} 中 ({len(files)} 个)"
                        
                        pattern_frame = ttk.LabelFrame(scrollable_frame, text=title)
                        pattern_frame.pack(fill='x', padx=5, pady=2)
                        
                        # 文件列表
                        files_text = tk.Text(pattern_frame, height=min(6, len(files)), wrap=tk.WORD)
                        files_text.pack(fill='x', padx=5, pady=5)
                        
                        for file in files:
                            files_text.insert(tk.END, file + '\n')
                        files_text.config(state='disabled')
                    
                    canvas.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
            else:
                hint_label = tk.Label(results_frame, text="请添加至少两个文件夹进行比较", 
                                    font=('Arial', 12), fg='gray')
                hint_label.pack(pady=50)
        except Exception as e:
            clear_results()
            error_label = tk.Label(results_frame, text=f"比较失败: {str(e)}", 
                                 font=('Arial', 12), fg='red')
            error_label.pack(pady=50)
            print(f"比较错误: {traceback.format_exc()}")
    
    # 绑定事件
    path_entry.bind('<Return>', lambda e: add_folder_text())
    path_entry.focus()
    
    # 启动程序
    window.mainloop()

if __name__ == "__main__":
    main()
