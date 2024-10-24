import sys
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import google.generativeai as genai
import time
import os
import math
import random
import datetime
import string
import itertools
import functools
import collections
from operator import itemgetter
from functools import reduce
import threading


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

def execute_conditional(condition, then_block, else_block, vars, window):
    condition = condition.strip()
    if '=' in condition:
        var, value = condition.split('=')
        var = var.strip()
        value = value.strip().strip('"')
        if vars.get(var) == value:
            for line in then_block:
                execute_line(line.strip(), vars, window)
        elif else_block:
            for line in else_block:
                execute_line(line.strip(), vars, window)
    else:
        print(f"Invalid condition: {condition}")




def clear_line():
    # Clear the current line in the console
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

def execute_blast(vars):
    # Game state variables
    human = "(ಠ_ಠ) ╦╤─"
    monster = "⩜⏖⩜"
    dead_monster = "X_X"  # Monster's dead representation
    bullet = ">"
    distance = 50  # Initial distance between human and monster
    blast_activated = False
    game_over = False

    # Function to display the current state
    def display_scene(bullet_pos, monster_state):
        clear_line()
        # Create the scene with the bullet position
        # Only show the bullet after it has been activated
        bullet_display = bullet if blast_activated else ''
        scene = f"{human}{' ' * bullet_pos}{bullet_display}{' ' * (distance - bullet_pos)}{monster_state}"
        sys.stdout.write(scene)
        sys.stdout.flush()

    # Function to handle the monster approaching
    def approach_monster():
        nonlocal distance, game_over
        while distance > 0 and not game_over:
            time.sleep(0.1)
            distance -= 1
            display_scene(-1, monster)  # Display monster approaching
        if distance == 0 and not blast_activated:
            game_over = True
            clear_line()
            sys.stdout.write("(X_X) ╦╤─  ⩜⏖⩜  \n")
            sys.stdout.write("You died!\n")
            sys.stdout.flush()

    # Function to handle the player's action (pressing Enter)
    def handle_input():
        nonlocal blast_activated, game_over
        bullet_pos = 0  # Starting position of the bullet
        while not game_over:
            input()  # Wait for the player to press Enter
            if not blast_activated:
                blast_activated = True
                # Animate the bullet traveling towards the monster
                while bullet_pos < distance:
                    bullet_pos += 1  # Move the bullet forward
                    display_scene(bullet_pos, monster)  # Update the scene with the bullet's position
                    time.sleep(0.1)  # Control speed of the bullet
                # Final display when the bullet reaches the monster
                clear_line()
                # Display the result with the dead monster without creating a new line
                display_scene(distance, dead_monster)  # Show the dead monster
                sys.stdout.write("\nYou did it! The monster died.\n")  # Final message
                sys.stdout.flush()
                game_over = True
                return  # Exit the function to prevent any further output

    # Start the game with the monster approaching in a separate thread
    monster_thread = threading.Thread(target=approach_monster)
    monster_thread.start()

    # Handle the player's input (waiting for Enter)
    handle_input()
    
    # Wait for the monster thread to finish
    monster_thread.join()


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
        if line == "blast":
            execute_blast(vars)
        elif line.startswith("if "):
            condition = line[3:]
            then_block = []
            else_block = []
            current_block = then_block
            for next_line in iter(lambda: next(lines, None), None):
                next_line = next_line.strip()
                if next_line == "else":
                    current_block = else_block
                elif next_line.startswith("if "):
                    break  # End the current block
                elif next_line:  # Only add non-empty lines
                    current_block.append(next_line)
            execute_conditional(condition, then_block, else_block, vars, window)
        elif line == "close":
            if 'root' in window and window['root']:
                window['root'].quit()
                window['root'].destroy()
            return "EXIT"
        elif line.startswith("typewriter "):
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
            var_name, var_value = var_declaration.split(" =", 1)  # Fixed to handle spaces correctly
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
                    location = line.split("objectLocation=")[1].strip().split(",")
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
    return None

def execute_script(filename):
    global lines
    vars = {}
    window = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        lines = iter(lines)
        for line in lines:
            if line.strip():  # Skip empty lines
                result = execute_line(line.strip(), vars, window)
                if result == "EXIT":
                    break

        if "root" in window and window["root"]:
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
