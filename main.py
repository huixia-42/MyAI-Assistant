# main.py
import sys
import re
from llm_brain import ask_deepseek, client, history_messages, memory_file
from voice_engine import speak_bilingual
import agent_tools

# 保留防乱码设置
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')

def safe_print(text):
    try:
        sys.stdout.buffer.write((str(text) + "\n").encode('utf-8'))
        sys.stdout.flush()
    except Exception:
        pass

if __name__ == "__main__":
    safe_print("AI Assistant is running. Type 'quit' to exit.")
    safe_print("=" * 40)

    while True:
        try:
            user_input = input("You: ")
            
            # 1. 拦截退出
            if user_input.lower() in ["退出", "exit", "quit"]:
                if not history_messages:
                    safe_print("AI: Goodbye!")
                    break
                
                safe_print("[系统] 正在总结记忆并保存，请稍候...")
                # 借用 client 和 history_messages 进行总结
                summary_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        *history_messages,
                        {"role": "user", "content": "请用不超过50个字，提取以上对话中关于我的核心信息，直接输出总结内容，不要废话。如果无价值，输出'无新记忆'。"}
                    ]
                )
                new_memory = summary_response.choices[0].message.content
                
                if "无新记忆" not in new_memory:
                    with open(memory_file, "a", encoding="utf-8") as f:
                        f.write(new_memory + "\n")
                    safe_print(f"[系统] 记忆已写入硬盘：{new_memory}")
                
                safe_print("AI: Goodbye!")
                break

            # 2. 第一次思考
            reply = ask_deepseek(user_input)
            
            # 3. 拦截搜索指令
            search_match = re.search(r'\[CMD:SEARCH (.*?)\]', reply)
            if search_match:
                query = search_match.group(1)
                safe_print(f"[系统] 正在为你上网搜索：{query} ...")
                
                # 调用 agent_tools 里的搜索函数
                search_results = agent_tools.web_search(query)
                
                safe_print("[系统] 搜索完毕，正在让 AI 整理答案...")
                
                # 把搜索结果喂给 AI
                history_messages.append({"role": "user", "content": f"[系统通知：这是你刚才要求搜索的结果：\n{search_results}\n]"})
                
                # 第二次思考：严格约束格式
                strict_prompt = """请根据搜索结果，直接输出最终回答。
【极其重要：你必须严格遵守以下格式，绝不能遗漏任何标签！】
[EMO:61]
[ZH]这里写中文回答[/ZH]
[JP]ここに日本語の回答を書いてください[/JP]"""
                
                reply = ask_deepseek(strict_prompt)
                
                if "[ZH]" not in reply:
                    reply = f"[EMO:61]\n[ZH]{reply}[/ZH]\n[JP]すみません、検索結果の処理に失敗しました。[/JP]"

            # 4. 拦截工具指令
            if "[CMD:CALC]" in reply:
                agent_tools.open_calc()
                reply = reply.replace("[CMD:CALC]", "")
            elif "[CMD:NOTEPAD]" in reply:
                agent_tools.open_notepad()
                reply = reply.replace("[CMD:NOTEPAD]", "")

            # 5. 提取情绪与文本
            emo_match = re.search(r'\[EMO:(\d+)\]', reply)
            emotion_id = int(emo_match.group(1)) if emo_match else 61 
            
            zh_match = re.search(r'\[ZH\](.*?)\[/ZH\]', reply, re.DOTALL)
            zh_text = zh_match.group(1).strip() if zh_match else ""
            
            jp_match = re.search(r'\[JP\](.*?)\[/JP\]', reply, re.DOTALL)
            jp_text = jp_match.group(1).strip() if jp_match else ""
            
            # 打印干净文本
            safe_print(f"AI (中文): {zh_text}")
            safe_print(f"AI (日文): {jp_text}")
            
            # 6. 调用 voice_engine 发声
            speak_bilingual(reply, emotion_id) 
            
            safe_print("-" * 40)
            
        except Exception as e:
            # 用 repr(e) 把报错信息转成纯英文/数字，防止中文引发二次崩溃
            safe_print(f"[System Error] {repr(e)}")