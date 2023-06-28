import autoit
import sys
import ast
from OpenAIAPIGrabber.chat import OpenAIChat
import re
import configparser
import os

config_file = 'config.ini'
config = None
unattended = False
preprompt = '''You are directly controlling a windows PC using autoit functions.
I will reply back with the result of any commands that return a value and you can use that to decide what commands to generate next.
Output only the functions to run and nothing else. Don't set any variables. Don't use window handles. Don't comment anything.
Here is an example to type hello world in notepad.
`Run('notepad.exe')
WinWaitActive('[CLASS:Notepad]','',3)
ControlSend('[CLASS:Notepad]','','[CLASS:Edit1]','hello world')`
Now generate commands to'''

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

def extract_code_blocks(code_string):
    code_block_regex = r"```([\w\W]*?)```" if code_string.count("`") == 6 else r"`([\w\W]*?)`"
    matches = re.findall(code_block_regex, code_string)
    functions = []
    
    for match in matches:
        match = match.strip()
        if '(' in match and ')' in match:
            functions.append(match)
    if(len(functions) > 0):
        return functions
    else:
        return code_string

def correct_file_path(arg):
    if(not isinstance(arg, str)):
        return arg
    if arg.startswith("'\"") and arg.endswith("\"'"):
        arg = arg.replace("'\"", "'").replace("\"'", "'")
    if arg.startswith('"'):
        arg = arg.replace('"', "'")
    if arg.endswith('"'):
        arg = arg.replace('"', "'")
    drive, path = os.path.splitdrive(arg.replace("'","").replace('"',""))
    if(drive):
        if(os.path.exists(arg)):
            return arg
        elif("\\" in arg and not "\\\\" in arg):
            arg = arg.replace("\\", "/")
            if(os.path.exists(arg)):
                return arg
    return arg

def extract_file_path(cmd_string):
    cmds = re.findall(r'\((.*?)\)', cmd_string)
    argsnew = []
    for args in cmds:
        arg_list = [correct_file_path(arg.strip()) for arg in args.split(',')]
        argsnew.append('(' + ', '.join(arg_list) + ')')
    cmd_string_new = re.sub(r'\((.*?)\)', lambda x: argsnew.pop(0), cmd_string)
    return cmd_string_new

def convert_function_call(cmd_string):
    cmd_string = extract_file_path(cmd_string)
    tree = ast.parse(cmd_string.strip())
    function_call = next(node for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call))
    function_name = function_call.value.func.id
    func = getattr(autoit, function_name)
    if func:
        args = [ast.literal_eval(arg) for arg in function_call.value.args]
        try:
            funcResult = func(*args)
            return funcResult
        except Exception as e:
            errorMsg = "Call to " + function_name + " with arguments " + ",".join(str(x) for x in args) + " returned error: " + str(e)
            print(errorMsg)
            return errorMsg
    else:
        raise ValueError("Invalid function name: " + function_name)

def remove_variable_assignment(text):
    if hasattr(text, '__len__') and (not isinstance(text, str)):
        text = "\n".join(text)
    lines = text.split("\n")
    functions = []
    for line in lines:
        match = re.search(r'(\b\w+\(.*?\))', line)
        if match:
            functions.append(match.group(1).strip())
        else:
            functions.append(line)
    return functions

def execute_commands(cmds_string):
    funcData = []
    commands = remove_variable_assignment(cmds_string)
    for cmd in commands:
        returnData = str(convert_function_call(cmd))
        if(returnData): funcData.append('Call to ' + cmd + ' returned: ' + returnData)
    if(len(funcData) > 0):
        return "\n".join(funcData) + "\nWhat function do you want to execute next?"
    else:
        return None

def getCmd(chat, prompt, reply=False):
    chatResult = None
    if(reply):
        chatResult = chat.replyLast(prompt)
    else:
        chatResult = chat.start(preprompt + " " + prompt)
    if(chatResult):
        if hasattr(chatResult, '__len__') and (not isinstance(chatResult, str)):
            chatResult = str(chatResult[0])
        chatResult = chatResult.replace('```python','```').replace('```autoit','```').replace('```plaintext','```')
        chatResult = extract_code_blocks(chatResult)
        if (not unattended):
            print('Going to execute:')
            commands = remove_variable_assignment(chatResult)
            for cmd in commands:
                print(cmd)
            confirmation = input("\nProceed? (y/n): ")
            if confirmation.lower() != "y":
                chat.deleteLast()
                print("Operation cancelled.")
                return
        cmdResult = execute_commands(chatResult)
        if(cmdResult):
            getCmd(chat, cmdResult, True)
        elif(unattended):
            getCmd(chat, "what function do you want to execute next?", True)
        else:
            chat.deleteLast()

if __name__ == "__main__":
    load_config()
    try:
        cmd_string = sys.argv[1]
    except IndexError:
        cmd_string = input("Enter a task: ")
    getCmd(OpenAIChat(), cmd_string)