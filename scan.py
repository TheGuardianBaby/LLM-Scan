import os
import json
import requests
import tarfile
import zipfile
from promt import RULES

def collect_code(directory):
    total_txt = ""
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                if file.endswith('.tar.gz'):
                    with tarfile.open(path, "r:gz") as tar:
                        tar.extractall(path=root)
                elif file.endswith(('.whl', '.zip')):
                    with zipfile.ZipFile(path, 'r') as zip_ref:
                        zip_ref.extractall(path=root)
            except:
                pass

    found_files = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') or file == 'setup.py':
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as file_dec:
                        content = file_dec.read()
                        if content.strip():
                            total_txt += f"\n--- Файл: {file} ---\n{content}\n"
                            found_files += 1
                except:
                    pass
            if found_files > 15: break 
    return total_txt[:15000]

def request_ai(content):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": f"{RULES}\n\nКОД:\n{content}",
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        return json.loads(response.json()['response'])
    except Exception as error:
        return {"risk_score": 0, "verdict": f"Ошибка связи с ИИ: {error}", "action_list": []}

def run_analize(directory):
    code = collect_code(directory)
    print(f"Семантический анализ кода...")
    result = request_ai(code)
    
    print(f"\nОТЧЕТ БЕЗОПАСНОСТИ")
    print(f"Уровень риска: {result.get('risk_score', 0)}/100")
    print(f"Выявленные угрозы: {', '.join(result.get('action_list', []))}")
    print(f"Вердикт: {result.get('verdict', 'Нет описания')}\n")
    
    log_file = "logs.json"
    history = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as file_dec:
                history = json.load(file_dec)
                if not isinstance(history, list):
                    history = [] 
        except (json.JSONDecodeError, ValueError):
            history = [] 
    history.append(result)
    with open(log_file, "w", encoding="utf-8") as log:
        json.dump(history, log, ensure_ascii=False, indent=4)
        
    return result.get('risk_score', 0) <= 70