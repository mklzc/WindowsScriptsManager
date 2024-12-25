import os
import subprocess
import tkinter as tk
from tkinter import messagebox

class ScriptManagerApp:
    def __init__(self, _root):
        self.SCRIPT_LIST_FILE = "scripts.txt"
        self._root = _root
        self._root.title("Script Manager")
        self._root.geometry("400x270")

        self.scripts = self.load_scripts()
        self.script_listbox = None

        self.create_ui()
        self.update_script_list()

    def load_scripts(self):
        if not os.path.exists(self.SCRIPT_LIST_FILE):
            messagebox.showerror("错误", f"脚本列表文件 {self.SCRIPT_LIST_FILE} 不存在！")
            return []

        with open(self.SCRIPT_LIST_FILE, "r", encoding="utf-8") as file:
            scripts = [line.strip() for line in file if line.strip()]
        return scripts

    def open_scripts_file(self):
        subprocess.run(["notepad", self.SCRIPT_LIST_FILE], check=True)

        self.scripts = self.load_scripts()
        self.update_script_list()
        return

    def create_ui(self):
        edit_script_btn = tk.Button(self._root, text="编辑", command=self.open_scripts_file,
                                   bg="green", fg="white")
        edit_script_btn.pack()

        self.script_listbox = tk.Listbox(self._root, height=10, width=50)
        self.script_listbox.pack(pady=10)

        run_script_btn = tk.Button(self._root, text="运行", command=self.run_script, bg="lightblue")
        run_script_btn.pack()

    def update_script_list(self):
        print(self.scripts)
        self.script_listbox.delete(0, tk.END)
        for script in self.scripts:
            print(script)
            self.script_listbox.insert(tk.END, script)

    def run_script(self):
        selected_index = self.script_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("提示", "请先选择一个脚本")
            return

        script_path = self.scripts[selected_index[0]]
        try:
            ext = os.path.splitext(script_path)[1].lower()
            if ext == ".py":
                subprocess.run(["python", script_path], check=True)
            elif ext == ".sh":
                subprocess.run(["bash", script_path], check=True)
            elif ext == ".bat":
                subprocess.run([script_path], shell=True, check=True)
            elif ext == ".ps1":
                subprocess.run(["powershell", "-File", script_path], check=True)
            elif ext == ".exe":
                subprocess.run([script_path], check=True)
            else:
                tk.messagebox.showerror("错误", f"不支持的脚本类型: {ext}")
            subprocess.run(["python", script_path], capture_output=True, text=True)

        except Exception as e:
            messagebox.showerror("错误", f"脚本运行失败：{e}")


if __name__ == "__main__":
    _root = tk.Tk()
    app = ScriptManagerApp(_root)
    _root.mainloop()
