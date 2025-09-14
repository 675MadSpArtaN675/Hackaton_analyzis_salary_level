from dotenv import load_dotenv, find_dotenv

from pages.root_page import RootPage

import flet as f


load_dotenv(find_dotenv())

def main(page: f.Page):
    root = RootPage(page=page)
    root.SetupUI()
    
    page.views.append(root)

fa_application = f.app(main, view=f.AppView.WEB_BROWSER)