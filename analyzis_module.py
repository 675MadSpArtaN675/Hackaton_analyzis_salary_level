from gigachat_service import GigaChat_Service
from datatable import PdfStatisticsParser

import re

class SalaryAnalyzer:
    __year: int
    __parser: PdfStatisticsParser
    __neuro_module: GigaChat_Service

    def __init__(self, token: str, url: str, year: int | str, start_message: str):
        if type(year) == str and re.match(r"\d{4}", year):
            self.__year = int(year)
        
        else:
            self.__year = year
        
        self.__parser = PdfStatisticsParser(url)
        self.__neuro_module = GigaChat_Service(token, start_message)
    
    def PerformAnalysis(self):
        return