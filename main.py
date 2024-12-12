# -*- coding: utf-8 -*-
import os
import re
from enum import Enum

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage

import notion
from shell import PersistentShell


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
NOTION_TOKEN = test_config["NOTION_TOKEN"]
MEMBER_DATABASE_ID = test_config["MEMBER_DATABASE_ID"]
LOG_DATABASE_ID = test_config["LOG_DATABASE_ID"]
PROGRESS_DATABASE_ID = test_config["PROGRESS_DATABASE_ID"]
_log = logging.get_logger()
persistent_shell = None


class CommandType(Enum):
    LOG = "/log"
    PROGRESS = "/进度"
    INIT = "/init"
    SHELL = "/shell"


def match_command(input_str):
    pattern = "|".join([re.escape(command.value) for command in CommandType])
    match = re.search(pattern, input_str)
    if match:
        matched_command = match.group(0)
        for command in CommandType:
            if command.value == matched_command:
                remaining_str = input_str[match.end():].strip()
                return {matched_command: remaining_str}
    return None

def extract_numbers(input_string):
    return ''.join(re.findall(r'\d', input_string))

def sanitize_message_content(content):
    """
    格式化消息内容，避免触发 URL 检测。
    """
    sanitized = content.replace(".", "[dot]")  # 将点替换为 [dot]
    return sanitized


def process_command(message):
    global persistent_shell
    command_operator = notion.CommandOperator(NOTION_TOKEN, MEMBER_DATABASE_ID, LOG_DATABASE_ID, PROGRESS_DATABASE_ID)
    result = match_command(message.content)

    if result:
        command = list(result.keys())[0]  # 获取匹配到的命令
        remaining_str = result[command]  # 获取剩余的字符串

        if command == CommandType.INIT.value:
            qq_number = extract_numbers(remaining_str)
            res = command_operator.init_qq_id_pair(qq_number, message.author.member_openid)
            return "status_code:" + str(res.status_code)
        elif command == CommandType.LOG.value:
            user_info = command_operator.get_entry_by_member_openid(message.author.member_openid)
            if not user_info:
                return "User not found, please try /init"
            notion_userid = user_info['created_by']['id']
            group_name = user_info['properties']['组别']['select']['name']
            _log.info(f"Creating Notion page with log content: {remaining_str}")
            res = command_operator.create_notion_log(remaining_str, notion_userid, group_name)
            return "status_code:" + str(res.status_code)
        elif command == CommandType.PROGRESS.value:
            user_info = command_operator.get_entry_by_member_openid(message.author.member_openid)
            if not user_info:
                return "User not found, please try /init"
            notion_userid = user_info['created_by']['id']
            group_name = user_info['properties']['组别']['select']['name']
            _log.info(f"Creating Notion page with Progress content: {remaining_str}")
            res = command_operator.create_notion_progress(remaining_str, notion_userid, group_name)
            return "status_code:" + str(res.status_code)
        elif command == CommandType.SHELL.value:
            if remaining_str.isspace() or not remaining_str:
                # 创建或重置 PersistentShell 实例
                if persistent_shell is not None:
                    _log.info("Restarting PersistentShell instance.")
                    persistent_shell.close()
                persistent_shell = PersistentShell()
                return "Shell started or restarted."
            else:
                if persistent_shell is None:
                    return "Shell not initialized. Use `/shell` to start it."
                _log.info(f"Executing shell command: {remaining_str}")
                res = persistent_shell.run_command(remaining_str)
                _log.info(f"Shell command result: {res}")
                return sanitize_message_content(res) if res else " "
        else:
            _log.info(f"其他命令: {command}，内容: {remaining_str}")
            return "Invalid command"
    else:
        _log.info("没有匹配到任何命令")
        return "Invalid command"




class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
    async def on_group_at_message_create(self, message: GroupMessage):
        try:
            res = process_command(message)
            message_result = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"{res}")
        except Exception as e:
            _log.info(f"Error processing command: {e}")
            message_result = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"{e}")
        _log.info(message_result)



if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])