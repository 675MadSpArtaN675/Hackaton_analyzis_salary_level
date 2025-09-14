from typing import Sequence, Callable
import flet as f

class RootPage(f.View):
    __page: f.Page = None
    __file_choose_button: f.Button
    __file_parse_button: f.Button

    __parsing_func: Callable = None
    __choose_func: Callable = None

    def __init__(self, controls: Sequence[f.Control] = (), page: f.Page = None):
        super().__init__("/", controls=controls)

        if (page is not None):
            self.__page = page

    def SetupUI(self):
        self.__page.title = "Анализ уровня заработной платы"
        self.__page.theme_mode = f.ThemeMode.LIGHT
        self.__page.adaptive = True

        self.__page.vertical_alignment = f.MainAxisAlignment.CENTER
        self.__page.horizontal_alignment = f.CrossAxisAlignment.END

        self.__page.window.width = 515
        self.__page.window.height = 200

        self.__text_link_entry = f.TextField(label="Ссылка на файл")
        self.__file_choose_button = f.Button("Выбрать файл на диске...", on_click=self.__choose_func if self.__choose_func is not None else None)
        self.__file_parse_button = f.Button("Скачать/Спарсить файл...", on_click=self.__parsing_func if self.__parsing_func is not None else None)

        row_1 = f.Row([self.__text_link_entry, self.__file_parse_button])
        row_2 = f.Row([self.__file_choose_button])

        base_column = f.Row([f.Column([row_1, row_2], alignment=f.alignment.top_center)], alignment=f.alignment.center)

        self.__page.add(base_column)

    @property
    def ChooseEvent(self):
        return self.__choose_func
    
    @ChooseEvent.setter
    def ChooseEvent(self, func: Callable):
        self.__choose_func = func
        self.__file_choose_button = func


    @property
    def ParsingEvent(self):
        return self.__parsing_func
    
    @ParsingEvent.setter
    def ParsingEvent(self, func: Callable):
        self.__parsing_func = func
        self.__file_choose_button = func

    @property
    def WorkingPage(self):
        return self.__page

    @WorkingPage.setter
    def WorkingPage(self, page: f.Page):
        self.__page = page 