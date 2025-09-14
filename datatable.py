from dotenv import find_dotenv, load_dotenv
from pprint import pprint, pp

from month_data_parser import MoneyDataParser, MoneyDataFilesDownloader

import os, re

import asyncio as aio
import pandas as pd
import pdfminer.high_level as pmhl
import pdfminer.layout as pml

class PdfStatisticsParser:
    __money_parser: MoneyDataParser
    __files_downloader: MoneyDataFilesDownloader

    @staticmethod
    def GetMonthName(filename: str):
        return re.search(r"области\s(.*?)\s*\d{4}\s*года\.pdf$", filename).group(1)

    def __init__(self, url: str):
        load_dotenv(find_dotenv())

        self.__money_parser = MoneyDataParser(url)
        self.__files_downloader = MoneyDataFilesDownloader()

    def ParseFiles(self, year :int | str):
        files_start = "./files_downloaded"

        if (not os.path.exists(files_start)):
            os.mkdir(files_start)

        sorted_years = self.__get_files_names(year)
        self.__files_downloader.DownloadFiles(sorted_years)

        files_data = pd.DataFrame(self.__get_data_from_files(files_start))
        files_data.to_excel(excel_writer="./salaries.xlsx", 
                  sheet_name="Уровень зарплат за текущий год")
        
        return files_data

    def __get_files_names(self, year: int):
        docs = self.__money_parser.GetDocLinks(os.environ["TITLE_TO_FOUND"])
        filtered = self.__money_parser.FilterByYear(docs, year)
        sorted_years = self.__money_parser.MonthSort(filtered)

        return sorted_years

    def __get_data_from_files(self, files_start):
        files_data = dict()
        for file in os.listdir(files_start):
            filename = files_start + "/" + file

            name = PdfStatisticsParser.GetMonthName(file)
            lines = self.__parse_file_page(filename, 7)

            files_data[name] = dict(lines)
            os.remove(filename)

        os.removedirs(files_start)
        return files_data
    
    def __parse_file_page(self, file_name: str, number_page: int):
        lines = []
        for page in pmhl.extract_pages(file_name, page_numbers=[number_page - 1]):
            for element in page:
                if isinstance(element, pml.LTTextContainer):
                    lines.extend([sub_element for sub_element in element])
        
        return self.__filter_files(lines[3:])

    def __filter_files(self, lines: list[pml.LTTextLine]):
        cities = []
        nums = []

        for line in lines:
            line_str = line.get_text().strip()

            if line_str == "":
                continue

            if re.match(r"г\..*|.+Федерация|.+область", line_str):
                cities.append(line_str)

            elif re.match(r"\d+[^/\\]\s*\d+", line_str):
                nums.append(line_str.replace(" ", ""))

        sorted_nums = list(sorted(map(int, nums[:len(cities)]), reverse=True))

        return zip(cities, sorted_nums)



if __name__ == "__main__":
    url = "https://36.rosstat.gov.ru/folder/26390"

    psp = PdfStatisticsParser(url)
    data = psp.ParseFiles(2025)
    
    