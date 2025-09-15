from gigachat_service import GigaChat_Service
from datatable import PdfStatisticsParser
from month_data_parser import MoneyDataParser, MonthEnum

from pandas import DataFrame

from typing import Final

import pandas as pd

import re
import datetime as dt



class SalaryAnalyzer:
    __year: int
    __data: pd.DataFrame

    __parser: PdfStatisticsParser
    __neuro_module: GigaChat_Service

    _quartal_partition: dict[str, list[str]]

    @staticmethod
    def _QuartalPartition(months: list[str] | map | filter) -> dict[int, list[str]]:
        quartals = {i:[] for i in range(1, 5)}

        for month in months:
            if (re.search(r"январь|февраль|март", month) is not None):
                quartals[1].append(month)
            elif (re.search(r"апрель|май|июнь", month) is not None):
                quartals[2].append(month)
            elif (re.search(r"июль|август|сентябрь", month) is not None):
                quartals[3].append(month)
            elif (re.search(r"октябрь|ноябрь|декабрь", month) is not None):
                quartals[4].append(month)

        return quartals

    @staticmethod
    def _FindNeedQuartal(data: dict[int, list[str]], month: str):
        last_not_empty = -1
        for quartal_num in range(1, 5):
            elements = data[quartal_num]

            if elements != []:
                last_not_empty = quartal_num

            if month in elements:
                return quartal_num
        
        return last_not_empty
    
    def __init__(self, url: str, start_message: str, token: str):
        self.__year = dt.date.today().year

        self.__parser = PdfStatisticsParser(url, self.__year)
        self.__neuro_module = GigaChat_Service(token, start_message)
    
    def PerformAnalysis(self, data: pd.DataFrame, filename: str, analyze_message: str):
        self._quartal_partition = SalaryAnalyzer._QuartalPartition(data.columns)
        print(self._quartal_partition[1])
        uploaded_file = self.__neuro_module.upload_file_from_disk(filename)
        uploaded_file_id = uploaded_file.id_

        message = self.__create_message(analyze_message)
        return self.__neuro_module.send_message_with_file(message, [uploaded_file_id])

    def DownloadFilesFromWebSite(self):
        data = self.__parser.ParseFiles(self.__year)
        filename = self.__parser.CreateExcelFile()

        self.__data = data
        return filename

    def GetData(self):
        return self.__data

    def __create_message(self, analyze_message: str):
        now_month = MoneyDataParser.ConvertIntMonth(dt.date.today().month)
        quartal = SalaryAnalyzer._FindNeedQuartal(self._quartal_partition, now_month)

        message = analyze_message.format(quartal, quartal - 1)

        return message
    

if __name__ == "__main__":
    q = SalaryAnalyzer.QuartalPartition(["январь", "февраль", "март", "апрель", "май", "июнь", "июль"])
    print(q)