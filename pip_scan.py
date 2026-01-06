import sys
import subprocess
import os
import shutil
from scan import run_analize

def main():
    args = sys.argv[1:]
    if "install" in args:
        packages1 = [a for a in args if not a.startswith("-") and a != "install"]
        if packages1:
            now_package = packages1[0]
            print(f"LLM-Scan: Проверка пакета '{now_package}'")
            
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
                    print("[*] Безопасно. Установка...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", 
                        "--no-index", f"--find-links={sandbox_temp}", now_package
                    ])
                else:
                    print("УСТАНОВКА ЗАБЛОКИРОВАНА.")
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