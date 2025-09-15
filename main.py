from dotenv import load_dotenv, find_dotenv

from root_page import RootPage

import flet as f


load_dotenv(find_dotenv())

def main(page: f.Page):
    page.title = "Анализ уровня заработной платы..."
    page.theme_mode = f.ThemeMode.LIGHT

    page.adaptive = True
    page.vertical_alignment = f.MainAxisAlignment.START
    page.horizontal_alignment = f.CrossAxisAlignment.CENTER

    page.window.width = 515
    page.window.height = 200

    root = RootPage()
    root.SetupUI()
    
    page.views.append(root)
    page.go("/")

fa_application = f.app(main, view=f.AppView.WEB_BROWSER)