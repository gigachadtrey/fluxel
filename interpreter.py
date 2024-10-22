import sys
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import google.generativeai as genai
import time

def execute_typewriter(text, duration, vars):
    total_chars = len(text)
    delay = duration / total_chars
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # New line at the end

def execute_typewriter_ask(text, duration, vars):
    total_chars = len(text)
    delay = duration / total_chars
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(" ")  # Add a space at the end
    sys.stdout.flush()
    answer = input()
    vars["user_input"] = answer
    print()  # New line at the end

def execute_wait(duration):
    try:
        duration = float(duration)
        print(f"Waiting for {duration} seconds...")
        time.sleep(duration)
        print("Wait completed.")
    except ValueError:
        print(f"Error: Invalid wait duration '{duration}'. Please use a number.")

def execute_silent_wait(duration):
    try:
        duration = float(duration)
        time.sleep(duration)
    except ValueError:
        print(f"Error: Invalid wait duration '{duration}'. Please use a number.")

def process_text(text, vars):
    parts = re.split(r'("\s*\+\s*"|\s*\+\s*)', text)
    result = ""
    for part in parts:
        if part.strip() in ['+', '"+"']:
            continue
        if part.startswith('"') and part.endswith('"'):
            result += part[1:-1]
        else:
            result += str(vars.get(part.strip(), ''))
    return result

def execute_line(line, vars, window):
    line = line.strip()
    try:
        if line.startswith("typewriter "):
            match = re.match(r'typewriter\s+(.*)\s+(\d+(?:\.\d+)?)\s*$', line)
            if match:
                text = match.group(1)
                duration = float(match.group(2))
                processed_text = process_text(text, vars)
                execute_typewriter(processed_text, duration, vars)
            else:
                raise ValueError("Invalid typewriter command format")
        elif line.startswith("typewriteask "):
            match = re.match(r'typewriteask\s+(.*?)(?:\s+(\d+(?:\.\d+)?))?\s*$', line)
            if match:
                text = match.group(1)
                duration = float(match.group(2)) if match.group(2) else 3.0  # Default duration of 3 seconds
                processed_text = process_text(text, vars)
                execute_typewriter_ask(processed_text, duration, vars)
            else:
                raise ValueError("Invalid typewriteask command format")
        elif line.startswith("wait "):
            duration = line[5:].strip()
            execute_wait(duration)
        elif line.startswith("silentWait "):
            duration = line[11:].strip()
            execute_silent_wait(duration)
        elif line.startswith("var "):
            var_declaration = line[4:].strip()
            var_name, var_value = var_declaration.split(" = ", 1)
            if var_value.strip() == "entry":
                vars[var_name.strip()] = tk.Entry(window.get("root"))
                vars[var_name.strip()].pack()
            elif var_value.strip() == "text":
                vars[var_name.strip()] = tk.Text(window.get("root"))
                vars[var_name.strip()].pack()
            else:
                vars[var_name.strip()] = eval(var_value.strip())
        elif line.startswith("say "):
            message = line[4:].strip()
            result = process_text(message, vars)
            print(result)
        elif line.startswith("ask "):
            question = line[4:].strip().strip('"')
            answer = input(question + " ")
            vars["user_input"] = answer
        elif line.startswith("remember "):
            var_name = line[9:].strip()
            vars[var_name] = vars.get("user_input", "")
        elif line.strip() == "pause":
            input("Press Enter to continue...")
        elif line.startswith("window "):
            title = line[7:].strip().strip('"')
            if "root" not in window:
                window["root"] = tk.Tk()
            window["root"].title(title)
        elif line.startswith("windowsize "):
            size = line[11:].strip().strip('"')
            width, height = map(int, size.split(','))
            window["root"].geometry(f"{width}x{height}")
        elif line.startswith("button "):
            parts = line.split('"')
            if len(parts) >= 4:
                text = parts[1]
                command = parts[3]
                if "objectLocation" in line:
                    location = line.split("objectLocation =")[1].strip().split(",")
                    x, y = map(int, location)
                    button = tk.Button(window["root"], text=text, command=lambda: execute_line(command, vars, window))
                    button.place(x=x, y=y)
                else:
                    tk.Button(window["root"], text=text, command=lambda: execute_line(command, vars, window)).pack()
            else:
                raise ValueError("Invalid button command format")
        elif line.startswith("label "):
            text = line[6:].strip().strip('"')
            tk.Label(window["root"], text=text).pack()
        elif line == "show window":
            window["root"].mainloop()
        elif line.startswith("message "):
            text = line[8:].strip().strip('"')
            messagebox.showinfo("Message", text)
        elif line.startswith("get entry "):
            var_name, entry_var = line[10:].strip().split()
            vars[var_name] = vars[entry_var].get()
        elif line.startswith("configure_gemini "):
            api_key = line[17:].strip().strip('"')
            genai.configure(api_key=api_key)
            vars["gemini_model"] = genai.GenerativeModel("gemini-1.0-pro")
        elif line.startswith("generate_content "):
            prompt = line[17:].strip().strip('"')
            response = vars["gemini_model"].generate_content(prompt)
            vars["gemini_response"] = response.text
        elif line.startswith("append_text "):
            _, var_name, text = line.split(None, 2)
            vars[var_name].insert(tk.END, eval(text.strip()) + "\n")
            vars[var_name].see(tk.END)
        else:
            print(f"Unknown command: {line}")
    except Exception as e:
        print(f"Error executing line '{line}': {str(e)}")

def execute_script(filename):
    vars = {}
    window = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            if line.strip():  # Skip empty lines
                execute_line(line, vars, window)

        if "root" in window:
            window["root"].mainloop()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error executing script: {str(e)}")
    finally:
        # Add an automatic pause at the end of the script
        input("Press Enter to exit...")

def main():
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <script.flux>")
    else:
        execute_script(sys.argv[1])

if __name__ == "__main__":
    main()