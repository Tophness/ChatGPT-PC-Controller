import os
import sys
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from openai_loader import OpenAILoader
import codecs
from tkhtmlview import HTMLLabel
import markdown

def iterate_js_files(directory, output_filename, output_type, file_types, prepend_text=""):
    output_text = ""
    if prepend_text:
        output_text += prepend_text + "\n\n"
    if directory:
        for filename in os.listdir(directory):
            if any(filename.endswith("." + file_type) for file_type in file_types):
                file_path = os.path.join(directory, filename)
                with open(file_path, "r") as js_file:
                    output_text += filename + ":\n"
                    output_text += js_file.read()
                    output_text += "\n\n"
        if output_type == "clipboard":
            window.clipboard_clear()
            window.clipboard_append(output_text)
        elif(output_type == "prompt"):
            loader = OpenAILoader()
            chatResult = loader.start(output_text)
            if(not chatResult):
                chatResult = loader.start(output_text, True)
            result_text.set_html(markdown.markdown(codecs.decode(str(chatResult).encode(), "unicode_escape")))
        else:
            with open(output_filename, "w") as output_file:
                output_file.write(output_text)

def browse_directory():
    directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, directory)
    output_type = output_type_var.get()
    if output_type == "clipboard":
        generate_output()

def browse_output_file():
    output_filename = filedialog.asksaveasfilename(defaultextension=".txt")
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(tk.END, output_filename)

def generate_output():
    directory = directory_entry.get()
    output_filename = output_file_entry.get()
    if not output_filename:
        output_filename = "prompt.txt"
    output_type = output_type_var.get()
    file_types = file_types_entry.get().split(",")
    prepend_text = prepend_text_entry.get("1.0", tk.END).strip()
    iterate_js_files(directory, output_filename, output_type, file_types, prepend_text)

def handle_output_type_change():
    if(output_type_var.get() == "clipboard" or output_type_var.get() == "prompt"):
        output_file_entry.config(state="disabled")
        browse_output_button.config(state="disabled")
    else:
        output_file_entry.config(state="normal")
        browse_output_button.config(state="normal")
    if(output_type_var.get() == "prompt"):
        result_text.config(state="normal")
    else:
        result_text.config(state="disabled")

window = tk.Tk()
window.title("ChatGPT Uploader")
window.geometry("400x550")

prepend_text_label = tk.Label(window, text="Prepend Text:")
prepend_text_label.pack()

prepend_text_entry = tk.Text(window, height=4, width=50)
prepend_text_entry.pack()

directory_label = tk.Label(window, text="Input Directory:")
directory_label.pack()

directory_entry = tk.Entry(window, width=50)
directory_entry.pack()

file_types_label = tk.Label(window, text="File Types (comma-separated):")
file_types_label.pack()

file_types_entry = tk.Entry(window, width=50)
file_types_entry.pack()
file_types_entry.insert(tk.END, "js,json,py")

browse_button = tk.Button(window, text="Browse", command=browse_directory)
browse_button.pack()

output_type_label = tk.Label(window, text="Output Type:")
output_type_label.pack()

output_type_var = tk.StringVar(value="prompt")
output_type_frame = ttk.Frame(window)
output_type_frame.pack()

prompt_radio = ttk.Radiobutton(output_type_frame, text="Prompt", value="prompt", variable=output_type_var, command=handle_output_type_change)
prompt_radio.pack()

clipboard_radio = ttk.Radiobutton(output_type_frame, text="Copy to Clipboard", value="clipboard", variable=output_type_var, command=handle_output_type_change)
clipboard_radio.pack()

file_radio = ttk.Radiobutton(output_type_frame, text="Save to File", value="file", variable=output_type_var, command=handle_output_type_change)
file_radio.pack()

output_file_label = tk.Label(window, text="Output Text File:")
output_file_label.pack()

output_file_entry = tk.Entry(window, width=50)
output_file_entry.pack()
output_file_entry.insert(tk.END, "prompt.txt")

browse_output_button = tk.Button(window, text="Browse", command=browse_output_file)
browse_output_button.pack()

result_text = HTMLLabel(window, width=50, height=10, state="disabled", html='<html></html>')
result_text.pack()

generate_button = tk.Button(window, text="Generate Output", command=generate_output)
generate_button.pack()

handle_output_type_change()

window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 3:
        directory_path = sys.argv[1]
        output_filename = sys.argv[2]
        iterate_js_files(directory_path, output_filename)