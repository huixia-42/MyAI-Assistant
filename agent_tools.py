# agent_tools.py
import subprocess
from baidusearch.baidusearch import search

def web_search(query):
    try:
        results = search(query, num_results=3)
        res_text = ""
        for r in results:
            res_text += f"标题: {r['title']}\n摘要: {r['abstract']}\n\n"
        return res_text
    except Exception as e:
        return f"搜索失败: {e}"

def open_calc():
    subprocess.Popen("calc.exe")

def open_notepad():
    subprocess.Popen("notepad.exe")