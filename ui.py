"""
用户界面模块
包含所有GUI相关的功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback
from typing import List, Dict, Tuple, Any, Optional
from core import sanitize_path, compare_multiple_folders
from interaction import setup_context_menus

# 定义现代化的颜色主题
COLORS = {
    'primary': '#4a90e2',      # 主色调 - 蓝色
    'secondary': '#7f8c8d',    # 辅助色 - 灰色
    'success': '#27ae60',      # 成功色 - 绿色
    'warning': '#f39c12',      # 警告色 - 橙色
    'danger': '#e74c3c',       # 危险色 - 红色
    'light': '#ecf0f1',        # 浅色
    'dark': '#2c3e50',         # 深色
    'background': '#f8f9fa',   # 背景色
    'border': '#d1d1d1'        # 边框色
}


def get_screen_geometry() -> Tuple[int, int, int, int, int, int]:
    """
    获取屏幕几何信息并计算最佳窗口尺寸
    
    Returns:
        Tuple[int, int, int, int, int, int]: (窗口宽度, 窗口高度, X位置, Y位置, 屏幕宽度, 屏幕高度)
    """
    root = tk.Tk()
    root.withdraw()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.update_idletasks()

    window_width = min(1400, int(screen_width * 0.85))
    window_height = min(1000, int(screen_height * 0.85))

    window_width = max(window_width, 1000)
    window_height = max(window_height, 700)

    pos_x = (screen_width - window_width) // 2
    pos_y = (screen_height - window_height) // 2

    root.destroy()

    return window_width, window_height, pos_x, pos_y, screen_width, screen_height


def create_main_window() -> Optional[tk.Tk]:
    """
    创建主窗口界面
    
    Returns:
        Optional[tk.Tk]: 创建的主窗口对象，如果创建失败则返回None
    """
    try:
        window_width, window_height, pos_x, pos_y, screen_width, screen_height = get_screen_geometry()
    except Exception as e:
        print(f"获取屏幕几何信息失败: {e}")
        return None

    window = tk.Tk()
    window.title("文件夹比较工具")
    window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    window.minsize(1000, 700)
    window.maxsize(screen_width, screen_height)

    try:
        window.iconbitmap(default=None)
    except Exception:
        # 如果设置图标失败，继续运行程序
        pass

    # 设置窗口背景色
    window.configure(bg=COLORS['background'])

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # 存储文件夹列表
    folders: List[str] = []
    current_path = tk.StringVar()
    interaction_manager = None  # 用于存储交互管理器的引用

    def exit_program() -> None:
        """退出程序"""
        try:
            window.quit()
            window.destroy()
        except Exception as e:
            print(f"退出程序时发生错误: {e}")
            try:
                window.destroy()
            except Exception as e2:
                print(f"销毁窗口时发生错误: {e2}")

    def handle_return(event: tk.Event) -> None:
        """处理回车键事件"""
        add_folder_text()

    window.bind('<Escape>', lambda e: exit_program())

    # 文件夹管理功能
    def add_folder_dialog() -> None:
        """通过文件对话框添加文件夹"""
        try:
            new_folder = filedialog.askdirectory(title="选择要添加的文件夹")
            if new_folder and new_folder not in folders:
                if not os.path.exists(new_folder):
                    messagebox.showerror("错误", f"选择的路径不存在: {new_folder}")
                    return
                if not os.path.isdir(new_folder):
                    messagebox.showerror("错误", f"选择的路径不是文件夹: {new_folder}")
                    return

                folders.append(new_folder)
                update_folder_list()
                compare_and_update()
        except Exception as e:
            error_msg = f"添加文件夹失败: {str(e)}"
            print(f"添加文件夹失败: {traceback.format_exc()}")
            messagebox.showerror("错误", error_msg)

    def add_folder_text() -> None:
        """通过文本输入添加文件夹"""
        try:
            path = current_path.get().strip()
            if not path:
                return

            path = sanitize_path(path)

            if not os.path.exists(path):
                messagebox.showwarning("警告", f"路径不存在: {path}")
                return

            if not os.path.isdir(path):
                messagebox.showwarning("警告", f"路径不是文件夹: {path}")
                return

            if path in folders:
                messagebox.showwarning("警告", "文件夹已存在于列表中")
                return

            folders.append(path)
            current_path.set("")
            path_entry.focus()
            update_folder_list()
            compare_and_update()
        except Exception as e:
            error_msg = f"添加文件夹失败: {str(e)}"
            print(f"添加文件夹失败: {traceback.format_exc()}")
            messagebox.showerror("错误", error_msg)

    def remove_folder() -> None:
        """移除选中的文件夹"""
        try:
            selected = folder_listbox.curselection()
            if not selected:
                messagebox.showwarning("警告", "请选择要移除的文件夹")
                return

            if len(selected) > 1:
                result = messagebox.askyesno("确认", f"确定要移除选中的 {len(selected)} 个文件夹吗？")
            else:
                # 确保索引有效
                if 0 <= selected[0] < len(folders):
                    folder_name = os.path.basename(folders[selected[0]])
                    result = messagebox.askyesno("确认", f"确定要移除文件夹 '{folder_name}' 吗？")
                else:
                    result = messagebox.askyesno("确认", f"确定要移除文件夹吗？")

            if not result:
                return

            # 从后往前删除，避免索引问题
            for index in reversed(selected):
                if 0 <= index < len(folders):
                    folders.pop(index)

            update_folder_list()
            compare_and_update()
        except Exception as e:
            error_msg = f"移除文件夹失败: {str(e)}"
            print(f"移除文件夹失败: {traceback.format_exc()}")
            messagebox.showerror("错误", error_msg)

    def update_folder_list() -> None:
        """更新文件夹列表显示"""
        try:
            folder_listbox.delete(0, tk.END)
            for i, folder in enumerate(folders):
                display_text = f"{i+1}. {os.path.basename(folder) or folder}"
                folder_listbox.insert(tk.END, display_text)

            status_label.config(text=f"已添加文件夹: {len(folders)} 个")
            remove_btn.config(state='normal' if folders else 'disabled')

        except Exception as e:
            error_msg = f"更新文件夹列表失败: {str(e)}"
            print(f"更新文件夹列表失败: {traceback.format_exc()}")
            # 不向用户显示此错误，因为这可能会影响用户体验

    def compare_and_update():
        """执行比较并更新结果显示"""
        try:
            valid_folders = []
            for folder in folders:
                if folder and os.path.exists(folder) and os.path.isdir(folder):
                    valid_folders.append(folder)
                else:
                    print(f"Invalid folder removed: {folder}")

            if len(valid_folders) != len(folders):
                folders.clear()
                folders.extend(valid_folders)
                update_folder_list()

            if len(valid_folders) >= 2:
                clear_results()
                loading_label = tk.Label(results_frame, text="正在比较文件夹，请稍候...", 
                                       font=('Arial', 12, 'bold'), fg=COLORS['primary'], bg=COLORS['background'])
                loading_label.pack(pady=50)

                try:
                    window.update_idletasks()
                    window.update()
                except:
                    pass

                common_files, pattern_files, folder_list = compare_multiple_folders(valid_folders)
                update_results(common_files, pattern_files, folder_list)
            else:
                clear_results()
                if len(valid_folders) == 0:
                    hint_text = "请添加有效的文件夹进行比较"
                elif len(valid_folders) == 1:
                    hint_text = "请再添加一个文件夹进行比较"
                else:
                    hint_text = "请至少添加两个文件夹进行比较"

                hint_label = tk.Label(results_frame, text=hint_text, 
                                    font=('Arial', 12), fg=COLORS['secondary'], bg=COLORS['background'])
                hint_label.pack(pady=50)
        except Exception as e:
            clear_results()
            error_msg = f"比较失败: {str(e)}"
            error_label = tk.Label(results_frame, text=error_msg, 
                                 font=('Arial', 12), fg=COLORS['danger'], bg=COLORS['background'])
            error_label.pack(pady=50)
            print(f"Error in compare_and_update: {traceback.format_exc()}")
            messagebox.showerror("错误", error_msg)

    def clear_results():
        """清空结果显示"""
        try:
            for widget in results_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Error clearing results: {str(e)}")

    def update_results(common_files, pattern_files, folder_list):
        """更新比较结果显示"""
        try:
            clear_results()

            if not isinstance(common_files, list):
                common_files = []
            if not isinstance(pattern_files, dict):
                pattern_files = {}
            if not isinstance(folder_list, list):
                folder_list = []

            # 创建主结果容器
            main_results_frame = tk.Frame(results_frame, bg=COLORS['background'])
            main_results_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            main_results_frame.grid_columnconfigure(0, weight=1)
            results_frame.grid_rowconfigure(0, weight=1)
            results_frame.grid_columnconfigure(0, weight=1)

            current_row = 0

            # 显示共有文件
            if common_files:
                # 创建带样式的标签框架
                common_frame = tk.LabelFrame(
                    main_results_frame,
                    text=f"所有文件夹共有的文件 ({len(common_files)} 个)",
                    font=('Arial', 10, 'bold'),
                    fg=COLORS['primary'],
                    bg=COLORS['background'],
                    padx=10,
                    pady=5
                )
                common_frame.grid(row=current_row, column=0, sticky='ew', pady=(0, 10))
                common_frame.grid_rowconfigure(0, weight=1)
                common_frame.grid_columnconfigure(0, weight=1)

                list_height = min(8, max(4, len(common_files)))
                # 创建带样式的列表框
                common_list = tk.Listbox(
                    common_frame,
                    selectmode=tk.EXTENDED,
                    height=list_height,
                    font=('Consolas', 10),
                    bg='white',
                    fg=COLORS['dark'],
                    selectbackground=COLORS['primary'],
                    selectforeground='white',
                    highlightthickness=1,
                    highlightcolor=COLORS['border'],
                    relief='flat',
                    bd=0
                )
                common_list.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)


                # 滚动条
                common_scrollbar = tk.Scrollbar(common_frame, orient="vertical", command=common_list.yview)
                common_scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=5)
                common_list.config(yscrollcommand=common_scrollbar.set)

                for item in common_files:
                    common_list.insert(tk.END, item)

                current_row += 1

            # 显示文件分布矩阵
            if pattern_files:
                # 创建带样式的标签框架
                matrix_frame = tk.LabelFrame(
                    main_results_frame,
                    text="文件分布矩阵",
                    font=('Arial', 10, 'bold'),
                    fg=COLORS['primary'],
                    bg=COLORS['background'],
                    padx=10,
                    pady=5
                )
                matrix_frame.grid(row=current_row, column=0, sticky='nsew', pady=(5, 0))
                matrix_frame.grid_rowconfigure(0, weight=1)
                matrix_frame.grid_columnconfigure(0, weight=1)

                main_results_frame.grid_rowconfigure(current_row, weight=1)

                # 创建带样式的画布和滚动条
                canvas = tk.Canvas(
                    matrix_frame,
                    bg=COLORS['background'],
                    highlightthickness=0
                )
                scrollbar = tk.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                def on_mousewheel(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                canvas.bind("<MouseWheel>", on_mousewheel)

                canvas.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=5)
                scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=5)

                pattern_row = 0
                for pattern, files in pattern_files.items():
                    if not files:
                        continue

                    pattern_desc = []
                    for i, exists in enumerate(pattern):
                        if exists:
                            pattern_desc.append(f"文件夹{i+1}")

                    if len(pattern_desc) == 1:
                        title = f"仅在 {pattern_desc[0]} 中存在 ({len(files)} 个)"
                    else:
                        title = f"存在于 {' 和 '.join(pattern_desc)} 中 ({len(files)} 个)"

                    # 创建带样式的标签框架
                    pattern_frame = tk.LabelFrame(
                        scrollable_frame,
                        text=title,
                        font=('Arial', 9, 'bold'),
                        fg=COLORS['dark'],
                        bg=COLORS['background'],
                        padx=10,
                        pady=5
                    )
                    pattern_frame.grid(row=pattern_row, column=0, sticky='ew', padx=5, pady=5)
                    pattern_frame.grid_columnconfigure(0, weight=1)
                    pattern_frame.grid_rowconfigure(1, weight=1)
                    scrollable_frame.grid_columnconfigure(0, weight=1)

                    # 创建文件列表
                    text_frame = tk.Frame(pattern_frame, bg=COLORS['background'])
                    text_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
                    text_frame.grid_rowconfigure(0, weight=1)
                    text_frame.grid_columnconfigure(0, weight=1)

                    text_height = min(8, max(3, len(files)))
                    # 创建带样式的文本框
                    files_text = tk.Text(
                        text_frame,
                        height=text_height,
                        wrap=tk.WORD,
                        font=('Consolas', 9),
                        bg='white',
                        fg=COLORS['dark'],
                        highlightthickness=1,
                        highlightcolor=COLORS['border'],
                        relief='flat',
                        bd=0
                    )
                    files_text.grid(row=0, column=0, sticky='ew')


                    if len(files) > text_height:
                        text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=files_text.yview)
                        text_scrollbar.grid(row=0, column=1, sticky='ns')
                        files_text.config(yscrollcommand=text_scrollbar.set)

                    for i, file in enumerate(files):
                        if i > 0:
                            files_text.insert(tk.END, '\n')
                        files_text.insert(tk.END, file)

                    pattern_row += 1

        except Exception as e:
            clear_results()
            error_msg = f"更新结果显示失败: {str(e)}"
            error_label = tk.Label(results_frame, text=error_msg, 
                                 font=('Arial', 12), fg=COLORS['danger'], bg=COLORS['background'])
            error_label.pack(pady=50)
            print(f"Error in update_results: {traceback.format_exc()}")
        
        # 通知交互管理器重新绑定事件
        if interaction_manager and hasattr(interaction_manager, '_bind_child_events'):
            # 创建一个假的事件来触发重新绑定
            class FakeEvent:
                def __init__(self, widget):
                    self.widget = widget
            
            fake_event = FakeEvent(results_frame)
            interaction_manager._bind_child_events(fake_event)

    # 创建主界面布局
    main_frame = tk.Frame(window, bg=COLORS['background'])
    main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=0, minsize=int(window_width * 0.3))
    main_frame.grid_columnconfigure(1, weight=1)

    # 左侧：文件夹管理区域
    left_frame = tk.LabelFrame(
        main_frame,
        text="文件夹管理",
        font=('Arial', 11, 'bold'),
        fg=COLORS['primary'],
        bg=COLORS['background'],
        padx=15,
        pady=10
    )
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
    left_frame.grid_rowconfigure(2, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)

    # 输入区域
    input_frame = tk.Frame(left_frame, bg=COLORS['background'])
    input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    input_frame.grid_columnconfigure(0, weight=1)

    # 创建带样式的标签
    path_label = tk.Label(
        input_frame,
        text="文件夹路径:",
        font=('Arial', 9, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['dark']
    )
    path_label.grid(row=0, column=0, sticky='w', pady=(0, 2))

    # 创建带样式的输入框
    path_entry = tk.Entry(
        input_frame,
        textvariable=current_path,
        font=('Arial', 10),
        bg='white',
        fg=COLORS['dark'],
        highlightthickness=2,
        highlightcolor=COLORS['primary'],
        relief='flat',
        bd=0,
        insertbackground=COLORS['dark']
    )
    path_entry.grid(row=1, column=0, sticky='ew', pady=(0, 5), ipady=3)
    path_entry.bind('<Return>', handle_return)

    # 路径输入框提示文本
    def on_entry_click(event):
        if path_entry.get() == "请按Ctrl+V粘贴或输入文件夹路径，按Enter添加":
            path_entry.delete(0, tk.END)
            path_entry.config(fg=COLORS['dark'])

    def on_focusout(event):
        if path_entry.get() == '':
            path_entry.insert(0, "请按Ctrl+V粘贴或输入文件夹路径，按Enter添加")
            path_entry.config(fg=COLORS['secondary'])

    path_entry.insert(0, "请按Ctrl+V粘贴或输入文件夹路径，按Enter添加")
    path_entry.config(fg=COLORS['secondary'])
    path_entry.bind('<FocusIn>', on_entry_click)
    path_entry.bind('<FocusOut>', on_focusout)


    # 创建自定义样式的按钮
    def create_styled_button(parent, text, command, column, sticky='ew', padx=(0, 2)):
        """创建自定义样式的按钮"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS['primary'],
            fg='white',
            activebackground=COLORS['primary'],
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        btn.grid(row=0, column=column, sticky=sticky, padx=padx)
        return btn

    # 按钮区域
    button_frame = tk.Frame(input_frame, bg=COLORS['background'])
    button_frame.grid(row=2, column=0, sticky='ew', pady=(0, 5))
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    create_styled_button(button_frame, "添加路径 (Enter)", add_folder_text, 0, padx=(0, 2))
    create_styled_button(button_frame, "浏览文件夹", add_folder_dialog, 1, padx=2)
    remove_btn = create_styled_button(button_frame, "移除选中", remove_folder, 2, padx=(2, 0))
    remove_btn.config(state='disabled', bg=COLORS['secondary'])

    # 文件夹列表
    folder_list_label = tk.Label(
        left_frame,
        text="已添加的文件夹:",
        font=('Arial', 9, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['dark']
    )
    folder_list_label.grid(row=1, column=0, sticky='w', padx=5, pady=(5, 2))

    list_frame = tk.Frame(left_frame, bg=COLORS['background'])
    list_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    # 创建带样式的列表框
    folder_listbox = tk.Listbox(
        list_frame,
        selectmode=tk.EXTENDED,
        font=('Consolas', 10),
        bg='white',
        fg=COLORS['dark'],
        selectbackground=COLORS['primary'],
        selectforeground='white',
        highlightthickness=1,
        highlightcolor=COLORS['border'],
        relief='flat',
        bd=0
    )
    folder_listbox.grid(row=0, column=0, sticky='nsew', padx=(0, 2), pady=2)

    # 文件夹列表滚动条
    list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=folder_listbox.yview)
    list_scrollbar.grid(row=0, column=1, sticky='ns', pady=2)
    folder_listbox.config(yscrollcommand=list_scrollbar.set)

    # 状态和控制区域
    control_frame = tk.Frame(left_frame, bg=COLORS['background'])
    control_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    control_frame.grid_columnconfigure(0, weight=1)

    status_label = tk.Label(
        control_frame,
        text="已添加文件夹: 0 个",
        font=('Arial', 10, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['dark']
    )
    status_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

    # 创建退出按钮
    exit_btn = tk.Button(
        control_frame,
        text="退出程序 (ESC)",
        command=exit_program,
        bg=COLORS['danger'],
        fg='white',
        activebackground=COLORS['danger'],
        activeforeground='white',
        relief='flat',
        bd=0,
        padx=10,
        pady=5,
        font=('Arial', 9, 'bold')
    )
    exit_btn.grid(row=2, column=0, sticky='ew', pady=2)

    # 右侧：结果显示区域
    results_frame = tk.LabelFrame(
        main_frame,
        text="比较结果",
        font=('Arial', 11, 'bold'),
        fg=COLORS['primary'],
        bg=COLORS['background'],
        padx=15,
        pady=10
    )
    results_frame.grid(row=0, column=1, sticky='nsew')
    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)

    # 结果显示区域

    # 初始化上下文菜单
    interaction_manager = setup_context_menus(window, path_entry, results_frame, compare_and_update)

    # 初始化
    path_entry.focus()

    return window
