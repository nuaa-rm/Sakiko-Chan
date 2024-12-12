# QQ机器人Saki

## 项目简介

本项目是一个基于腾讯官方平台的QQ机器人，通过与Notion数据库进行交互，管理用户日志和进度，并实现Shell命令执行功能。该机器人能够处理来自群聊的特定命令，提供相应的服务，如初始化用户信息、记录日志、更新进度、执行Shell命令等。

## 主要功能

1. **命令解析与处理**：机器人能够识别并处理多个自定义命令，包括：
   - `/init`: 初始化用户与QQ号的绑定。
   - `/log`: 记录用户的日志。
   - `/进度`: 更新用户的进度。
   - `/shell`: 执行Shell命令。

2. **与Notion的交互**：机器人能够与Notion数据库进行交互，进行以下操作：
   - 初始化QQ号与Notion成员数据库中的用户信息的绑定。
   - 创建日志和进度条目，并将其记录到Notion数据库。

3. **Shell命令执行**：机器人能够通过与持久化Shell子进程交互，执行系统命令并返回结果。

## 项目结构

### 1. `main.py`

该文件是项目的主要入口，包含了以下关键功能：

- **命令解析**：通过正则表达式解析群聊消息中的命令，并调用相应的功能模块。
- **命令处理**：根据命令类型（如初始化、日志记录、进度更新等），与Notion数据库进行交互。
- **Shell命令执行**：如果命令是`/shell`，则执行Shell命令，并返回执行结果。

#### 核心函数：
- `match_command(input_str)`: 使用正则表达式匹配输入字符串中的命令。
- `extract_numbers(input_string)`: 从输入字符串中提取数字（用于提取QQ号）。
- `process_command(message)`: 根据命令类型执行相应操作，包含初始化用户、记录日志、更新进度以及执行Shell命令。

### 2. `notion.py`

该文件封装了与Notion API的交互功能。通过`NotionApi`类和`CommandOperator`类，机器人可以从Notion数据库中获取、创建和更新页面。

#### 核心功能：
- `get_pages()`: 获取Notion数据库中的页面。
- `update_page(page_id, data)`: 更新指定页面的数据。
- `create_page(data)`: 创建新的页面。
- `get_entry_by_qq(qq_number)`: 根据QQ号获取Notion数据库中的用户条目。
- `create_notion_log(log_content, user_id, group_name)`: 创建日志条目。
- `create_notion_progress(progress_content, user_id, group_name)`: 创建进度条目。

### 3. `shell.py`

该文件包含了一个`PersistentShell`类，用于在后台运行并与Shell交互。此类可以执行任意Shell命令，并实时返回输出或错误信息。

#### 核心功能：
- `run_command(command)`: 执行Shell命令并返回执行结果。
- `close()`: 关闭与Shell进程的连接。

## 使用方法

1. **配置文件**：
   - 在`config.yaml`中配置Notion API的Token和数据库ID等信息。

2. **启动机器人**：
   - 运行`main.py`文件，机器人将自动连接QQ平台，并监听群聊消息。

3. **常用命令**：
   - `/init [QQ号]`: 初始化QQ号与Notion数据库中的用户信息绑定。
   - `/log [日志内容]`: 记录用户的日志。
   - `/进度 [进度内容]`: 更新用户的进度。
   - `/shell [命令]`: 执行Shell命令。

## 依赖

- `botpy`: QQ机器人框架。
- `requests`: 与Notion API交互。
- `fcntl` 和 `subprocess`: 用于创建和管理Shell进程。

