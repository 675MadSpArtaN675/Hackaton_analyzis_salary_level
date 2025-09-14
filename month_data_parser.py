from dotenv import load_dotenv, find_dotenv

from enum import IntEnum
from pprint import pprint
from urllib.parse import quote
from aiohttp_retry import RetryClient, ExponentialRetry

import requests as r
import aiohttp as ah
import aiofiles as af
import bs4 as bs

import os, io
import re
import asyncio as aio

class MonthEnum(IntEnum):
    Jan: int = 0
    Feb: int = 1
    Mar: int = 2
    Apr: int = 3
    May: int = 4
    Jun: int = 5
    Jul: int = 6
    Aug: int = 7
    Sep: int = 8
    Oct: int = 9
    Nov: int = 10
    Dec: int = 11

class MoneyDataParser:
    __domain: str
    __parser: bs.BeautifulSoup

    @staticmethod
    def ConvertMonth(link: str):
        month = re.search(r's?(\w*?)\s?\d{4}', link).group(1)

        match(month):
            case "январь":
                return MonthEnum.Jan
            case "февраль":
                return MonthEnum.Feb
            case "март":
                return MonthEnum.Mar
            case "апрель":
                return MonthEnum.Apr
            case "май":
                return MonthEnum.May
            case "июнь":
                return MonthEnum.Jun
            case "июль":
                return MonthEnum.Jul
            case "август":
                return MonthEnum.Aug
            case "сентябрь":
                return MonthEnum.Sep
            case "октябрь":
                return MonthEnum.Oct
            case "ноябрь":
                return MonthEnum.Nov
            case "декабрь":
                return MonthEnum.Dec
            
            case _:
                return MonthEnum.Dec

    @staticmethod
    def GetDomain(url: str):
        return re.search(r"(https?://.*?)/", url).group(1)

    def __init__(self, url: str):
        html_file = r.get(url).content

        self.__parser = bs.BeautifulSoup(html_file, "lxml")
        self.__domain = MoneyDataParser.GetDomain(url)

    def QuartalPartition(self, links: list[str] | map | filter) -> dict[int, str]:
        quartals = {i:[] for i in range(1, 5)}

        for link in links:
            if (re.search(r"январь|февраль|март", link) is not None):
                quartals[1].append(link)
            elif (re.search(r"апрель|май|июнь", link) is not None):
                quartals[2].append(link)
            elif (re.search(r"июль|август|сентябрь", link) is not None):
                quartals[3].append(link)
            elif (re.search(r"октябрь|ноябрь|декабрь", link) is not None):
                quartals[4].append(link)

        return quartals
    
    def MonthSort(self, links: list[str] | map | filter):
        return sorted(links, key=lambda element: MoneyDataParser.ConvertMonth(element).value)
    
    def FilterByYear(self, links: list[str] | map | filter, year: int | str):
        return filter(lambda element: re.search(r"\d{4}", element, re.I).group() == str(year), links)
    
    def GetDocLinks(self, title: str) -> map:
        content_section = self.FindContentSection(title)

        return self.__GetContentElements(content_section)

    def FindContentSection(self, title: str):
        title_section = self.FindTitleSection(title)
        content_section = title_section.find_next_sibling("div")
        
        return content_section
    
    def __GetContentElements(self, content_section : bs.PageElement):
        contents = content_section.find_all("div", attrs={"class": "document-list__item"})

        return map(lambda element: self.__domain + element.find("a").get("href"), contents)
    
    def FindTitleSection(self, title: str):
        elements = self.__parser.find_all("div", {"class": "toggle-section__title"})
        for element in elements:
            if (re.match(title, element.get_text(strip=True), re.I)):
                return element

        return None
    
class MoneyDataFilesDownloader:
    __client: r.Session

    @staticmethod
    def GetFileName(url: str):
        name = re.search(r"mediabank(/.+?)$", url)
        
        if name is not None:
            name = name.group(1).strip()
        
            return re.sub(r"\s*\(\d*\)", "", name)
    
    def __init__(self):
        self.__client = r.Session()

    def DownloadFiles(self, urls: list[str]):
        files_data = []
        for url in urls:
            files_data.append(self.DownloadFile(url))

        return files_data

    def DownloadFile(self, url: str):
        filename = "./files_downloaded" + MoneyDataFilesDownloader.GetFileName(url)
        with self.__client.get(url) as res:
            content = res.content

            with open(filename, "wb") as file:
                file.write(content)

            return content 

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    url = "https://36.rosstat.gov.ru/folder/26390"
    m = MoneyDataParser(url)
    docs = m.GetDocLinks(os.environ["TITLE_TO_FOUND"])
    filtered = m.FilterByYear(docs, 2024)
    sorted_years = m.MonthSort(filtered)
    quartals = m.QuartalPartition(filtered)

    loop = aio.new_event_loop()
    aio.set_event_loop(loop)

    md = MoneyDataFilesDownloader()
    ready = md.DownloadFiles(sorted_years)

    print(ready)
    