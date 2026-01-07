import sys
import subprocess
import os
import shutil
import requests
from scan import run_analize

def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        if response.status_code != 200:
            raise ConnectionError
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("ОШИБКА: Сервис Ollama не обнаружен!")
        sys.exit(1)

def main():
    args = sys.argv[1:]
    if "install" in args:
        packages1 = [a for a in args if not a.startswith("-") and a != "install"]
        if packages1:
            check_ollama()
            
            now_package = packages1[0]
            print(f"Проверка пакета '{now_package}'")
            
            sandbox_temp = os.path.abspath("sandbox")
            if os.path.exists(sandbox_temp):
                shutil.rmtree(sandbox_temp)
            os.makedirs(sandbox_temp)

            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "download", 
                    now_package, "--no-deps", "-d", sandbox_temp
                ])
                
                is_safe = run_analize(sandbox_temp)
                
                if is_safe:
                    print("Безопасно. Установка...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", 
                        "--no-index", f"--find-links={sandbox_temp}", now_package
                    ])
                else:
                    print("\nУСТАНОВКА ЗАБЛОКИРОВАНА! ИИ обнаружил угрозу.")
                    sys.exit(1)
            except Exception as error:
                print(f"Ошибка: {error}")
            finally:
                if os.path.exists(sandbox_temp):
                    try:
                        shutil.rmtree(sandbox_temp, ignore_errors=True)
                    except Exception as error:
                        print(f"Не удалось полностью очистить sandbox: {error}")
            return

    subprocess.check_call([sys.executable, "-m", "pip"] + args)

if __name__ == "__main__":
    main()
