# app_ui.py
import os
from PIL import Image
import customtkinter as ctk
import threading
import re
import time
from llm_brain import ask_deepseek
from voice_engine import speak_bilingual
from auto_chat import AutoChatEngine

# 1. 设置 UI 的基础风格（黑底蓝调）
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 2. 定义窗口类（模具）
class AIChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aive")
        self.geometry("700x800")

        # 初始化自动聊天引擎
        self.auto_chat = AutoChatEngine(trigger_callback=self.ai_speak_proactively, idle_threshold=120)

        # ============ 新增：加载背景图 ============
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "bg.png")
        
        print(f"[调试信息] 程序正在这个路径下寻找背景图: {bg_path}")
        
        if os.path.exists(bg_path):
            print("[调试信息] 找到图片了！正在加载...")
            bg_image = ctk.CTkImage(Image.open(bg_path), size=(700, 800))
            self.bg_label = ctk.CTkLabel(self, image=bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            print("[警告] 没找到 bg.png！请检查图片名字是否正确，或者它是不是真的在这个文件夹里。")
        # =========================================
        # =========================================

        # 聊天记录显示区（设置 fg_color="transparent" 让背景透明）
        # 稍微减小了高度，给底部的输入框留出空间
                # 聊天记录显示区（改成深灰色背景，加一点边框）
        self.chat_box = ctk.CTkTextbox(self, width=650, height=560, font=("Consolas", 14), 
                                       fg_color="#121212", text_color="white", 
                                       border_width=1, border_color="#333333")
        self.chat_box.pack(pady=(20, 10), padx=20)
        self.chat_box.configure(state="disabled") 

        # 顶部控制区框架
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20)

        self.auto_chat_switch = ctk.CTkSwitch(self.top_frame, text="开启自动聊天(工作勿扰)", command=self.toggle_auto_chat)
        self.auto_chat_switch.pack(side="left")

        # 底部输入区框架
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=(10, 20))

        # 输入框和按钮
                # 输入框和按钮
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="输入你想说的话...",
                                  fg_color="#121212", border_color="#333333", text_color="white")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def append_text(self, text):
        """向屏幕追加文字的小工具"""
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text + "\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def toggle_auto_chat(self):
        """当用户点击开关时触发"""
        if self.auto_chat_switch.get() == 1:
            self.auto_chat.start()
            self.append_text("[系统] 自动聊天已开启，AI 可能会主动找你搭话。")
        else:
            self.auto_chat.stop()
            self.append_text("[系统] 自动聊天已关闭。")

    def handle_send(self):
        """用户手动点击发送按钮或按回车时触发"""
        user_input = self.entry.get().strip()
        if not user_input:
            return
        
        self.entry.delete(0, "end")
        self.append_text(f"👤 你: {user_input}")
        
        # 告诉自动聊天引擎：用户刚刚说话了，重新开始计时
        self.auto_chat.reset_timer()
        
        # 开一个后台线程去请求 AI（防止界面卡死）
        threading.Thread(target=self.request_ai_response, args=(user_input,)).start()

    def request_ai_response(self, prompt):
        """后台请求 AI 的逻辑"""
        self.send_btn.configure(state="disabled", text="思考中...")
        try:
            reply = ask_deepseek(prompt)
            
            # 使用正则提取情绪和中日双语
            emo_match = re.search(r'\[EMO:(\d+)\]', reply)
            emotion_id = int(emo_match.group(1)) if emo_match else 61 
            
            zh_match = re.search(r'\[ZH\](.*?)\[/ZH\]', reply, re.DOTALL)
            zh_text = zh_match.group(1).strip() if zh_match else ""
            
            jp_match = re.search(r'\[JP\](.*?)\[/JP\]', reply, re.DOTALL)
            jp_text = jp_match.group(1).strip() if jp_match else ""

            self.append_text(f"🤖 AI (中文): {zh_text}\n🤖 AI (日文): {jp_text}")
            
            # 调用发声引擎
            speak_bilingual(reply, emotion_id)
            
        except Exception as e:
            self.append_text(f"❌ [系统错误] {e}")
        finally:
            self.send_btn.configure(state="normal", text="发送")
            self.auto_chat.reset_timer() # AI 说完了，重新开始计时

    def ai_speak_proactively(self):
        """当计时器到了，自动聊天引擎会调用这个函数"""
        self.append_text(f"[系统] AI 觉得你太久没理她了，正在主动思考...")
        hidden_prompt = f"[系统：现在时间是 {time.strftime('%H:%M')}。用户已经很久没动静了。请你根据你的性格，主动找个简短的话题跟用户搭话，不要长篇大论。]"
        threading.Thread(target=self.request_ai_response, args=(hidden_prompt,)).start()

# 3. 程序入口
if __name__ == "__main__":
    app = AIChatApp()
    app.mainloop()