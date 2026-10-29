# auto_chat.py
import time
import threading

class AutoChatEngine:
    def __init__(self, trigger_callback, idle_threshold=60):
        """
        trigger_callback: 当时间到了，要执行哪个函数（也就是让 AI 说话的函数）
        idle_threshold: 多少秒没说话算“发呆”
        """
        self.trigger_callback = trigger_callback
        self.idle_threshold = idle_threshold
        self.last_interaction_time = time.time()
        
        # 开关：默认关闭（工作时不打扰）
        self.is_enabled = False
        self.is_running = False

    def start(self):
        """开启自动聊天引擎"""
        self.is_enabled = True
        if not self.is_running:
            self.is_running = True
            # 开一个后台线程，专门跑计时器
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def stop(self):
        """关闭自动聊天引擎"""
        self.is_enabled = False

    def reset_timer(self):
        """只要用户手动发消息了，就重置计时器，AI不该打扰"""
        self.last_interaction_time = time.time()

    def _heartbeat_loop(self):
        """后台默默运转的心脏跳动"""
        while True:
            time.sleep(1) # 每秒跳一次
            # 如果开关开着，并且离上次互动超过了设定时间
            if self.is_enabled and (time.time() - self.last_interaction_time > self.idle_threshold):
                self.last_interaction_time = time.time() # 重置时间，防止连续触发
                self.trigger_callback() # 呼叫主程序：时间到了，该主动说话了！