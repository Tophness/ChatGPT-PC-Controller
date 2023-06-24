import autoit
import sys
import shlex
from OpenAIAPIGrabber.chat import OpenAIChat
import re
import configparser

config_file = 'config.ini'
config = None
unattended = False
preprompt = '''
You are directly controlling a windows PC using a python script that parses commands and runs them with autoit using the pyautoit library.
Output only the command to run (inside a code block) and nothing else. Commands are separated by colons, and arguments to those commands are separated by spaces. Argument strings must be encased in single quotes.
Here is an example to type hello world in notepad. Pay close attention to the format.
`run 'notepad.exe';win_wait_active '[CLASS:Notepad]' '3';control_send '[CLASS:Notepad]' '[CLASS:Edit1]' 'hello world'`
Now generate a command to '''

function_mapping = {
    "control_click": autoit.control_click,
    "control_click_by_handle": autoit.control_click_by_handle,
    "control_command": autoit.control_command,
    "control_command_by_handle": autoit.control_command_by_handle,
    "control_list_view": autoit.control_list_view,
    "control_list_view_by_handle": autoit.control_list_view_by_handle,
    "control_disable": autoit.control_disable,
    "control_disable_by_handle": autoit.control_disable_by_handle,
    "control_enable": autoit.control_enable,
    "control_enable_by_handle": autoit.control_enable_by_handle,
    "control_focus": autoit.control_focus,
    "control_focus_by_handle": autoit.control_focus_by_handle,
    "control_get_focus": autoit.control_get_focus,
    "control_get_focus_by_handle": autoit.control_get_focus_by_handle,
    "control_get_handle": autoit.control_get_handle,
    "control_get_handle_as_text": autoit.control_get_handle_as_text,
    "control_get_pos": autoit.control_get_pos,
    "control_get_pos_by_handle": autoit.control_get_pos_by_handle,
    "control_get_text": autoit.control_get_text,
    "control_get_text_by_handle": autoit.control_get_text_by_handle,
    "control_hide": autoit.control_hide,
    "control_hide_by_handle": autoit.control_hide_by_handle,
    "control_move": autoit.control_move,
    "control_move_by_handle": autoit.control_move_by_handle,
    "control_send": autoit.control_send,
    "control_send_by_handle": autoit.control_send_by_handle,
    "control_set_text": autoit.control_set_text,
    "control_set_text_by_handle": autoit.control_set_text_by_handle,
    "control_show": autoit.control_show,
    "control_show_by_handle": autoit.control_show_by_handle,
    "control_tree_view": autoit.control_tree_view,
    "control_tree_view_by_handle": autoit.control_tree_view_by_handle,
    "statusbar_get_text": autoit.statusbar_get_text,
    "statusbar_get_text_by_handle": autoit.statusbar_get_text_by_handle,
    "clip_get": autoit.clip_get,
    "clip_put": autoit.clip_put,
    "is_admin": autoit.is_admin,
    "mouse_click": autoit.mouse_click,
    "mouse_click_drag": autoit.mouse_click_drag,
    "mouse_down": autoit.mouse_down,
    "mouse_get_cursor": autoit.mouse_get_cursor,
    "mouse_get_pos": autoit.mouse_get_pos,
    "mouse_move": autoit.mouse_move,
    "mouse_up": autoit.mouse_up,
    "mouse_wheel": autoit.mouse_wheel,
    "opt": autoit.opt,
    "pixel_checksum": autoit.pixel_checksum,
    "pixel_get_color": autoit.pixel_get_color,
    "pixel_search": autoit.pixel_search,
    "send": autoit.send,
    "keyboard_send": autoit.send,
    "tooltip": autoit.tooltip,
    "win_activate": autoit.win_activate,
    "win_activate_by_handle": autoit.win_activate_by_handle,
    "win_active": autoit.win_active,
    "win_active_by_handle": autoit.win_active_by_handle,
    "win_close": autoit.win_close,
    "win_close_by_handle": autoit.win_close_by_handle,
    "win_exists": autoit.win_exists,
    "win_exists_by_handle": autoit.win_exists_by_handle,
    "win_get_caret_pos": autoit.win_get_caret_pos,
    "win_get_class_list": autoit.win_get_class_list,
    "win_get_class_list_by_handle": autoit.win_get_class_list_by_handle,
    "win_get_client_size": autoit.win_get_client_size,
    "win_get_client_size_by_handle": autoit.win_get_client_size_by_handle,
    "win_get_handle": autoit.win_get_handle,
    "win_get_handle_as_text": autoit.win_get_handle_as_text,
    "win_get_pos": autoit.win_get_pos,
    "win_get_pos_by_handle": autoit.win_get_pos_by_handle,
    "win_get_process": autoit.win_get_process,
    "win_get_process_by_handle": autoit.win_get_process_by_handle,
    "win_get_state": autoit.win_get_state,
    "win_get_state_by_handle": autoit.win_get_state_by_handle,
    "win_get_text": autoit.win_get_text,
    "win_get_text_by_handle": autoit.win_get_text_by_handle,
    "win_get_title": autoit.win_get_title,
    "win_get_title_by_handle": autoit.win_get_title_by_handle,
    "win_kill": autoit.win_kill,
    "win_kill_by_handle": autoit.win_kill_by_handle,
    "win_menu_select_item": autoit.win_menu_select_item,
    "win_menu_select_item_by_handle": autoit.win_menu_select_item_by_handle,
    "win_minimize_all": autoit.win_minimize_all,
    "win_minimize_all_undo": autoit.win_minimize_all_undo,
    "win_move": autoit.win_move,
    "win_move_by_handle": autoit.win_move_by_handle,
    "win_set_on_top": autoit.win_set_on_top,
    "win_set_on_top_by_handle": autoit.win_set_on_top_by_handle,
    "win_set_state": autoit.win_set_state,
    "win_set_state_by_handle": autoit.win_set_state_by_handle,
    "win_set_title": autoit.win_set_title,
    "win_set_title_by_handle": autoit.win_set_title_by_handle,
    "win_set_trans": autoit.win_set_trans,
    "win_set_trans_by_handle": autoit.win_set_trans_by_handle,
    "win_wait": autoit.win_wait,
    "win_wait_by_handle": autoit.win_wait_by_handle,
    "win_wait_active": autoit.win_wait_active,
    "win_wait_active_by_handle": autoit.win_wait_active_by_handle,
    "win_wait_close": autoit.win_wait_close,
    "win_wait_close_by_handle": autoit.win_wait_close_by_handle,
    "win_wait_not_active": autoit.win_wait_not_active,
    "win_wait_not_active_by_handle": autoit.win_wait_not_active_by_handle,
    "run": autoit.run,
    "auto_it_set_option": autoit.auto_it_set_option,
    "run_wait": autoit.run_wait,
    "process_close": autoit.process_close,
    "process_exists": autoit.process_exists,
    "process_set_priority": autoit.process_set_priority,
    "process_wait": autoit.process_wait,
    "process_wait_close": autoit.process_wait_close,
    "run_as": autoit.run_as,
    "run_as_wait": autoit.run_as_wait,
    "shutdown": autoit.shutdown
}

def convert_function_call(args):
    if args[0] in function_mapping:
        func = function_mapping[args[0]]
        converted_args = [int(arg) if isinstance(arg, str) and arg.isdigit() else arg for arg in args[1:]]
        return func(*converted_args)
    else:
        raise ValueError("Invalid function name: " + args[0])

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

def execute_commands(cmd_string):
    commands = cmd_string.split(";")
    funcData = []
    for cmd in commands:
        args = shlex.split(cmd)
        print(f'Command: {args[0]}, Arguments: {args[1:]}')
        returnData = convert_function_call(args)
        if(returnData): funcData.append(returnData)
    if(len(funcData) > 0):
        return "\n".join(funcData)
    else:
        return None

def isArray(N):
    if hasattr(N, '__len__') and (not isinstance(N, str)):
        return True
    else:
        return False

def getCmd(chat, prompt, reply=False):
    chatResult = None
    if(reply):
        chatResult = chat.replyLast(prompt)
    else:
        chatResult = chat.start(preprompt + prompt)
    if(chatResult):
        if(isArray(chatResult)):
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