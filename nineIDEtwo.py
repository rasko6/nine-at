import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re

class NineEdit:
    def __init__(self, root):
        self.root = root
        self.root.title("NineEdit - Nine@ IDE")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        self.current_file = None
        self.file_changed = False
        self.process = None
        
        self.setup_menu()
        self.setup_toolbar()
        self.setup_editor()
        self.setup_output()
        self.setup_statusbar()
        self.bind_shortcuts()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Run in Terminal", command=self.run_in_terminal)
        run_menu.add_separator()
        run_menu.add_command(label="Stop", command=self.stop_code)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Commands Reference", command=self.show_commands)
        tools_menu.add_command(label="About", command=self.show_about)
        
    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text="Run (F5)", command=self.run_code).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="Stop", command=self.stop_code).pack(side=tk.LEFT, padx=2, pady=2)
        
    def setup_editor(self):
        editor_frame = tk.Frame(self.root)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.line_numbers = tk.Text(editor_frame, width=5, padx=3, takefocus=0, border=0,
                                    background='#3c3f41', foreground='#888888', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE,
                                                  font=('Consolas', 11),
                                                  background='#2b2b2b',
                                                  foreground='#a9b7c6',
                                                  insertbackground='white',
                                                  selectbackground='#214283',
                                                  undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        self.setup_syntax_highlighting()
        self.editor.bind('<KeyRelease>', self.on_edit)
        
    def setup_syntax_highlighting(self):
        self.editor.tag_configure("header", foreground="#ff3333", font=("Consolas", 11, "bold")) 
        self.editor.tag_configure("kw", foreground="#ff6666")     
        self.editor.tag_configure("comment", foreground="#5e5e5e") 
        
    def highlight_syntax(self, event=None):
        keywords = ["print", "var", "calc", "if", "else", "while", "random", "wait", "input", "cls", "exit"]
        
        for tag in ["kw", "header", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
        
        start = "1.0"
        while True:
            start = self.editor.search("nine@", start, stopindex=tk.END)
            if not start: break
            end = f"{start}+{len('nine@')}c"
            self.editor.tag_add("header", start, end)
            start = end

        for kw in keywords:
            start = "1.0"
            while True:
                start = self.editor.search(rf"\y{kw}\y", start, stopindex=tk.END, regexp=True)
                if not start: break
                end = f"{start}+{len(kw)}c"
                self.editor.tag_add("kw", start, end)
                start = end

        start = "1.0"
        while True:
            start = self.editor.search("//", start, stopindex=tk.END)
            if not start: break
            end = self.editor.index(f"{start} lineend")
            self.editor.tag_add("comment", start, end)
            start = end
        
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        lines = int(self.editor.index('end-1c').split('.')[0])
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
        
    def on_edit(self, event=None):
        self.file_changed = True
        self.highlight_syntax()
        self.update_line_numbers()
        
    def setup_output(self):
        output_frame = tk.LabelFrame(self.root, text="Output", bg='#2b2b2b', fg='#a9b7c6')
        output_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        self.output = scrolledtext.ScrolledText(output_frame, height=10,
                                                  font=('Consolas', 10),
                                                  background='#2b2b2b',
                                                  foreground='#a9b7c6')
        self.output.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(output_frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(btn_frame, text="Clear", command=self.clear_output).pack(side=tk.RIGHT, padx=2)
        
    def setup_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())

    def new_file(self):
        self.editor.delete('1.0', tk.END)
        self.current_file = None
        self.file_changed = False

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', f.read())
            self.current_file = path
            self.highlight_syntax()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get('1.0', tk.END))
            self.file_changed = False
        else:
            self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".nin")
        if path:
            self.current_file = path
            self.save_file()

    def run_code(self):
        self.output.delete('1.0', tk.END)
        code = self.editor.get("1.0", tk.END)
        with open("temp_run.nin", "w", encoding="utf-8") as f:
            f.write(code)
        try:
            import ninecompiler
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            ninecompiler.run_nine("temp_run.nin")
            self.output.insert(tk.END, sys.stdout.getvalue())
            sys.stdout = old_stdout
        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}")

    def stop_code(self): pass
    def run_in_terminal(self): pass
    def cut(self): self.editor.event_generate("<<Cut>>")
    def copy(self): self.editor.event_generate("<<Copy>>")
    def paste(self): self.editor.event_generate("<<Paste>>")
    def clear_output(self): self.output.delete('1.0', tk.END)
    def show_commands(self): pass
    def show_about(self): pass
    def exit_app(self): self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NineEdit(root)
    root.mainloop()
