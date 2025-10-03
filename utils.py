import os
import platform


def clear_console():
    # osの情報
    curernt_os = platform.system()
    if curernt_os == "Windows":
        os.system("cls") # Windows
    else:
        os.system("clear") # Mac Linux系


# 以下テスト

if __name__ == "__main__":
    print("テスト出力")
    print(platform.system())
    input("Enterを押すとクリアします...")
    clear_console()
