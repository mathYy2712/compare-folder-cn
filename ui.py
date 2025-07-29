"""
用户界面模块
包含所有GUI相关的功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback
from .core import sanitize_path, compare_multiple_folders


def get_screen_geometry():
    """获取屏幕几何信息并计算最佳窗口尺寸"""
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


def create_main_window():
    """创建主窗口界面"""
    window_width, window_height, pos_x, pos_y, screen_width, screen_height = get_screen_geometry()

    window = tk.Tk()
    window.title("文件夹比较工具")
    window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    window.minsize(1000, 700)
    window.maxsize(screen_width, screen_height)

    try:
        window.iconbitmap(default=None)
    except:
        pass

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # 存储文件夹列表
    folders = []
    current_path = tk.StringVar()

    def exit_program():
        """退出程序"""
        try:
            window.quit()
            window.destroy()
        except:
            pass

    def handle_return(event):
        """处理回车键事件"""
        add_folder_text()

    window.bind('<Escape>', lambda e: exit_program())

    # 文件夹管理功能
    def add_folder_dialog():
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
            messagebox.showerror("错误", f"添加文件夹失败: {str(e)}")

    def add_folder_text():
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
            messagebox.showerror("错误", f"添加文件夹失败: {str(e)}")

    def remove_folder():
        """移除选中的文件夹"""
        try:
            selected = folder_listbox.curselection()
            if not selected:
                messagebox.showwarning("警告", "请选择要移除的文件夹")
                return

            if len(selected) > 1:
                result = messagebox.askyesno("确认", f"确定要移除选中的 {len(selected)} 个文件夹吗？")
            else:
                result = messagebox.askyesno("确认", f"确定要移除文件夹 '{os.path.basename(folders[selected[0]])}' 吗？")

            if not result:
                return

            for index in reversed(selected):
                if 0 <= index < len(folders):
                    folders.pop(index)

            update_folder_list()
            compare_and_update()
        except Exception as e:
            messagebox.showerror("错误", f"移除文件夹失败: {str(e)}")

    def update_folder_list():
        """更新文件夹列表显示"""
        try:
            folder_listbox.delete(0, tk.END)
            for i, folder in enumerate(folders):
                display_text = f"{i+1}. {os.path.basename(folder) or folder}"
                folder_listbox.insert(tk.END, display_text)

            status_label.config(text=f"已添加文件夹: {len(folders)} 个")
            remove_btn.config(state='normal' if folders else 'disabled')

        except Exception as e:
            print(f"Error updating folder list: {str(e)}")

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
                                       font=('Arial', 12), fg='blue')
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
                                    font=('Arial', 12), fg='gray')
                hint_label.pack(pady=50)
        except Exception as e:
            clear_results()
            error_msg = f"比较失败: {str(e)}"
            error_label = tk.Label(results_frame, text=error_msg, 
                                 font=('Arial', 12), fg='red')
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
            main_results_frame = ttk.Frame(results_frame)
            main_results_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            main_results_frame.grid_columnconfigure(0, weight=1)
            results_frame.grid_rowconfigure(0, weight=1)
            results_frame.grid_columnconfigure(0, weight=1)

            current_row = 0

            # 显示共有文件
            if common_files:
                common_frame = ttk.LabelFrame(main_results_frame, text=f"所有文件夹共有的文件 ({len(common_files)} 个)")
                common_frame.grid(row=current_row, column=0, sticky='ew', pady=(0, 5))
                common_frame.grid_rowconfigure(0, weight=1)
                common_frame.grid_columnconfigure(0, weight=1)

                list_height = min(8, max(4, len(common_files)))
                common_list = tk.Listbox(common_frame, selectmode=tk.EXTENDED, height=list_height, font=('Consolas', 9))
                common_list.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

                # 右键菜单
                common_menu = tk.Menu(window, tearoff=0)
                common_menu.add_command(label="复制选中项", command=lambda: window.clipboard_clear() or 
                                      window.clipboard_append('\n'.join([common_list.get(i) for i in common_list.curselection()])))

                def show_common_menu(event):
                    try:
                        common_menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        common_menu.grab_release()

                common_list.bind("<Button-3>", show_common_menu)

                common_scrollbar = ttk.Scrollbar(common_frame, orient="vertical", command=common_list.yview)
                common_scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=5)
                common_list.config(yscrollcommand=common_scrollbar.set)

                for item in common_files:
                    common_list.insert(tk.END, item)

                current_row += 1

            # 显示文件分布矩阵
            if pattern_files:
                matrix_frame = ttk.LabelFrame(main_results_frame, text="文件分布矩阵")
                matrix_frame.grid(row=current_row, column=0, sticky='nsew', pady=(5, 0))
                matrix_frame.grid_rowconfigure(0, weight=1)
                matrix_frame.grid_columnconfigure(0, weight=1)

                main_results_frame.grid_rowconfigure(current_row, weight=1)

                canvas = tk.Canvas(matrix_frame, highlightthickness=0)
                scrollbar = ttk.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)

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

                    pattern_frame = ttk.LabelFrame(scrollable_frame, text=title)
                    pattern_frame.grid(row=pattern_row, column=0, sticky='ew', padx=5, pady=2)
                    pattern_frame.grid_columnconfigure(0, weight=1)
                    pattern_frame.grid_rowconfigure(1, weight=1)
                    scrollable_frame.grid_columnconfigure(0, weight=1)

                    # 创建文件列表
                    text_frame = ttk.Frame(pattern_frame)
                    text_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
                    text_frame.grid_rowconfigure(0, weight=1)
                    text_frame.grid_columnconfigure(0, weight=1)

                    text_height = min(8, max(3, len(files)))
                    files_text = tk.Text(text_frame, height=text_height, wrap=tk.WORD, font=('Consolas', 9))
                    files_text.grid(row=0, column=0, sticky='ew')

                    # 右键菜单
                    text_menu = tk.Menu(files_text, tearoff=0)
                    text_menu.add_command(label="复制选中文本", command=lambda: window.clipboard_clear() or 
                                        window.clipboard_append(files_text.get("sel.first", "sel.last")))
                    text_menu.add_command(label="粘贴", command=lambda: files_text.insert(tk.INSERT, window.clipboard_get()))
                    text_menu.add_separator()
                    text_menu.add_command(label="全选", command=lambda: files_text.tag_add(tk.SEL, "1.0", tk.END))

                    def show_text_menu(event):
                        try:
                            text_menu.tk_popup(event.x_root, event.y_root)
                        finally:
                            text_menu.grab_release()

                    files_text.bind("<Button-3>", show_text_menu)
                    files_text.bind("<Button-2>", show_text_menu)  # 支持Mac上的右键

                    if len(files) > text_height:
                        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=files_text.yview)
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
                                 font=('Arial', 12), fg='red')
            error_label.pack(pady=50)
            print(f"Error in update_results: {traceback.format_exc()}")

    # 创建主界面布局
    main_frame = ttk.Frame(window)
    main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=0, minsize=int(window_width * 0.3))
    main_frame.grid_columnconfigure(1, weight=1)

    # 左侧：文件夹管理区域
    left_frame = ttk.LabelFrame(main_frame, text="文件夹管理")
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
    left_frame.grid_rowconfigure(2, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)

    # 输入区域
    input_frame = ttk.Frame(left_frame)
    input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    input_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(input_frame, text="文件夹路径:").grid(row=0, column=0, sticky='w', pady=(0, 2))
    path_entry = ttk.Entry(input_frame, textvariable=current_path)
    path_entry.grid(row=1, column=0, sticky='ew', pady=(0, 5))
    path_entry.bind('<Return>', handle_return)

    # 路径输入框提示文本
    def on_entry_click(event):
        if path_entry.get() == "请粘贴或输入文件夹路径...":
            path_entry.delete(0, tk.END)
            path_entry.config(foreground='black')

    def on_focusout(event):
        if path_entry.get() == '':
            path_entry.insert(0, "请粘贴或输入文件夹路径...")
            path_entry.config(foreground='grey')

    path_entry.insert(0, "请粘贴或输入文件夹路径...")
    path_entry.config(foreground='grey')
    path_entry.bind('<FocusIn>', on_entry_click)
    path_entry.bind('<FocusOut>', on_focusout)

    # 添加Ctrl+V粘贴功能
    def paste_from_clipboard(event):
        try:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, window.clipboard_get())
        except:
            pass

    path_entry.bind('<Control-v>', paste_from_clipboard)

    # 按钮区域
    button_frame = ttk.Frame(input_frame)
    button_frame.grid(row=2, column=0, sticky='ew', pady=(0, 5))
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    ttk.Button(button_frame, text="添加路径 (Enter)", command=add_folder_text).grid(row=0, column=0, sticky='ew', padx=(0, 2))
    ttk.Button(button_frame, text="浏览文件夹", command=add_folder_dialog).grid(row=0, column=1, sticky='ew', padx=2)
    remove_btn = ttk.Button(button_frame, text="移除选中", command=remove_folder, state='disabled')
    remove_btn.grid(row=0, column=2, sticky='ew', padx=(2, 0))

    # 文件夹列表
    ttk.Label(left_frame, text="已添加的文件夹:").grid(row=1, column=0, sticky='w', padx=5, pady=(5, 2))

    list_frame = ttk.Frame(left_frame)
    list_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    folder_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=('Consolas', 9))
    folder_listbox.grid(row=0, column=0, sticky='nsew')

    # 文件夹列表滚动条

    list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=folder_listbox.yview)
    list_scrollbar.grid(row=0, column=1, sticky='ns')
    folder_listbox.config(yscrollcommand=list_scrollbar.set)

    # 状态和控制区域
    control_frame = ttk.Frame(left_frame)
    control_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    control_frame.grid_columnconfigure(0, weight=1)

    status_label = ttk.Label(control_frame, text="已添加文件夹: 0 个", font=('Arial', 10, 'bold'))
    status_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

    ttk.Button(control_frame, text="退出程序 (ESC)", command=exit_program).grid(row=2, column=0, sticky='ew', pady=2)

    # 右侧：结果显示区域
    results_frame = ttk.LabelFrame(main_frame, text="比较结果")
    results_frame.grid(row=0, column=1, sticky='nsew')
    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)

    # 结果显示区域

    # 初始化
    path_entry.focus()

    return window
