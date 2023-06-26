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
Windows will reply back with the result of any commands that return a value and you can use that to decide what commands to generate next.
Output only the functions to run and nothing else. Don't set any variables. Don't comment anything.
Here is an example to type hello world in notepad.
`Run('notepad.exe')
WinWaitActive('[CLASS:Notepad]',3)
ControlSend('[CLASS:Notepad]','[CLASS:Edit1]','hello world')`
Now generate commands to'''

function_mapping = {
    "ControlClick": autoit.control_click,
    "ControlClickByHandle": autoit.control_click_by_handle,
    "ControlCommand": autoit.control_command,
    "ControlCommandByHandle": autoit.control_command_by_handle,
    "ControlListView": autoit.control_list_view,
    "ControlListViewByHandle": autoit.control_list_view_by_handle,
    "ControlDisable": autoit.control_disable,
    "ControlDisableByHandle": autoit.control_disable_by_handle,
    "ControlEnable": autoit.control_enable,
    "ControlEnableByHandle": autoit.control_enable_by_handle,
    "ControlFocus": autoit.control_focus,
    "ControlFocusByHandle": autoit.control_focus_by_handle,
    "ControlGetFocus": autoit.control_get_focus,
    "ControlGetFocusByHandle": autoit.control_get_focus_by_handle,
    "ControlGetHandle": autoit.control_get_handle,
    "ControlGetHandleAsText": autoit.control_get_handle_as_text,
    "ControlGetPos": autoit.control_get_pos,
    "ControlGetPosByHandle": autoit.control_get_pos_by_handle,
    "ControlGetText": autoit.control_get_text,
    "ControlGetTextByHandle": autoit.control_get_text_by_handle,
    "ControlHide": autoit.control_hide,
    "ControlHideByHandle": autoit.control_hide_by_handle,
    "ControlMove": autoit.control_move,
    "ControlMoveByHandle": autoit.control_move_by_handle,
    "ControlSend": autoit.control_send,
    "ControlSendByHandle": autoit.control_send_by_handle,
    "ControlSetText": autoit.control_set_text,
    "ControlSetTextByHandle": autoit.control_set_text_by_handle,
    "ControlShow": autoit.control_show,
    "ControlShowByHandle": autoit.control_show_by_handle,
    "ControlTreeView": autoit.control_tree_view,
    "ControlTreeViewByHandle": autoit.control_tree_view_by_handle,
    "StatusbarGetText": autoit.statusbar_get_text,
    "StatusbarGetTextByHandle": autoit.statusbar_get_text_by_handle,
    "ClipGet": autoit.clip_get,
    "ClipPut": autoit.clip_put,
    "IsAdmin": autoit.is_admin,
    "MouseClick": autoit.mouse_click,
    "MouseClickDrag": autoit.mouse_click_drag,
    "MouseDown": autoit.mouse_down,
    "MouseGetCursor": autoit.mouse_get_cursor,
    "MouseGetPos": autoit.mouse_get_pos,
    "MouseMove": autoit.mouse_move,
    "MouseUp": autoit.mouse_up,
    "MouseWheel": autoit.mouse_wheel,
    "Opt": autoit.opt,
    "PixelChecksum": autoit.pixel_checksum,
    "PixelGetColor": autoit.pixel_get_color,
    "PixelSearch": autoit.pixel_search,
    "Send": autoit.send,
    "KeyboardSend": autoit.send,
    "Tooltip": autoit.tooltip,
    "WinActivate": autoit.win_activate,
    "WinActivateByHandle": autoit.win_activate_by_handle,
    "WinActive": autoit.win_active,
    "WinActiveByHandle": autoit.win_active_by_handle,
    "WinClose": autoit.win_close,
    "WinCloseByHandle": autoit.win_close_by_handle,
    "WinExists": autoit.win_exists,
    "WinExistsByHandle": autoit.win_exists_by_handle,
    "WinGetCaretPos": autoit.win_get_caret_pos,
    "WinGetClassList": autoit.win_get_class_list,
    "WinGetClassListByHandle": autoit.win_get_class_list_by_handle,
    "WinGetClientSize": autoit.win_get_client_size,
    "WinGetClientSizeByHandle": autoit.win_get_client_size_by_handle,
    "WinGetHandle": autoit.win_get_handle,
    "WinGetHandleAsText": autoit.win_get_handle_as_text,
    "WinGetPos": autoit.win_get_pos,
    "WinGetPosByHandle": autoit.win_get_pos_by_handle,
    "WinGetProcess": autoit.win_get_process,
    "WinGetProcessByHandle": autoit.win_get_process_by_handle,
    "WinGetState": autoit.win_get_state,
    "WinGetStateByHandle": autoit.win_get_state_by_handle,
    "WinGetText": autoit.win_get_text,
    "WinGetTextByHandle": autoit.win_get_text_by_handle,
    "WinGetTitle": autoit.win_get_title,
    "WinGetTitleByHandle": autoit.win_get_title_by_handle,
    "WinKill": autoit.win_kill,
    "WinKillByHandle": autoit.win_kill_by_handle,
    "WinMenuSelectItem": autoit.win_menu_select_item,
    "WinMenuSelectItemByHandle": autoit.win_menu_select_item_by_handle,
    "WinMinimizeAll": autoit.win_minimize_all,
    "WinMinimizeAllUndo": autoit.win_minimize_all_undo,
    "WinMove": autoit.win_move,
    "WinMoveByHandle": autoit.win_move_by_handle,
    "WinSetOnTop": autoit.win_set_on_top,
    "WinSetOnTopByHandle": autoit.win_set_on_top_by_handle,
    "WinSetState": autoit.win_set_state,
    "WinSetStateByHandle": autoit.win_set_state_by_handle,
    "WinSetTitle": autoit.win_set_title,
    "WinSetTitleByHandle": autoit.win_set_title_by_handle,
    "WinSetTrans": autoit.win_set_trans,
    "WinSetTransByHandle": autoit.win_set_trans_by_handle,
    "WinWait": autoit.win_wait,
    "WinWaitByHandle": autoit.win_wait_by_handle,
    "WinWaitActive": autoit.win_wait_active,
    "WinWaitActiveByHandle": autoit.win_wait_active_by_handle,
    "WinWaitClose": autoit.win_wait_close,
    "WinWaitCloseByHandle": autoit.win_wait_close_by_handle,
    "WinWaitNotActive": autoit.win_wait_not_active,
    "WinWaitNotActiveByHandle": autoit.win_wait_not_active_by_handle,
    "Run": autoit.run,
    "AutoItSetOption": autoit.auto_it_set_option,
    "RunWait": autoit.run_wait,
    "ProcessClose": autoit.process_close,
    "ProcessExists": autoit.process_exists,
    "ProcessSetPriority": autoit.process_set_priority,
    "ProcessWait": autoit.process_wait,
    "ProcessWaitClose": autoit.process_wait_close,
    "RunAs": autoit.run_as,
    "RunAsWait": autoit.run_as_wait,
    "Shutdown": autoit.shutdown
}

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
    if(":" in arg):
        if arg.startswith("'\"") and arg.endswith("\"'"):
            arg = arg.replace("'\"", "'").replace("\"'", "'")
        if(os.path.exists(arg)):
            return arg
        elif("\\" in arg and not "\\\\" in arg):
            arg = arg.replace("\\", "/")
            if(os.path.exists(arg)):
                return arg
    return arg

def extract_file_path(cmd_string):
    args = re.findall(r'\((.*?)\)', cmd_string)
    if args:
        args = [arg.strip() for arg in args[0].split(',')]
        args = [correct_file_path(arg) for arg in args]
        return re.sub(r'\((.*?)\)', '(' + ', '.join(args) + ')', cmd_string)
    return args

def convert_function_call(cmd_string):
    cmd_string = extract_file_path(cmd_string)
    tree = ast.parse(cmd_string.strip())
    function_call = next(node for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call))
    function_name = function_call.value.func.id
    if function_name in function_mapping:
        func = function_mapping[function_name]
    if func:
        args = [ast.literal_eval(arg) for arg in function_call.value.args]
        if(len(args) > 2 and args[1] == ""):
            args.pop(1)
        try:
            funcResult = func(*args)
            return funcResult
        except Exception as e:
            errorMsg = "Call to " + function_name + " with arguments " + ",".join(args) + " returned error: " + str(e)
            print(errorMsg)
            return errorMsg
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