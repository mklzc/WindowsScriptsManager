import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageTk

def run_script(script_path, params, selected_mode):
    try:
        log_file = f"{os.path.basename(script_path)}.log"

        with open(log_file, "w+") as logfile:
            ext = os.path.splitext(script_path)[1].lower()
            if ext == ".py":
                command = ["python", script_path] + params.split()
            elif ext == ".sh":
                command = ["bash", script_path] + params.split()
            elif ext == ".ps1":
                command = ["powershell", "-File", script_path] + params.split()
            else:
                command = [script_path] + params.split()

            if selected_mode == "直接运行":
                subprocess.run(command, stdout=logfile, stderr=logfile, check=True)
            else:
                subprocess.Popen(
                    command,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdout=logfile,
                    stderr=logfile,
                )
    except Exception as e:
        messagebox.showerror("错误", f"脚本运行失败：{e}")

class ScriptManagerApp:
    def __init__(self, _root):
        self.script_list_context_menu = None
        self.SCRIPT_LIST_FILE = "scripts.txt"
        self._root = _root
        self._root.title("Script Manager")
        self._root.geometry("1000x600")
        self._root.iconbitmap("icon.ico")
        self.style = ttk.Style(theme="minty")

        self.run_mode_var = tk.StringVar()
        self.param_entry = tk.Entry()
        self.run_mode_var.set("直接运行")
        self.scripts = []
        self.script_listbox = None
        self.create_ui()
        self.load_scripts()
        self.tray_icon = None
        self.create_tray_icon()
        self._root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def create_tray_icon(self):
        # 托盘图标的图标文件
        image = Image.open("icon.ico")  # 确保提供一个有效的 .ico 文件

        # 托盘菜单
        menu = Menu(
            MenuItem("显示窗口", self.restore_window),
            MenuItem("退出", action=self.exit_app)
        )

        # 创建托盘图标
        self.tray_icon = Icon("TkApp", image, "托盘图标示例", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def minimize_to_tray(self):
        self._root.withdraw()

    def restore_window(self):
        self._root.deiconify()

    def exit_app(self, icon: Icon):
        icon.stop()
        self._root.quit()
        self._root.destroy()

    def load_scripts(self):
        with open(self.SCRIPT_LIST_FILE, "r+", encoding="utf-8") as file:
            scripts = [line.strip() for line in file if line.strip()]

        self.scripts = scripts
        self.update_script_list()

    def open_scripts_file(self):
        subprocess.run(["notepad", self.SCRIPT_LIST_FILE], check=True)

        self.load_scripts()
        self.update_script_list()
        return

    def create_ui(self):

        # 编辑按钮
        edit_script_btn = ttk.Button(self._root, text="编辑列表", command=self.open_scripts_file, style=INFO)
        edit_script_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w", ipadx=20, ipady=10)

        # 刷新按钮
        refresh_script_btn = ttk.Button(self._root, text="刷新列表", command=self.load_scripts, style=INFO)
        refresh_script_btn.grid(row=0, column=2, padx=10, pady=10, sticky="e", ipadx=20, ipady=10)

        # 脚本列表
        self.script_listbox = tk.Listbox(self._root, height=10, width=50)
        self.script_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 右键菜单
        self.script_list_context_menu = tk.Menu(self._root, tearoff=0)
        self.script_list_context_menu.add_command(label="清空日志", command=self.clear_selected_script_log)
        self.script_list_context_menu.add_command(label="显示日志", command=self.view_log)
        self.script_listbox.bind("<Button-3>", self.show_script_context_menu)

        # 运行模式选择
        run_mode_combobox = ttk.Combobox(
            self._root, textvariable=self.run_mode_var, state="readonly", values=["直接运行", "后台运行"]
        )
        run_mode_combobox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # 参数选择
        tk.Label(self._root, text="参数:").grid(row=2, column=1, padx=10, sticky="w")
        self.param_entry = tk.Entry(self._root, width=40)
        self.param_entry.grid(row=2, column=2, padx=10, pady=10, sticky="e")

        # 运行按钮
        run_script_btn = ttk.Button(self._root, text="运行", command=self.run_script_based_on_mode, style=PRIMARY)
        run_script_btn.grid(row=3, column=0, padx=10, pady=10, sticky="nsew", ipadx=20, ipady=10)

    def update_script_list(self):
        self.script_listbox.delete(0, tk.END)
        for script in self.scripts:
            self.script_listbox.insert(tk.END, script)

    def run_script_based_on_mode(self):
        selected_index = self.script_listbox.curselection()
        selected_mode = self.run_mode_var.get()
        params = self.param_entry.get()

        if not selected_index:
            messagebox.showwarning("提示", "请先选择一个脚本")
            return

        script_path = self.scripts[selected_index[0]]
        run_script(script_path, params, selected_mode)

    def view_log(self):
        selected_index = self.script_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("提示", "请先选择一个脚本")
            return

        script_path = self.scripts[selected_index[0]]
        log_file = f"{os.path.basename(script_path)}.log"
        if not os.path.exists(log_file):
            messagebox.showwarning("提示", "该脚本还没有生成日志文件")
            return

        log_window = tk.Toplevel(self._root)
        log_window.title(f"{os.path.basename(script_path)} 日志")
        log_window.geometry("1000x600")
        text_area = tk.Text(log_window, wrap="word", height=15)
        text_area.pack(fill="x", padx=10, pady=10)

        with open(log_file, "r") as logfile:
            text_area.insert("1.0", logfile.read())

        def refresh_log():
            with open(log_file, "r") as f:
                text_area.delete("1.0", tk.END)
                text_area.insert("1.0", f.read())

        refresh_button = ttk.Button(log_window, text="刷新", command=refresh_log)
        refresh_button.pack(side="bottom", pady=5)

    def clear_selected_script_log(self):
        selected_index = self.script_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("提示", "请先选择一个脚本")
            return

        script_path = self.scripts[selected_index[0]]
        log_file = f"{os.path.basename(script_path)}.log"
        try:
            with open(log_file, "w") as logfile:
                logfile.write("")
            messagebox.showinfo("提示", f"{os.path.basename(script_path)}的日志已清空")
        except Exception as e:
            messagebox.showerror("错误", "无法清空日志文件")

    def show_script_context_menu(self, event):
        try:
            index = self.script_listbox.nearest(event.y)
            self.script_listbox.selection_clear(0, tk.END)
            self.script_listbox.selection_set(index)
            self.script_listbox.activate(index)
            self.script_list_context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass


if __name__ == "__main__":
    _root = ttk.Window()

    app = ScriptManagerApp(_root)
    _root.mainloop()
