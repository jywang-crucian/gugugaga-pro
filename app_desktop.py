from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from chat_service import ask_deepseek
from storage import add_message, load_history, save_history


WELCOME_TEXT = "（摇摇晃晃地走过来）咕咕嘎嘎！\n\n我是小企鹅管理员，虽然不太会说话，但我会认真听你说哦~"


class ChatApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI Talk Desktop")
        self.root.geometry("780x580")

        self.messages: list[dict] = load_history()
        self._worker_error: str | None = None
        self._worker_reply: str | None = None
        if not self.messages:
            self.messages.append(add_message("assistant", WELCOME_TEXT))
            save_history(self.messages)

        self._build_ui()
        self._render_history()

    def _build_ui(self) -> None:
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
