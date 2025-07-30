"""
交互模块
实现右键菜单和用户交互功能
"""

import tkinter as tk
from tkinter import messagebox
import pyperclip  # 用于剪贴板操作


class InteractionManager:
    """管理用户交互功能的类"""
    
    def __init__(self, root_window, path_entry, results_frame, compare_function):
        """
        初始化交互管理器
        
        Args:
            root_window: 主窗口对象
            path_entry: 路径输入框
            results_frame: 结果显示框架
            compare_function: 执行比较的函数
        """
        self.root_window = root_window
        self.path_entry = path_entry
        self.results_frame = results_frame
        self.compare_function = compare_function
        
        # 绑定右键菜单事件
        self._bind_right_click_menus()
    
    def _bind_right_click_menus(self):
        """绑定右键菜单事件"""
        # 为路径输入框绑定右键菜单
        self.path_entry.bind("<Button-3>", self._show_path_entry_menu)
        
        # 为结果框架绑定右键菜单
        self.results_frame.bind("<Button-3>", self._show_results_menu)
        
        # 为结果框架内的所有文本组件绑定右键菜单
        self.results_frame.bind("<Button-3>", self._show_text_copy_menu, add="+")
        
        # 绑定子组件的右键事件
        self.results_frame.bind("<Button-3>", self._bind_child_events, add="+")
    
    def _bind_child_events(self, event):
        """绑定子组件的事件"""
        # 为新创建的文本组件绑定右键菜单
        for child in self.results_frame.winfo_children():
            self._bind_widget_events(child)
    
    def _bind_widget_events(self, widget):
        """递归绑定组件事件"""
        # 为Text和Listbox组件绑定右键菜单
        if isinstance(widget, (tk.Text, tk.Listbox)):
            widget.bind("<Button-3>", self._show_text_copy_menu_for_widget, add="+")
        
        # 递归处理子组件
        for child in widget.winfo_children():
            self._bind_widget_events(child)
    
    def _show_path_entry_menu(self, event):
        """
        显示路径输入框的右键菜单
        
        Args:
            event: 鼠标事件
        """
        # 创建右键菜单
        menu = tk.Menu(self.root_window, tearoff=0)
        menu.add_command(label="粘贴路径", command=self._paste_path)
        menu.add_command(label="清除路径", command=self._clear_path)
        
        # 显示菜单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _paste_path(self):
        """粘贴剪贴板中的路径到输入框"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, clipboard_content)
        except Exception as e:
            messagebox.showerror("错误", f"粘贴路径失败: {str(e)}")
    
    def _clear_path(self):
        """清除路径输入框的内容"""
        self.path_entry.delete(0, tk.END)
    
    def _show_results_menu(self, event):
        """
        显示比较结果区域的右键菜单（未选中文本时）
        
        Args:
            event: 鼠标事件
        """
        # 检查是否点击在文本组件上
        widget = event.widget
        if isinstance(widget, (tk.Text, tk.Listbox)):
            # 如果是文本组件且有选中文本，则显示复制菜单
            try:
                if widget.selection_get():
                    self._show_text_copy_menu(event)
                    return
            except tk.TclError:
                # 没有选中文本，继续显示刷新菜单
                pass
        
        # 创建右键菜单
        menu = tk.Menu(self.root_window, tearoff=0)
        menu.add_command(label="刷新比较结果", command=self.compare_function)
        
        # 显示菜单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _show_text_copy_menu(self, event):
        """
        显示文本复制的右键菜单
        
        Args:
            event: 鼠标事件
        """
        widget = event.widget
        
        # 检查是否有选中文本
        try:
            selected_text = widget.selection_get()
            if selected_text:
                # 创建右键菜单
                menu = tk.Menu(self.root_window, tearoff=0)
                menu.add_command(label="复制", command=lambda: self._copy_text(selected_text))
                
                # 显示菜单
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()
        except tk.TclError:
            # 没有选中文本，显示刷新菜单
            self._show_results_menu(event)
    
    def _show_text_copy_menu_for_widget(self, event):
        """
        为特定组件显示文本复制的右键菜单
        
        Args:
            event: 鼠标事件
        """
        widget = event.widget
        
        # 检查是否有选中文本
        try:
            selected_text = widget.selection_get()
            if selected_text:
                # 创建右键菜单
                menu = tk.Menu(self.root_window, tearoff=0)
                menu.add_command(label="复制", command=lambda: self._copy_text(selected_text))
                
                # 显示菜单
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()
            else:
                # 没有选中文本，显示刷新菜单
                self._show_results_menu(event)
        except tk.TclError:
            # 没有选中文本，显示刷新菜单
            self._show_results_menu(event)
    
    def _copy_text(self, text):
        """
        复制文本到剪贴板
        
        Args:
            text: 要复制的文本
        """
        try:
            pyperclip.copy(text)
        except Exception as e:
            messagebox.showerror("错误", f"复制文本失败: {str(e)}")


def setup_context_menus(window, path_entry, results_frame, compare_function):
    """
    设置上下文菜单
    
    Args:
        window: 主窗口
        path_entry: 路径输入框组件
        results_frame: 结果显示框架
        compare_function: 刷新比较结果的函数
    """
    try:
        # 创建交互管理器实例
        interaction_manager = InteractionManager(
            window, 
            path_entry, 
            results_frame, 
            compare_function
        )
        return interaction_manager
    except Exception as e:
        print(f"设置上下文菜单失败: {e}")
        return None
