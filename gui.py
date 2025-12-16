import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import csv

# Импорт логики (ваши файлы)
try:
    import assembler
    import interpreter
except ImportError as e:
    messagebox.showerror("Ошибка импорта", f"Не найден файл: {e.name}\nУбедитесь, что assembler.py и interpreter.py лежат рядом.")
    exit()

# --- ЦВЕТОВАЯ ПАЛИТРА (Dark Theme) ---
COLOR_BG = "#1e1e1e"
COLOR_FG = "#d4d4d4"
COLOR_ACCENT = "#007acc"
COLOR_SIDEBAR = "#252526"
COLOR_EDITOR = "#1e1e1e"
COLOR_SUCCESS = "#4caf50"
COLOR_TEST = "#FF9800"

class IDEApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UVM Studio - Variant 10 (CSV Support)")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLOR_BG)

        # Стилизация
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_FG)
        style.configure("TButton", background=COLOR_ACCENT, foreground="white", borderwidth=0)
        
        # --- МЕНЮ ---
        menubar = tk.Menu(root, bg=COLOR_SIDEBAR, fg=COLOR_FG)
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLOR_SIDEBAR, fg=COLOR_FG)
        file_menu.add_command(label="Открыть...", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menubar)

        # --- TOOLBAR ---
        toolbar = tk.Frame(root, bg=COLOR_SIDEBAR, height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.btn_run = tk.Button(toolbar, text="▶ Собрать и Запустить", command=self.run_process, 
                                 bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=10)
        self.btn_run.pack(side=tk.LEFT, padx=5)

        tk.Label(toolbar, text="Диапазон памяти:", bg=COLOR_SIDEBAR, fg=COLOR_FG).pack(side=tk.LEFT, padx=10)
        self.entry_range = tk.Entry(toolbar, width=10, bg="#3c3c3c", fg="white", insertbackground="white", relief="flat")
        self.entry_range.insert(0, "0:30")
        self.entry_range.pack(side=tk.LEFT)

        # --- РАБОЧАЯ ОБЛАСТЬ ---
        paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=COLOR_BG, sashwidth=4, sashrelief="flat")
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5)

        # Редактор (Слева)
        left_frame = tk.Frame(paned_window, bg=COLOR_BG)
        tk.Label(left_frame, text=" EDITOR (ASSEMBLER)", bg=COLOR_SIDEBAR, fg="#888", anchor="w").pack(fill=tk.X)
        self.code_editor = scrolledtext.ScrolledText(left_frame, font=("Consolas", 12), 
                                                     bg=COLOR_EDITOR, fg=COLOR_FG, insertbackground="white", undo=True)
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        # Дефолтный код
        self.code_editor.insert(tk.END, "; Пример (Векторы)\nLOAD 100\nLOAD 10\nWRITE 0\nLOAD 200\nLOAD 11\nWRITE 0\nLOAD 1\nLOAD 20\nWRITE 0\nLOAD 2\nLOAD 21\nWRITE 0\n; Операция SAR\nLOAD 10\nSAR 10\nLOAD 11\nSAR 10\n")
        paned_window.add(left_frame)

        # Результат (Справа)
        right_frame = tk.Frame(paned_window, bg=COLOR_BG)
        tk.Label(right_frame, text=" MEMORY DUMP (CSV)", bg=COLOR_SIDEBAR, fg="#888", anchor="w").pack(fill=tk.X)
        self.output_view = scrolledtext.ScrolledText(right_frame, font=("Consolas", 11), 
                                                     bg="#1e1e1e", fg="#ce9178", state='disabled')
        self.output_view.pack(fill=tk.BOTH, expand=True)
        paned_window.add(right_frame)

        # --- ЛОГИ (Снизу) ---
        log_frame = tk.Frame(root, bg=COLOR_BG, height=150)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Label(log_frame, text="OUTPUT / LOGS", bg=COLOR_SIDEBAR, fg="#888", anchor="w").pack(fill=tk.X)
        
        self.log_view = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 10), 
                                                  bg="#000000", fg="#cccccc", state='disabled')
        self.log_view.pack(fill=tk.BOTH, expand=True)

        self.log("System ready. Welcome to UVM Studio.")

    def log(self, message, level="INFO"):
        self.log_view.config(state='normal')
        prefix = f"[{level}] "
        self.log_view.insert(tk.END, prefix + message + "\n")
        self.log_view.see(tk.END)
        self.log_view.config(state='disabled')

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Assembler Files", "*.asm"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, content)
            self.log(f"Opened file: {file_path}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembler Files", "*.asm")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_editor.get("1.0", tk.END))
            self.log(f"Saved file: {file_path}")

    def run_process(self):
        self.log("--- Starting Build Process ---")
        code_text = self.code_editor.get("1.0", tk.END).strip()
        if not code_text:
            self.log("Error: Source code is empty.", "ERROR")
            return

        instructions = []
        try:
            lines = code_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                
                # --- АДАПТАЦИЯ ПОД НОВЫЙ ASSEMBLER.PY ---
                # Теперь там нет parse_line, но есть pack_command(cmd, args)
                parts = line.split()
                if not parts: continue
                
                cmd_name = parts[0]
                args = parts[1:]
                
                try:
                    bytes_list = assembler.pack_command(cmd_name, args)
                    if bytes_list:
                        instructions.extend(bytes_list)
                    elif bytes_list is None:
                        self.log(f"Assembler Warning: Unknown command at line {i+1}: '{line}'", "WARN")
                except Exception as parse_err:
                     self.log(f"Assembler Syntax Error at line {i+1}: {parse_err}", "ERROR")
                     return
                     
            self.log(f"Assembly complete. Size: {len(instructions)} bytes.")
        except Exception as e:
            self.log(f"Assembly Critical Error: {e}", "ERROR")
            return

        temp_bin = "temp_build.bin"
        temp_res = "temp_dump.csv" # ТЕПЕРЬ CSV
        
        try:
            with open(temp_bin, 'wb') as f:
                f.write(bytearray(instructions))
        except Exception as e:
             self.log(f"File System Error: {e}", "ERROR")
             return

        try:
            vm = interpreter.VM()
            dump_range = self.entry_range.get().strip()
            
            # Запуск VM
            vm.run(temp_bin, temp_res, dump_range)
            self.log(f"VM Executed successfully. Dumping memory {dump_range}.")

            # --- ЧТЕНИЕ CSV РЕЗУЛЬТАТА ---
            if os.path.exists(temp_res):
                with open(temp_res, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
                
                self.output_view.config(state='normal')
                self.output_view.delete("1.0", tk.END)
                self.output_view.insert(tk.END, csv_content)
                self.output_view.config(state='disabled')
            else:
                self.log("VM Error: No result file generated.", "ERROR")
        except Exception as e:
            self.log(f"Runtime Error: {e}", "ERROR")
        finally:
            if os.path.exists(temp_bin): os.remove(temp_bin)
            if os.path.exists(temp_res): os.remove(temp_res)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDEApp(root)
    root.mainloop()