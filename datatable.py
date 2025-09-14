from dotenv import find_dotenv, load_dotenv

from month_data_parser import MoneyDataParser, MoneyDataFilesDownloader

import os, io

import asyncio as aio
import pandas as pd
import pdfminer.high_level as pmhl
import pdfminer.layout as pml

class TableCreator:
    __money_parser: MoneyDataParser
    __files_downloader: MoneyDataFilesDownloader

    def __init__(self, url: str):
        load_dotenv(find_dotenv())

        self.__money_parser = MoneyDataParser(url)
        self.__files_downloader = MoneyDataFilesDownloader()

    def Parser(self, year :int | str):
        docs = self.__money_parser.GetDocLinks(os.environ["TITLE_TO_FOUND"])
        filtered = self.__money_parser.FilterByYear(docs, 2024)
        sorted_years = self.__money_parser.MonthSort(filtered)
        downloaded_files = self.__files_downloader.DownloadFiles(sorted_years)

        files_data = []
        for file in downloaded_files:
            files_data.append(self.__parse_file_page(file))

        return files_data
    
    def __parse_file_page(self, file_data_: io.BytesIO):
        print(file_data_)
        file_data = io.BytesIO(file_data_)
        output_fp = io.StringIO()

        try:
            pmhl.extract_text_to_fp(file_data, output_fp, page_numbers=[7])
            
            return output_fp
        
        except pmhl.pdfparser.PDFSyntaxError:
            return None


if __name__ == "__main__":
    url = "https://36.rosstat.gov.ru/folder/26390"

    tc = TableCreator(url)
    for i in tc.Parser(2024):
        print(i.read())