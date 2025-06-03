import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import psutil
import os
import threading
import time
import pywinctl as pwc

def is_gui_application(process):
    try:
        windows = pwc.getAllWindows()
        for window in windows:
            if window.getPID() == process.info["pid"]:
                return True
        return False
    except Exception:
        return False

def get_active_apps():
    active_apps = {}
    for proc in psutil.process_iter(attrs=["pid", "name", "memory_info", "status", "username"]):
        try:
            if proc.info["status"] == psutil.STATUS_RUNNING and proc.info["name"] and proc.info["pid"]:
                if proc.info["username"] and is_gui_application(proc):
                    name = proc.info["name"].lower()
                    pid = proc.info["pid"]
                    memory = round(proc.info["memory_info"].rss / (1024 * 1024), 2)
                    if name not in active_apps:
                        active_apps[name] = (pid, memory)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted([(pid, name, memory) for name, (pid, memory) in active_apps.items()], key=lambda x: x[1])

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RDJD's Task Manager")
        self.root.geometry("800x500")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        
        self.process_tab = ProcessTab(self.notebook)
        self.task_tab = TaskTab(self.notebook)
        self.performance_tab = PerformanceTab(self.notebook)
        
        self.notebook.add(self.process_tab.frame, text="Processes")
        self.notebook.add(self.task_tab.frame, text="Tasks")
        self.notebook.add(self.performance_tab.frame, text="Performance")
        
        self.update_thread = threading.Thread(target=self.auto_refresh, daemon=True)
        self.update_thread.start()
        
    def auto_refresh(self):
        while True:
            self.process_tab.update_processes()
            self.task_tab.update_tasks()
            self.performance_tab.update_performance()
            time.sleep(5)

class ProcessTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, font=("Arial", 12))
        self.search_entry.pack(fill="x", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_processes)
        
        self.tree = ttk.Treeview(self.frame, columns=("PID", "Name", "Memory"), show="headings")
        self.tree.heading("PID", text="PID", anchor=tk.CENTER)
        self.tree.heading("Name", text="Process Name", anchor=tk.CENTER)
        self.tree.heading("Memory", text="Memory (MB)", anchor=tk.CENTER)
        self.tree.column("PID", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=300, anchor=tk.CENTER)
        self.tree.column("Memory", width=150, anchor=tk.CENTER)
        self.tree.pack(expand=True, fill="both")
        
        self.refresh_button = ttk.Button(self.frame, text="Refresh", command=self.update_processes)
        self.refresh_button.pack(pady=5)
        
        self.kill_button = ttk.Button(self.frame, text="Kill Process", command=self.kill_process)
        self.kill_button.pack(pady=5)
        
        self.update_processes()
        
    def update_processes(self, event=None):
        self.tree.delete(*self.tree.get_children())
        search_query = self.search_var.get().lower()
        
        for proc in psutil.process_iter(attrs=["pid", "name", "memory_info"]):
            try:
                pid = proc.info["pid"]
                name = proc.info["name"]
                memory = round(proc.info["memory_info"].rss / (1024 * 1024), 2)
                
                if search_query in name.lower():
                    self.tree.insert("", "end", values=(pid, name, memory))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
    def kill_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No process selected.")
            return
        
        pid = int(self.tree.item(selected_item, "values")[0])
        try:
            psutil.Process(pid).terminate()
            self.update_processes()
            messagebox.showinfo("Success", f"Process {pid} terminated.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "Process no longer exists.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Permission denied.")

class TaskTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, font=("Arial", 12))
        self.search_entry.pack(fill="x", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_tasks)
        
        self.tree = ttk.Treeview(self.frame, columns=("PID", "Name", "Memory"), show="headings")
        self.tree.heading("PID", text="PID", anchor=tk.CENTER)
        self.tree.heading("Name", text="Task Name", anchor=tk.CENTER)
        self.tree.heading("Memory", text="Memory (MB)", anchor=tk.CENTER)
        self.tree.column("PID", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=300, anchor=tk.CENTER)
        self.tree.column("Memory", width=150, anchor=tk.CENTER)
        self.tree.pack(expand=True, fill="both")
        
        self.refresh_button = ttk.Button(self.frame, text="Refresh", command=self.update_tasks)
        self.refresh_button.pack(pady=5)
        
        self.add_task_button = ttk.Button(self.frame, text="Run New Task", command=self.open_task)
        self.add_task_button.pack(pady=5)
        
        self.end_task_button = ttk.Button(self.frame, text="End Task", command=self.end_task)
        self.end_task_button.pack(pady=5)
        
        self.update_tasks()
        
    def update_tasks(self, event=None):
        current_tasks = {item: self.tree.item(item, "values") for item in self.tree.get_children()}
        tasks = get_active_apps()
        tasks.sort(key=lambda x: x[1].lower())
        
        for pid, name, memory in tasks:
            if str(pid) not in current_tasks:
                self.tree.insert("", "end", values=(pid, name, memory), iid=str(pid))
        
        for item in current_tasks:
            if int(item) not in [task[0] for task in tasks]:
                self.tree.delete(item)
        
    def open_task(self):
        file_path = filedialog.askopenfilename(title="Select Application")
        if file_path:
            try:
                os.startfile(file_path)
                messagebox.showinfo("Success", f"Opened: {file_path}")
                self.update_tasks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open: {e}")
    
    def end_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No task selected.")
            return
        
        pid = int(selected_item[0])
        try:
            psutil.Process(pid).terminate()
            self.update_tasks()
            messagebox.showinfo("Success", f"Task {pid} terminated.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "Task no longer exists.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Permission denied.")

class PerformanceTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        
        self.cpu_label = ttk.Label(self.frame, text="CPU Usage: ", font=("Arial", 12))
        self.cpu_label.pack(pady=2)
        
        self.memory_label = ttk.Label(self.frame, text="Memory Usage: ", font=("Arial", 12))
        self.memory_label.pack(pady=2)
        
        self.disk_label = ttk.Label(self.frame, text="Disk Usage: ", font=("Arial", 12))
        self.disk_label.pack(pady=2)
        
        self.update_performance()
        
    def update_performance(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent}%")
        self.memory_label.config(text=f"Memory Usage: {memory_info.percent}%")
        self.disk_label.config(text=f"Disk Usage: {disk_usage.percent}%")
        
        self.frame.after(5000, self.update_performance)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()