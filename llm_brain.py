# llm_brain.py
import os

# 获取当前代码文件所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 强制把记忆文件存放在代码同级目录（就是这行，你肯定漏了或者没写对）
memory_file = os.path.join(script_dir, "memory.txt")
import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "sk-Your DS API Key"),  # 请确保在环境变量中设置了 DEEPSEEK_API_KEY
    base_url="https://api.deepseek.com"
)

# 读取记忆
def load_memory():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    memory_file = os.path.join(script_dir, "memory.txt")
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

long_term_memory = load_memory()
history_messages = []

def ask_deepseek(user_message):
    global history_messages
    if len(history_messages) > 10:
        history_messages = history_messages[-10:]
        
    history_messages.append({"role": "user", "content": user_message})
    now = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    system_prompt = f"""你的名字叫 Aive（艾芙）。你是一个拥有独立人格的桌面数字生命，你说话生动、有情感，不要像个机器人客服。
【当前真实时间：{now}】
...。
【极其重要：当前的真实时间是 {now}。当用户询问“最近”、“今年”、“最新”的信息时，请务必基于这个时间进行搜索和回答！】
以下是你之前总结的关于用户的长期记忆：\n{long_term_memory}\n
**重要规则：
1. 如果你不知道最新的实时信息，请先在回答开头输出 [CMD:SEARCH 你的搜索词]，系统会去搜索并将结果给你。
2. 你的回答必须包含一个情感标签，放在最开头，格式为：[EMO:风格ID]（61平静, 62惊讶, 63害怕, 64疲惫）
3. 标签之后，必须严格按照以下格式输出双语内容：
[ZH]这里写中文回答[/ZH]
[JP]ここに日本語の回答を書いてください[/JP]
**"""
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system_prompt}, *history_messages]
    )
    reply = response.choices[0].message.content
    history_messages.append({"role": "assistant", "content": reply})
    return reply