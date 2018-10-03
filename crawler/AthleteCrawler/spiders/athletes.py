# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from contextlib import contextmanager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

class AthletesSpider(scrapy.Spider):
    name = 'athletes'
    allowed_domains = ['athletic.net']

    def start_requests(self):
        #Login to the site
        driver = webdriver.Chrome("C:/Users/director/Documents/workspace/AthleteCrawler/chromedriver.exe")
        self.login(driver)

        divids = ['89120', '79871', '70667', '59640', '49524', '43258', '32448', '28139', '17385', '10054',
                  '10056', '19973', '30768', '35071', '45959', '52329', '62480', '73438', '82610', '91862',
                  '92344', '83077', '73896', '62919', '52756', '46339', '35438', '31125', '20262', '15967',
                  '10057', '17228', '27991', '32304', '43109', '49375', '59489', '70513', '79715', '88964']

        for i in range(12, 13):
            urls = self.fetch_links(driver, divids[i])
            for url in urls:
                req = scrapy.Request(url = url, callback=self.parse)
                req.meta['id'] = i
                yield req

                page = 1
                next_url = url + "&page=" + str(page)
                next_page = requests.get(next_url).text
                while ("There are no results matching your criteria." not in next_page):
                    req = scrapy.Request(url = next_url, callback=self.parse)
                    req.meta['id'] = i
                    yield req

                    page += 1
                    next_url = url + "&page=" + str(page)
                    next_page = requests.get(next_url).text

    def fetch_links(self, driver, divid):
        driver.get("https://www.athletic.net/TrackAndField/Division/Event.aspx?DivID=%s&Event=1;" % (divid))

        # find numbers for all events
        event_option_list = driver.find_elements_by_xpath("//select[@ng-model='appC.params.eventId']//option[(contains(text(), 'Meters') or contains(text(), 'Mile'))]")
        events = [event_option.get_attribute('value') for event_option in event_option_list]
        urls = []

        # create urls for each event in this divid
        for event in events:
            url = "https://www.athletic.net/TrackAndField/Division/Event.aspx?DivID=%s&Event=%s;" % (divid, event)
            urls.append(url)
        return urls

    def parse(self, response):
        athlete_urls = response.xpath('//a[contains(@href, "/Athlete.aspx")]/@href').extract()
        for url in athlete_urls:
            req = scrapy.Request(url = "https://www.athletic.net/TrackAndField" + url[2:], callback = self.parse_page)
            req.meta['id'] = response.meta['id']
            yield req

    def login(self, driver):
        driver.get("https://www.athletic.net/account/login/?ReturnUrl=%2Fdefault.aspx")
        email = driver.find_element_by_name("email")
        password = driver.find_element_by_name("password")
        login = driver.find_element_by_xpath("//button[contains(text(), 'Log In')]")
        email.send_keys("krishnasunder@gmail.com")
        password.send_keys("eadGBE!1athletic")
        login.click()
        time.sleep(2)

    def getDate(self, year, monthday):
        month = monthday.split()[0]
        day = monthday.split()[1]
        months = {
            "Jan" : "01",
            "Feb" : "02",
            "Mar" : "03",
            "Apr" : "04",
            "May" : "05",
            "Jun" : "06",
            "Jul" : "07",
            "Aug" : "08",
            "Sep" : "09",
            "Oct" : "10",
            "Nov" : "11",
            "Dec" : "12"
        }
        days = {
            "1" : "01",
            "2" : "02",
            "3" : "03",
            "4" : "04",
            "5" : "05",
            "6" : "06",
            "7" : "07",
            "8" : "08",
            "9" : "09",
        }
        return months.get(month, "n/a") + days.get(day, day) + year

    def parse_page(self, response):
        # Every race will include name, school, racing season, location of race, date of race, and time
        name = response.xpath("//h2/text()").extract_first()[1:-1]
        seasons = response.xpath('//div[contains(@class, "athleteResults")]/div[contains(@class, "season")]')
        races = ""
        for i in range(0, len(seasons)):
            season = seasons[i].xpath('.//div[contains(@class, "card-header")]/h5/text()').extract_first().split()
            events = seasons[i].xpath('.//div[contains(@class, "card-block")]//h5/text()').extract()
            school = seasons[i].xpath('.//div[contains(@class, "card-header")]//small//text()').extract_first()
            grade = seasons[i].xpath('.//div[contains(@class, "card-header")]//span//text()').extract_first()
            all_races = seasons[i].xpath('.//div[contains(@class, "card-block")]//tbody')
            for j in range(0, len(events)):
                if (("Mile" in events[j]) or ("Meter" in events[j])):
                    races_for_event = all_races[j].xpath('.//tr')
                    for k in range(0, len(races_for_event)):
                        entry = races_for_event[k].xpath('.//td')
                        rank = re.sub(r'\W+', '', entry[0].xpath('.//text()').extract_first())
                        racetime = entry[1].xpath('.//text()').extract()
                        time = racetime[0]; record = ' '
                        if (len(racetime) > 1): # windspeed and/or PR included
                            if ("PR" in racetime[1]):
                                record = "PR"
                            elif("SR" in racetime[1]):
                                record = "SR"
                        date = self.getDate(season[0], entry[2].xpath('.//text()').extract_first())
                        racename = entry[3].xpath('.//text()').extract_first()
                        team = entry[4].xpath('.//text()').extract_first().split()
                        if(len(team) != 2):
                            team.append("")
                        race = [name, school, grade, date, season[1], events[j], racename,
                                rank, time, record, team[0], team[1], response.request.url]
                        for info in race:
                            if(type(info) is not None):
                                races += str(info) + ","
                            else:
                                races += " ,"
                        races = races[:-1] + ";\n"

        filename = "outputs/" + str(response.meta['id']) + ".csv"
        with open(filename, 'a+') as f:
            f.write(races)
