# GuGuGaGa Pro

基于 DeepSeek 的 Windows 桌面聊天应用（`tkinter`），不依赖 Streamlit。

## 最新版本

- 新增 API Key 图形化配置（首次启动引导 + 设置菜单修改）
- 新增图标构建链路（`resources/logo.png` -> `resources/app.ico`）
- 打包脚本和安装脚本支持自定义应用图标
- 聊天请求改为后台线程，避免 UI 卡顿

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

## 发布流程

每次发版建议按下面顺序执行：

1. 更新代码与文档
   - 确认功能修改完成
   - 更新 `README.md`（功能变更、使用说明、兼容性）
2. 本地验证
   - 运行 `python app_desktop.py`
   - 验证：发送消息、清空记录、API Key 配置弹窗、重启后记录恢复
3. 构建可执行文件
   - 执行 `build.bat`
   - 检查产物：`dist/AI-Talk-Desktop.exe`
4. 构建安装包
   - 使用 Inno Setup 编译 `installer.iss`
   - 检查产物：`installer-output/AI-Talk-Desktop-Setup.exe`
5. 安装包验收
   - 在干净环境安装并启动
   - 验证桌面快捷方式、程序启动、聊天功能正常
6. 提交与推送
   - 提交源码（不要提交 `dist/`、`build/`、`installer-output/`）
   - 推送到 `main`
7. 发布记录（可选）
   - 在 GitHub Releases 填写版本说明
   - 附上安装包下载地址和变更摘要

## 常见问题

- `No module named openai`：执行 `python -m pip install -r requirements.txt`
- 启动后无法回复：检查 `DEEPSEEK_API_KEY` 是否生效
- 聊天记录异常：删除 `resources/chat_history.json` 后重启
- 需要更换应用图标：替换 `resources/logo.png` 后重新执行 `build.bat`
- `resources/app.ico` 为自动生成文件，如缺失可直接重新运行 `build.bat`
