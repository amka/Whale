# coding: utf-8
from sys import platform


if __name__ == '__main__':

    if platform == 'darwin':
        from app_osx import App
    elif platform == 'win32':
        from app_win import App

    whale_app = App()
    whale_app.run()
