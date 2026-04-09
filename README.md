# GuGuGaGa Pro

基于 DeepSeek 的 Windows 桌面聊天应用（`tkinter`），不依赖 Streamlit。

## 功能

- 桌面聊天窗口（输入、发送、清空）
- 小企鹅角色系统提示词
- 本地聊天记录持久化（`resources/chat_history.json`）
- API Key 图形化配置（保存到 `resources/config.json`）
- 一键打包 EXE（`build.bat`）
- Inno Setup 安装包脚本（`installer.iss`）

## 项目结构

```text
.
├── app_desktop.py      # 桌面 UI 入口
├── chat_service.py     # DeepSeek API 调用
├── storage.py          # 消息读写与本地持久化
├── config_store.py     # API Key 本地配置读写
├── make_icon.py        # 将 logo.png 转换为 app.ico
├── start.bat           # 本地运行脚本
├── build.bat           # 打包 EXE 脚本
├── installer.iss       # Inno Setup 安装脚本
├── requirements.txt
└── resources/
```

## 环境要求

- Python 3.10+
- 环境变量 `DEEPSEEK_API_KEY`

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 本地运行

命令行：

```powershell
python app_desktop.py
```

Windows 双击：

- 直接运行 `start.bat`

首次启动若未配置 API Key，会弹窗引导你填写并保存到本地配置。

你也可以手动设置环境变量（优先级更高）：

```powershell
setx DEEPSEEK_API_KEY "your_api_key"
```

然后重新打开终端/IDE 再运行。

## 打包 EXE

一键打包：

```bat
build.bat
```

输出文件：

- `dist/AI-Talk-Desktop.exe`
- 若存在 `resources/logo.png`，打包时会自动生成 `resources/app.ico` 并作为应用图标

## 制作安装包

1. 安装 [Inno Setup](https://jrsoftware.org/isinfo.php)
2. 先执行 `build.bat`
3. 用 Inno Setup 打开 `installer.iss`
4. 点击 Compile，得到：
   - `installer-output/AI-Talk-Desktop-Setup.exe`

## 常见问题

- `No module named openai`：执行 `python -m pip install -r requirements.txt`
- 启动后无法回复：检查 `DEEPSEEK_API_KEY` 是否生效
- 聊天记录异常：删除 `resources/chat_history.json` 后重启
- 需要更换应用图标：替换 `resources/logo.png` 后重新执行 `build.bat`
