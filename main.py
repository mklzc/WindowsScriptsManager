import os
import subprocess
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading


def run_script(script_path, params, selected_mode):
    try:
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
            subprocess.run(command, check=True)
        else:
            subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as e:
        messagebox.showerror("错误", f"脚本运行失败：{e}")

def bg_run_script(script_path, params):
    thread = threading.Thread(target=run_script(script_path, params), daemon=True)
    thread.start()

class ScriptManagerApp:
    def __init__(self, _root):

        self.SCRIPT_LIST_FILE = "scripts.txt"
        self._root = _root
        self._root.title("Script Manager")
        self._root.geometry("1000x600")
        self.style = ttk.Style(theme="minty")

        self.run_mode_var = tk.StringVar()
        self.param_entry = tk.Entry()
        self.run_mode_var.set("直接运行")

        self.scripts = []
        self.script_listbox = None

        self.create_ui()
        self.load_scripts()

    def load_scripts(self):
        with open(self.SCRIPT_LIST_FILE, "w+", encoding="utf-8") as file:
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

if __name__ == "__main__":
    _root = ttk.Window()
    app = ScriptManagerApp(_root)
    _root.mainloop()
