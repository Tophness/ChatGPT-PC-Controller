import autoit
import sys
import shlex
from OpenAIAPIGrabber.chat import OpenAIChat
import re
import configparser

config_file = 'config.ini'
config = None
unattended = False
preprompt = '''You are directly controlling a windows PC using a python script that parses commands and runs them with autoit using the pyautoit library. Windows will reply back with the result of any commands that return a value (like control_get_text), and you can use that to decide what commands to generate next.
Output only the commands to run (inside a code block) and nothing else. Commands are separated by colons, and arguments to those commands are separated by spaces. Argument strings must be encased in single quotes.
Here is an example to type hello world in notepad. Pay close attention to the format.
`run 'notepad.exe';win_wait_active '[CLASS:Notepad]' 3;control_send '[CLASS:Notepad]' '[CLASS:Edit1]' 'hello world'`
Now generate commands to '''

def load_config():
    global config
    config = configparser.ConfigParser()
    config.read(config_file)
    controller_section = None
    if('Controller' in config):
        controller_section = config['Controller']
    else:
        save_config()
        controller_section = config['Controller']
    if(controller_section):
        global unattended, preprompt
        unattended = controller_section.getboolean('Unattended')
        preprompt = controller_section.get('Preprompt')

def save_config():
    global config
    config['Controller'] = {
        'Unattended': unattended,
        'Preprompt': preprompt
    }
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def extract_code_block(code_string):
    code_block_regex = "```([\w\W]*?)```" if code_string.count("`") == 6 else "`([\w\W]*?)`"
    match = re.search(code_block_regex, code_string)
    if match:
        return match.group(1).strip()
    return code_string

def convert_function_call(args):
    func = getattr(autoit, args[0])
    if func:
        converted_args = [int(arg) if isinstance(arg, str) and arg.isdigit() else arg for arg in args[1:]]
        return func(*converted_args)
    else:
        raise ValueError("Invalid function name: " + args[0])

def execute_commands(cmd_string):
    commands = cmd_string.split(";")
    funcData = []
    for cmd in commands:
        args = shlex.split(cmd)
        print(f'Command: {args[0]}, Arguments: {args[1:]}')
        returnData = str(convert_function_call(args))
        if(returnData): funcData.append(returnData)
    if(len(funcData) > 0):
        return "\n".join(funcData)
    else:
        return None

def getCmd(chat, prompt, reply=False):
    chatResult = None
    if(reply):
        chatResult = chat.replyLast(prompt)
    else:
        chatResult = chat.start(preprompt + prompt)
    if(chatResult):
        if hasattr(chatResult, '__len__') and (not isinstance(chatResult, str)):
            chatResult = str(chatResult[0])
        chatResult = extract_code_block(chatResult).replace('python\n','').replace('\n','').replace('plaintext\n','')
        if (not unattended):
            print('Going to execute:')
            commands = chatResult.split(";")
            for cmd in commands:
                args = shlex.split(cmd)
                print(f'Command: {args[0]}, Arguments: {args[1:]}')
            confirmation = input("\nProceed? (y/n): ")
            if confirmation.lower() != "y":
                print("Operation cancelled.")
                return
        cmdResult = execute_commands(chatResult)
        if(cmdResult):
            getCmd(chat, cmdResult, True)
        elif(unattended):
            getCmd(chat, "what command do you want to execute next?", True)

if __name__ == "__main__":
    load_config()
    try:
        cmd_string = sys.argv[1]
    except IndexError:
        cmd_string = input("Enter a task: ")
    getCmd(OpenAIChat(), cmd_string)