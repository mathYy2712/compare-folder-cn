"""
主程序入口
启动文件夹比较工具
"""

import sys
import traceback
from tkinter import messagebox
from ui import create_main_window


def main():
    """主程序入口"""
    try:
        # 设置异常处理
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"Unhandled exception: {error_msg}")

            try:
                messagebox.showerror("程序错误", 
                                   f"程序遇到未处理的错误:\n{str(exc_value)}\n\n"
                                   f"详细信息已输出到控制台")
            except:
                pass

        sys.excepthook = handle_exception

        # 创建并运行主窗口
        window = create_main_window()
        if window:
            window.mainloop()
        else:
            print("Failed to create main window")

    except Exception as e:
        error_msg = f"程序启动失败: {str(e)}"
        print(f"Startup error: {traceback.format_exc()}")
        try:
            messagebox.showerror("启动错误", error_msg)
        except:
            print(error_msg)
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        try:
            if 'window' in locals():
                window.quit()
        except:
            pass


if __name__ == "__main__":
    main()
