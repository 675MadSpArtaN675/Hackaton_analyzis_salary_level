from typing import Sequence, Callable, Any

import flet as f
import pandas as pd

class RootPage(f.View):
    __situation_func: Callable = None

    def __init__(self, controls: Sequence[f.Control] = ()):
        super().__init__("/", controls=controls)

    def SetSituationButtonFunc(self, func: Callable[[f.ControlEvent], Any]):
        self.__situation_func = func

    def SetupUI(self):
        self.__text_link_entry = f.TextField(label="Ссылка на базу статистики")
        self.__situation_button = f.Button(text="Получить данные...", on_click=self.__situation_button)

        text_entry_container = f.Container(self.__text_link_entry, alignment=f.alignment.top_center)
        base_interface = f.Row(controls=[
            f.Column(
                controls=[
                    text_entry_container,
                    self.__situation_button
                ]
            )
        ], alignment=f.MainAxisAlignment.CENTER, expand=True)

        self.controls.append(base_interface)

    def ViewDatatableWithData(self, data: pd.DataFrame, city: str):
        column_indexes = data.columns.copy()
        column_indexes.insert(0, "")

        city_data = data[city].to_list()
        city_data.insert(0, city)

        return f.DataTable(columns=column_indexes, rows=city_data)

if __name__ == "__main__":
    def main(page: f.Page):
        page.title = "Анализ уровня заработной платы"
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

    f.app(main)