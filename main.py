from dotenv import load_dotenv, find_dotenv

from root_page import START_MESSAGE
from root_page import RootPage
from analyzis_module import SalaryAnalyzer

import flet as f
import os

load_dotenv(find_dotenv())

sa = SalaryAnalyzer(os.getenv("LINK_TO_STATISTIC"), 
                        START_MESSAGE, 
                        os.getenv("GIGACHAT_TOKEN"))

filename = sa.DownloadFilesFromWebSite()

def main(page: f.Page):
    page.title = "Анализ уровня заработной платы"
    page.theme_mode = f.ThemeMode.LIGHT

    page.adaptive = True
    page.vertical_alignment = f.MainAxisAlignment.START
    page.horizontal_alignment = f.CrossAxisAlignment.CENTER

    page.window.width = 900
    page.window.height = 600

    root = RootPage()
    root.SetupUI(sa, filename)
    
    page.views.append(root)
    page.update()

fa_application = f.app(main, view=f.AppView.WEB_BROWSER)