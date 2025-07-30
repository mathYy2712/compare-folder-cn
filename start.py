"""
文件夹比较工具 - 独立启动版本
解决模块导入问题
"""

import sys
import traceback
from tkinter import messagebox
from ui import create_main_window


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器
    捕获未处理的异常并显示友好的错误信息
    """
    # 允许键盘中断正常处理
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 格式化异常信息
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"未处理的异常: {error_msg}")

    # 显示错误对话框
    try:
        messagebox.showerror(
            "程序错误", 
            f"程序遇到未处理的错误:\n{str(exc_value)}\n\n"
            f"详细信息已输出到控制台"
        )
    except Exception:
        # 如果无法显示对话框，则只在控制台输出
        pass


def main():
    """主程序入口"""
    # 设置全局异常处理
    sys.excepthook = handle_exception

    try:
        # 创建并运行主窗口
        window = create_main_window()
        if window:
            window.mainloop()
        else:
            print("创建主窗口失败")
    except Exception as e:
        error_msg = f"程序启动失败: {str(e)}"
        print(f"启动错误: {traceback.format_exc()}")
        try:
            messagebox.showerror("启动错误", error_msg)
        except Exception:
            print(error_msg)
    except KeyboardInterrupt:
        print("程序被用户中断")


if __name__ == "__main__":
    main()
