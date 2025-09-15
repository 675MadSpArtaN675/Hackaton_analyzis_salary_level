from typing import Sequence
from gigachat_service import ANALYZE_MESSAGE, START_MESSAGE
from dotenv import load_dotenv, find_dotenv

from analyzis_module import SalaryAnalyzer

import os

import flet as f
import pandas as pd


class RootPage(f.View):
    __ready: bool = False

    def __init__(self, controls: Sequence[f.Control] = ()):
        super().__init__("/", controls=controls)

    def GetCitiesOptions(self, data: pd.DataFrame):
        cities = data.index

        options = []
        for city in cities:
            options.append(f.DropdownOption(key=city, text=city))

        return options

    def SetupUI(self, salary_analyzer: SalaryAnalyzer, filename: str):
        data = salary_analyzer.GetData()

        self.__dropdown_cities = f.Dropdown(
            value="Город не выбран", label="Города", options=self.GetCitiesOptions(data)
        )

        self.__situation_button = f.Button(
            text="Получить данные...",
            on_click=lambda x: self.__ParseData(salary_analyzer, data, filename),
        )

        self.city_dataFrame = f.DataTable(
            columns=[f.DataColumn(f.Text("Город/Область"))], rows=[]
        )

        base_interface = f.Row(
            controls=[
                f.Column(controls=[self.__dropdown_cities]),
                f.Column(controls=[self.__situation_button]),
            ],
            alignment=f.MainAxisAlignment.CENTER,
            expand=False,
        )

        self.__column_table = f.Column(
            controls=[self.city_dataFrame],
            alignment=f.MainAxisAlignment.CENTER,
            horizontal_alignment=f.MainAxisAlignment.START,
            on_scroll=f.ScrollMode.AUTO,
        )

        table_row = f.Row(controls=[self.__column_table])

        self.controls.append(base_interface)
        self.controls.append(table_row)

    def __ParseData(self, sa: SalaryAnalyzer, data: pd.DataFrame, filename: str):
        message = sa.PerformAnalysis(data, filename, ANALYZE_MESSAGE)

        self.__ViewDatatableWithData(sa.GetData(), self.__dropdown_cities.value)
        self.__text = f.Markdown(
            value="\n".join(map(lambda x: x.message.content, message.choices))
        )

        if not self.__ready:
            result_label = f.Container(content=self.__text)

            self.__column_table.controls.append(result_label)
            self.__ready = True

        self.page.update()

    def __ViewDatatableWithData(self, data: pd.DataFrame, city: str):
        if city == "Город не выбран":
            return f.DataTable(columns=[f.DataColumn(f.Text("Город/Область"))], rows=[])

        column_indexes = list(data.columns)
        column_indexes.insert(0, "Город/Область")
        column_indexes = list(
            map(lambda x: f.DataColumn(label=f.Text(x)), column_indexes)
        )

        city_data = data.loc[city].to_list()
        city_data.insert(0, city)
        city_data = list(map(lambda x: f.DataCell(f.Text(x)), city_data))

        self.city_dataFrame.columns = column_indexes
        self.city_dataFrame.rows = [f.DataRow(city_data)]


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    sa = SalaryAnalyzer(
        os.getenv("LINK_TO_STATISTIC"), START_MESSAGE, os.getenv("GIGACHAT_TOKEN")
    )

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

    f.app(main)
