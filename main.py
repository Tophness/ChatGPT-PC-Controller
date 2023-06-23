import autoit
import sys
import shlex
from OpenAIAPIGrabber.chat import OpenAIChat
import re

def extract_code_block(code_string):
    code_block_regex = "```([\w\W]*?)```" if code_string.count("`") == 6 else "`([\w\W]*?)`"
    match = re.search(code_block_regex, code_string)
    if match:
        return match.group(1).strip()
    return code_string

def execute_commands(cmd_string):
    commands = cmd_string.split(";")
    for cmd in commands:
        args = shlex.split(cmd)
        print(f'Command: {args[0]}, Arguments: {args[1:]}')
        if args[0] == "run":
            autoit.run(*args[1:])
        elif args[0] == "win_wait_active":
            if len(args) > 2: args[2] = int(args[2])
            autoit.win_wait_active(*args[1:])
        elif args[0] == "control_send":
            autoit.control_send(*args[1:])
        elif args[0] == "activate_window":
            autoit.win_activate(*args[1:])
        elif args[0] == "maximize_window":
            autoit.win_maximize(*args[1:])
        elif args[0] == "minimize_window":
            autoit.win_minimize(*args[1:])
        elif args[0] == "move_window":
            if len(args) > 2: args[2] = int(args[2])
            if len(args) > 3: args[3] = int(args[3])
            autoit.win_move(*args[1:])
        elif args[0] == "close_window":
            autoit.win_close(*args[1:])
        elif args[0] == "mouse_click":
            if len(args) > 2: args[2] = int(args[2])
            if len(args) > 3: args[3] = int(args[3])
            if len(args) > 4: args[4] = int(args[4])
            if len(args) > 5: args[5] = int(args[5])
            autoit.mouse_click(*args[1:])
        elif args[0] == "mouse_move":
            if len(args) > 1: args[1] = int(args[1])
            if len(args) > 2: args[2] = int(args[2])
            if len(args) > 3: args[3] = int(args[3])
            autoit.mouse_move(*args[1:])
        elif args[0] == "keyboard_send":
            autoit.send(*args[1:])
        else:
            print(f"Unknown command: {args[0]}")

if __name__ == "__main__":
    try:
        cmd_string = sys.argv[1]
    except IndexError:
        cmd_string = input("Enter a task: ")

    preprompt = '''
    You are directly controlling a windows PC using a python script that parses commands and runs them with autoit using the pyautoit library.
    Output only the command to run (inside a code block) and nothing else. Commands are separated by colons, and arguments to those commands are separated by spaces. Argument strings must be encased in single quotes.
    Here is an example to type hello world in notepad. Pay close attention to the format.
    `run 'notepad.exe';win_wait_active '[CLASS:Notepad]' '3';control_send '[CLASS:Notepad]' '[CLASS:RichEditD2DPT]' 'hello world'`
    Now generate a command to '''

    prompt = preprompt + cmd_string

    chat = OpenAIChat()
    result = chat.start(prompt)
    chatResult = extract_code_block(str(result[0])).replace('python\n','').replace('\n','')
    print('Going to execute:')
    commands = chatResult.split(";")
    for cmd in commands:
        args = shlex.split(cmd)
        print(f'Command: {args[0]}, Arguments: {args[1:]}')
    confirmation = input("\nProceed? (y/n): ")
    if confirmation.lower() == "y":
        execute_commands(chatResult)
    else:
        print("Operation cancelled.")