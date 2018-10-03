# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

class AthletesSpider(scrapy.Spider):
    name = 'athletes'
    allowed_domains = ['athletic.net']

    def start_requests(self):
        urls = ['https://www.athletic.net/TrackAndField/Division/Event.aspx?DivID=89120&Event=1']
        for url in urls:
            yield scrapy.Request(url = url, callback=self.parse)

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

    def parse(self, response):
        urls = response.xpath('//a[contains(@href, "/Athlete.aspx")]/@href').extract()
        for url in urls:
            yield scrapy.Request(url = "https://www.athletic.net/TrackAndField" + url[2:], callback = self.parse_page)

    def parse_page(self, response):
        # Every race will include name, school, racing season, location of race, date of race, and time
        name = response.xpath("//h2/text()").extract_first()[1:-1]
        seasons = response.xpath('//div[contains(@class, "athleteResults")]/div[contains(@class, "season")]')
        races = ""
        for i in range(0, len(seasons)):
            season = seasons[i].xpath('.//div[contains(@class, "card-header")]/h5/text()').extract_first().split()
            events = seasons[i].xpath('.//div[contains(@class, "card-block")]//h5/text()').extract() # will c
            school = seasons[i].xpath('.//div[contains(@class, "card-header")]//small//text()').extract_first()
            grade = seasons[i].xpath('.//div[contains(@class, "card-header")]//span//text()').extract_first()
            all_races = seasons[i].xpath('.//div[contains(@class, "card-block")]//tbody')
            for j in range(0, len(events)):
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
                    race = name + "," + school + "," + grade + "," + date + "," + season[1] + "," + \
                           events[j] + "," + racename + "," + rank + "," + time + "," + record + "," + \
                           team[0] + "," + team[1] + "," + response.request.url + ";\n"
                    races += race

        with open("output.csv", 'a+') as f:
            f.write(races)
