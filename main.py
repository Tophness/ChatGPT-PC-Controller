import autoit
import sys
import ast
from OpenAIAPIGrabber.chat import OpenAIChat
import re
import configparser

config_file = 'config.ini'
config = None
unattended = False
preprompt = '''You are directly controlling a windows PC using functions in the pyautoit library.
Windows will reply back with the result of any commands that return a value and you can use that to decide what commands to generate next.
Output only the functions to run and nothing else. Don't set any variables. Don't comment anything.
Here is an example to type hello world in notepad.
`run('notepad.exe')
win_wait_active('[CLASS:Notepad]',3)
control_send('[CLASS:Notepad]','[CLASS:Edit1]','hello world')`
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

def convert_function_call(cmd_string):
    tree = ast.parse(cmd_string.strip())
    function_call = next(node for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call))
    function_name = function_call.value.func.id
    func = getattr(autoit, function_name)
    if func:
        args = [ast.literal_eval(arg) for arg in function_call.value.args]
        return func(*args)
    else:
        raise ValueError("Invalid function name: " + function_name)

def remove_variable_assignment(text):
    if hasattr(text, '__len__') and (not isinstance(text, str)):
        return text
    pattern = r'([a-zA-Z_]\w*\([^)]*\))'
    lines = text.split("\n")
    functions = []

    for i in range(len(lines)):
        line = re.sub(r'^\s*[\w\d]+\s*=\s*', '', lines[i])
        match = re.search(pattern, line)
        if match:
            functions.append(match.group())

    return functions

def execute_commands(cmds_string):
    funcData = []
    commands = remove_variable_assignment(cmds_string)
    for cmd in commands:
        returnData = str(convert_function_call(cmd))
        if(returnData): funcData.append('Call to ' + cmd + ' returned: ' + returnData)
    if(len(funcData) > 0):
        return "\n".join(funcData) + "\nWhat command do you want to execute next?"
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
        chatResult = chatResult.replace('```python','```').replace('```plaintext','```')
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
            getCmd(chat, "what command do you want to execute next?", True)
        else:
            chat.deleteLast()

if __name__ == "__main__":
    load_config()
    try:
        cmd_string = sys.argv[1]
    except IndexError:
        cmd_string = input("Enter a task: ")
    getCmd(OpenAIChat(), cmd_string)