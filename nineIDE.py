import tkinter as tk
from tkinter import scrolledtext
import sys
import io
import os

try:
    import ninecompiler 
except ImportError:
    print("Error: ninecompiler.py not found in the same folder!")

def run_code():
    output_area.config(state=tk.NORMAL)
    output_area.delete("1.0", tk.END)
    code = code_area.get("1.0", tk.END)
    with open("temp_run.nin", "w", encoding="utf-8") as f:
        f.write(code)

    class RedirectText:
        def __init__(self, widget):
            self.widget = widget
        def write(self, string):
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)
            root.update()
        def flush(self):
            pass

    old_stdout = sys.stdout
    sys.stdout = RedirectText(output_area)
    try:
        ninecompiler.run_nine("temp_run.nin")
    except Exception as e:
        print(f"\nSystem Error: {e}")
    finally:
        sys.stdout = old_stdout
        output_area.config(state=tk.DISABLED)

def highlight_syntax(event=None):
    keywords = ["print", "var", "calc", "if", "else", "while", "random", "wait", "input", "cls", "exit"]
    
    for tag in ["kw", "header", "comment"]:
        code_area.tag_remove(tag, "1.0", tk.END)
    
    start = "1.0"
    while True:
        start = code_area.search("nine@", start, stopindex=tk.END)
        if not start: break
        end = f"{start}+{len('nine@')}c"
        code_area.tag_add("header", start, end)
        start = end

    for kw in keywords:
        start = "1.0"
        while True:
            start = code_area.search(rf"\y{kw}\y", start, stopindex=tk.END, regexp=True)
            if not start: break
            end = f"{start}+{len(kw)}c"
            code_area.tag_add("kw", start, end)
            start = end

    start = "1.0"
    while True:
        start = code_area.search("//", start, stopindex=tk.END)
        if not start: break
        end = code_area.index(f"{start} lineend")
        code_area.tag_add("comment", start, end)
        start = end

root = tk.Tk()
root.title("nine@ IDE")
root.geometry("950x650")
root.configure(bg="#1a1a1a")

code_area = tk.Text(root, font=("Consolas", 13), bg="#141414", fg="#f0f0f0", 
                    insertbackground="#ff4d4d", undo=True, bd=0, padx=15, pady=15)
code_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

code_area.tag_config("header", foreground="#ff3333", font=("Consolas", 13, "bold")) 
code_area.tag_config("kw", foreground="#ff6666")     
code_area.tag_config("comment", foreground="#5e5e5e") 

code_area.bind("<KeyRelease>", highlight_syntax)

run_btn = tk.Button(root, text="▶ RUN", command=run_code, 
                    bg="#b30000", fg="white", font=("Segoe UI", 11, "bold"), 
                    activebackground="#e60000", activeforeground="white",
                    relief=tk.FLAT, pady=8, cursor="hand2")
run_btn.pack(fill=tk.X, padx=20, pady=5)

output_area = scrolledtext.ScrolledText(root, height=12, font=("Consolas", 11), 
                                        bg="#13141B", fg="#ff8080", bd=0, padx=15, pady=10)
output_area.pack(fill=tk.X, padx=10, pady=10)

code_area.insert("1.0", "nine@\n\n// Welcome to nine@ IDE\nvar x = 1\nwhile x < 5 {\n    print Hello_Nineat\n    calc x + 1\n    var x = res\n}")
highlight_syntax()

root.mainloop()
