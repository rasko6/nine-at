import sys
import random
import os
import time  # Добавили этот импорт
from tkinter import simpledialog # Добавили для ввода внутри IDE

os.system("color 04")

def execute_command(cmd, args, variables, block=None):
    """function that can do any command"""
    cmd = cmd.strip().lower()
    args = args.strip()

    if cmd == "print":
        print(variables.get(args, args))

    elif cmd == "wait":
        try:
            time.sleep(float(args))
        except:
            pass


    elif cmd == "var":
        if "=" in args:
            name, val = args.split('=', 1)
            name = name.strip()
            try:
                variables[name] = eval(val.strip(), {}, variables)
            except:
                variables[name] = val.strip()

    elif cmd == "calc":
        try:
            result = eval(args, {}, variables)
            variables['res'] = result
            print(f"Result: {result}")
        except Exception as e:
            print(f"Calc Error: {e}")

    # --- НОВАЯ КОМАНДА RANDOM ---
    elif cmd == "random":
        try:
            # Ожидает формат: random 1,10
            low, high = args.split(',')
            result = random.randint(int(low), int(high))
            variables['res'] = result
            print(f"Random Result: {result}")
        except Exception as e:
            print(f"Random Error: {e}. Use format: random 1,10")

    elif cmd == "if":
        try:
            condition_met = eval(args, {}, variables)
            if condition_met and block:
                for block_line in block:
                    if not block_line: continue
                    c, a = (block_line.split(' ', 1) if ' ' in block_line else (block_line, ""))
                    execute_command(c, a, variables)
            return condition_met
        except Exception as e:
            print(f"If Error: {e}")

    elif cmd == "else":
        if block:
            for block_line in block:
                if not block_line: continue
                c, a = (block_line.split(' ', 1) if ' ' in block_line else (block_line, ""))
                execute_command(c, a, variables)

    elif cmd == "input":
        # simpledialog позволяет вводить данные прямо в IDE через окошко
        data = simpledialog.askstring("Nine@ Input", f"Enter value for {args}:")
        if data is None: data = "" # Если нажали отмену
        try:
            variables[args] = int(data) if "." not in data else float(data)
        except:
            variables[args] = data


    elif cmd == "cls": os.system('cls')
    elif cmd == "exit": sys.exit()
    
    return None

def run_nine(filename):
    variables = {'res': 0}
    last_if_result = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().lstrip('\ufeff')
            raw_lines = [l.strip() for l in content.splitlines()]
    except Exception as e:
        print(f"File Error: {e}")
        return

    if not raw_lines or raw_lines[0] != "nine@":
        print(f"Error: Missing 'nine@' header!")
        return

    print("-------------------------")

    i = 1
    while i < len(raw_lines):
        line = raw_lines[i]
        if not line or line.startswith("//") or line == "}":
            i += 1
            continue

        if "{" in line:
            header = line.split("{")[0].strip()
            cmd_part, condition = (header.split(' ', 1) if ' ' in header else (header, ""))
            
            block = []
            temp_i = i + 1
            nesting = 1
            while temp_i < len(raw_lines):
                if "{" in raw_lines[temp_i]: nesting += 1
                if "}" in raw_lines[temp_i]: nesting -= 1
                if nesting == 0: break
                block.append(raw_lines[temp_i])
                temp_i += 1
            
            if cmd_part.lower() == "while":
                while eval(condition, {}, variables):
                    for block_line in block:
                        if not block_line: continue
                        c, a = (block_line.split(' ', 1) if ' ' in block_line else (block_line, ""))
                        execute_command(c, a, variables)
                i = temp_i
            
            elif cmd_part.lower() == "else":
                if last_if_result is False:
                    execute_command(cmd_part, condition, variables, block)
                i = temp_i
                last_if_result = None
            
            else:
                last_if_result = execute_command(cmd_part, condition, variables, block)
                i = temp_i
        else:
            c, a = (line.split(' ', 1) if ' ' in line else (line, ""))
            execute_command(c, a, variables)
            if c.lower() != "else": last_if_result = None
            i += 1

    print("-------------------------")
    print("--- Execution Finished ---")

if __name__ == "__main__":
    if len(sys.argv) > 1: run_nine(sys.argv[1])
    else:
        path = input("Drag and drop .nin file: ").strip().replace('"', '')
        if os.path.exists(path): run_nine(path)
        input("Press Enter...")
