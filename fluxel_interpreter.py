import sys
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import google.generativeai as genai

def main():
    if len(sys.argv) != 2:
        print("Usage: fluxel Script.flux")
    else:
        execute_script(sys.argv[1])

if __name__ == "__main__":
    main()

def execute_line(line, vars, window):
    line = line.strip()
    if line.startswith("var "):
        var_declaration = line[4:].strip()
        var_name, var_value = var_declaration.split(" = ", 1)
        if var_value.strip() == "entry":
            vars[var_name.strip()] = tk.Entry(window["root"])
            vars[var_name.strip()].pack()
        elif var_value.strip() == "text":
            vars[var_name.strip()] = tk.Text(window["root"])
            vars[var_name.strip()].pack()
        else:
            vars[var_name.strip()] = eval(var_value.strip())
    elif line.startswith("say "):
        message = line[4:].strip()
        parts = re.split(r'("\s*\+\s*"|\s*\+\s*)', message)
        result = ""
        for part in parts:
            if part.strip() in ['+', '"+"']:
                continue
            if part.startswith('"') and part.endswith('"'):
                result += part[1:-1]
            else:
                result += str(vars.get(part.strip(), ''))
        print(result)
    elif line.startswith("ask "):
        question = line[4:].strip().strip('"')
        answer = input(question + " ")
        vars["user_input"] = answer
    elif line.startswith("remember "):
        var_name = line[9:].strip()
        vars[var_name] = vars["user_input"]
    elif line.strip() == "pause":
        input("Press Enter to continue...")
    elif line.startswith("window "):
        title = line[7:].strip().strip('"')
        window["root"] = tk.Tk()
        window["root"].title(title)
    elif line.startswith("windowsize "):
        size = line[11:].strip().strip('"')
        width, height = map(int, size.split(','))
        window["root"].geometry(f"{width}x{height}")
    elif line.startswith("button "):
        parts = line.split('"')
        text = parts[1]
        command = parts[3]
        if "objectLocation" in line:
            location = line.split("objectLocation =")[1].strip().split(",")
            x, y = map(int, location)
            button = tk.Button(window["root"], text=text, command=lambda: execute_line(command, vars, window))
            button.place(x=x, y=y)
        else:
            tk.Button(window["root"], text=text, command=lambda: execute_line(command, vars, window)).pack()
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

def execute_script(filename):
    vars = {}
    window = {}
    with open(filename, 'r') as file:
        for line in file:
            execute_line(line, vars, window)
    
    # Add an automatic pause at the end of the script
    input("Press Enter to exit...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fluxel_interpreter.py Script.flux")
    else:
        execute_script(sys.argv[1])