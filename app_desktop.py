from __future__ import annotations

import threading
import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, simpledialog

from chat_service import ask_deepseek
from config_store import get_saved_api_key, set_saved_api_key
from storage import add_message, load_history, save_history


WELCOME_TEXT = "（摇摇晃晃地走过来）咕咕嘎嘎！\n\n我是小企鹅管理员，虽然不太会说话，但我会认真听你说哦~"


class ChatApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI Talk Desktop")
        self.root.geometry("780x580")
        self._set_window_icon()

        self.messages: list[dict] = load_history()
        self._worker_error: str | None = None
        self._worker_reply: str | None = None
        if not self.messages:
            self.messages.append(add_message("assistant", WELCOME_TEXT))
            save_history(self.messages)

        self._build_ui()
        self._render_history()
        self.root.after(100, self._ensure_api_key_configured)

    def _set_window_icon(self) -> None:
        logo_path = Path("resources") / "logo.png"
        if not logo_path.exists():
            return
        try:
            self._logo_img = tk.PhotoImage(file=str(logo_path))
            self.root.iconphoto(True, self._logo_img)
        except Exception:
            # Ignore icon loading errors to keep app boot resilient.
            pass

    def _ensure_api_key_configured(self) -> None:
        has_env_key = bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())
        has_saved_key = bool(get_saved_api_key())
        if has_env_key or has_saved_key:
            return
        if messagebox.askyesno("首次配置", "未检测到 API Key。现在配置 DEEPSEEK_API_KEY 吗？"):
            self._open_api_key_dialog()

    def _build_ui(self) -> None:
        menu = tk.Menu(self.root)
        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="设置 API Key", command=self._open_api_key_dialog)
        menu.add_cascade(label="设置", menu=settings_menu)
        self.root.config(menu=menu)

        self.chat_box = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 11),
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_entry = tk.Entry(bottom, font=("Consolas", 11))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.input_entry.bind("<Return>", self._on_send)

        self.send_btn = tk.Button(bottom, text="发送", width=10, command=self._on_send)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.clear_btn = tk.Button(bottom, text="清空", width=10, command=self._clear_history)
        self.clear_btn.pack(side=tk.LEFT)

    def _open_api_key_dialog(self) -> None:
        current = get_saved_api_key()
        value = simpledialog.askstring(
            "设置 API Key",
            "请输入 DEEPSEEK_API_KEY：",
            initialvalue=current,
            show="*",
            parent=self.root,
        )
        if value is None:
            return
        value = value.strip()
        if not value:
            if messagebox.askyesno("清空配置", "输入为空，是否清空已保存的 API Key？"):
                set_saved_api_key("")
                messagebox.showinfo("已清空", "已清空本地保存的 API Key。")
            return
        set_saved_api_key(value)
        messagebox.showinfo("保存成功", "API Key 已保存到 resources/config.json")

    def _render_history(self) -> None:
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.delete("1.0", tk.END)
        for msg in self.messages:
            self._append_to_chat(msg["role"], msg["content"], msg.get("timestamp", ""))
        self.chat_box.configure(state=tk.DISABLED)
        self.chat_box.see(tk.END)

    def _append_to_chat(self, role: str, content: str, timestamp: str) -> None:
        speaker = "你" if role == "user" else "企鹅"
        self.chat_box.insert(tk.END, f"[{timestamp}] {speaker}:\n{content}\n\n")

    def _set_busy(self, is_busy: bool) -> None:
        state = tk.DISABLED if is_busy else tk.NORMAL
        self.send_btn.configure(state=state)
        self.input_entry.configure(state=state)
        self.clear_btn.configure(state=state)
        if not is_busy:
            self.input_entry.focus_set()

    def _on_send(self, event=None) -> None:
        text = self.input_entry.get().strip()
        if not text:
            return

        user_msg = add_message("user", text)
        self.messages.append(user_msg)
        save_history(self.messages)

        self.chat_box.configure(state=tk.NORMAL)
        self._append_to_chat("user", text, user_msg["timestamp"])
        self.chat_box.configure(state=tk.DISABLED)
        self.chat_box.see(tk.END)
        self.input_entry.delete(0, tk.END)

        self._set_busy(True)
        worker = threading.Thread(target=self._request_ai_reply_worker, daemon=True)
        worker.start()
        self.root.after(100, self._poll_worker_result)

    def _request_ai_reply_worker(self) -> None:
        try:
            reply = ask_deepseek(self.messages)
            if not reply:
                reply = "（歪头）嘎？"
            self._worker_reply = reply
            self._worker_error = None
            return
        except ValueError as exc:
            self._worker_reply = None
            self._worker_error = str(exc)
            return
        except Exception as exc:
            self._worker_reply = None
            self._worker_error = f"调用模型失败：{exc}"
            return

    def _poll_worker_result(self) -> None:
        if self._worker_reply is None and self._worker_error is None:
            self.root.after(100, self._poll_worker_result)
            return

        if self._worker_error is not None:
            title = "配置错误" if "DEEPSEEK_API_KEY" in self._worker_error else "请求失败"
            messagebox.showerror(title, self._worker_error)
            self._worker_error = None
            self._set_busy(False)
            return

        reply = self._worker_reply or "（歪头）嘎？"
        self._worker_reply = None
        assistant_msg = add_message("assistant", reply)
        self.messages.append(assistant_msg)
        save_history(self.messages)

        self.chat_box.configure(state=tk.NORMAL)
        self._append_to_chat("assistant", reply, assistant_msg["timestamp"])
        self.chat_box.configure(state=tk.DISABLED)
        self.chat_box.see(tk.END)
        self._set_busy(False)

    def _clear_history(self) -> None:
        if not messagebox.askyesno("确认", "确定要清空聊天记录吗？"):
            return
        self.messages = [add_message("assistant", WELCOME_TEXT)]
        save_history(self.messages)
        self._render_history()


def main() -> None:
    root = tk.Tk()
    app = ChatApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
