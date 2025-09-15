from dotenv import find_dotenv, load_dotenv

from month_data_parser import MoneyDataParser, MoneyDataFilesDownloader

import os, re

import pandas as pd
import pdfminer.high_level as pmhl
import pdfminer.layout as pml

class PdfStatisticsParser:
    __data: pd.DataFrame = None
    __money_parser: MoneyDataParser
    __files_downloader: MoneyDataFilesDownloader

    __year: int

    @staticmethod
    def GetMonthName(filename: str):
        return re.search(r"области\s(.*?)\s*\d{4}\s*года\.pdf$", filename).group(1)

    def __init__(self, url: str, year: int):
        load_dotenv(find_dotenv())

        self.__year = year

        self.__money_parser = MoneyDataParser(url)
        self.__files_downloader = MoneyDataFilesDownloader()

    def UpdateYear(self, year: int):
        self.__year = year
    
    def ParseFiles(self, year :int = None):
        if year is None:
            year = self.__year;
        
        files_start = "./files_downloaded"

        if (not os.path.exists(files_start)):
            os.mkdir(files_start)

        if len(os.listdir(files_start)) <= 0:
            sorted_years = self.__get_files_names(year)
            self.__files_downloader.DownloadFiles(sorted_years)

        self.__data = pd.DataFrame(data=self.__get_data_from_files(files_start))
        
        return self.__data
    
    def CreateExcelFile(self, filename: str = None):
        name = os.getenv("EXCEL_FILE_NAME") if filename is None else filename
        self.__data.to_string(buf=f"./{name}")
        
        return name

    def GetOutputFileName(self):
        return os.getenv("EXCEL_FILE_NAME")
    
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

    psp = PdfStatisticsParser(url, 2025)
    data = psp.ParseFiles()
    print(data.loc["Воронежская область"])