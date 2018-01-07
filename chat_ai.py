#!/usr/bin/env python
# coding: utf-8

# Fail, mida võib muuta ja mis tuleb esitada koduse töö lahendusena
# Faili nime peab jätma samaks
# Faili võib muuta suvaliselt, kuid see peab sisaldama funktsiooni getResponse(),
# millele antakse argumendina ette kasutajalt sisendiks saadud tekst (sõnena)
# ja mis tagastab sobiva vastuse (samuti sõnena)

import urllib.request
from urllib.parse import quote
import json
import re
import time
import math


# Freimi klass, hoiab asju meeles.
class Memory:
    def __init__(self):
        self.hasGreeted = False
        self.userName = None
        self.askForName = True
        self.attributes = []
        self.city = None
        self.weatherData = [None, None, None] # ilmad [today, tomorrow, day after tomorrow]
        self.time = 0 # 0 täna, 1 homme, 2 ülehomme,

    # Kui kasutaja on kirjutanud uue linna, siis laeme uue linna kohta ilma andmed alla.
    def updateCity(self, newCity):
        self.city = newCity
        self.weatherData[0] = getCurrentWeather(newCity)
        foreCastData = getForecast(newCity)

        dayInSeconds = 24 * 3600
        nextTime = time.time() + dayInSeconds

        tomorrow = False

        # Suht ebaefektiivne aga töötab
        for d in foreCastData["list"]:
            if d["dt"] > nextTime and not tomorrow:
                self.weatherData[1] = d
                nextTime += dayInSeconds
                tomorrow = True
            if d["dt"] > nextTime:
                self.weatherData[2] = d
                break

    # Erinevate parameetrite getterid.
    def getWindSpeed(self):
        return str(round(self.weatherData[self.time]["wind"]["speed"]))

    def getTemperature(self):
        return str(round(self.weatherData[self.time]["main"]["temp"]))

    def getHumidity(self):
        return str(round(self.weatherData[self.time]["main"]["humidity"]))

    def getPressure(self):
        return str(round(self.weatherData[self.time]["main"]["pressure"]))

    def getCountry(self):
        iso = self.weatherData[0]["sys"]["country"]
        return getCountryByIso(iso)

    def getCoordinates(self):
        lon = self.weatherData[0]["coord"]["lon"]
        lat = self.weatherData[0]["coord"]["lat"]
        return lon, lat

    # https://stackoverflow.com/questions/7490660/converting-wind-direction-in-angles-to-text-words
    def getWindDirection(self):
        angle = self.weatherData[self.time]["wind"]["deg"]
        val = math.floor((angle / 45) + 0.5)
        tuuled = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
        return tuuled[round(val % 8)]


# Kasutaja poolt sisestatud lause
class Sentence:
    # Võtmesõnad erinevatele parameetritele.
    temperatureKeywords = ("temperature", "warm", "cold", "hot", "chill", "temp", "warmth")
    humidityKeywords = ("humidity")
    pressureKeywords = ("pressure")
    countryKeywords = ("country", "land")
    coordinateKeywords = ("coordinates", "location")

    def __init__(self, text):
        self.order = []
        self.words = dict()
        self.text = text.lower()
        self.__preprocess()

    # Töötleb kasutaja sisendit
    def __preprocess(self):
        self.text = re.sub("[?!,]", "", self.text) # eemaldab ? ! ja , märgid
        wds = self.text.split(" ") # splitib teksti tühikute kaupa
        for word in wds:
            data = dict() # Leiab sõne lemma
            data["root"] = word
            self.order.append(data["root"]) # Ning lisab selle sõnade dictionarisse ning listi. List hoiab lihtsalt järjekorda
            if data["root"] not in self.words:
                self.words[data["root"]] = data
                self.words[data["root"]]["raw"] = word
            else:
                self.words[data["root"] + "_"] = data
                self.words[data["root"]]["raw"] = word

    def findName(self): # Otsib kasutaja nime lausest, kui ei leia tagastab None
        if "name" in self.words and "is" in self.words:
            index = self.order.index("is")
            if index != -1 and len(self.order) > index + 1:
                return self.order[index + 1].capitalize()
        return None

    def getCityName(self): # Otsib linna nime
        global allCities
        reg = re.match(".*in\s([A-ZÖÄÜÕ](\w|[ -.])+)", self.text) # Algul proovib lihtsalt leida regexiga
        if reg:                                                 
            name = reg.group(1)
            name1 = name[:-1]
            if name in allCities:
                return name
            if name1 in allCities:
                return name1
        return None

    def getAttributes(self): # Tagastab lauses olnud võtmesõnade listi
        keywords = []
        if any(i in self.text for i in self.humidityKeywords):
            keywords.append("humidity")
        if any(i in self.text for i in self.temperatureKeywords):
            keywords.append("temp")
        if any(i in self.text for i in self.pressureKeywords):
            keywords.append("pressure")
        if "wind" in self.text:
            if "speed" in self.text:
                keywords.append("windSpeed")
            if "direction" in self.text:
                keywords.append("windDir")
        if any(i in self.text for i in self.countryKeywords):
            keywords.append("country")
        if any(i in self.text for i in self.coordinateKeywords):
            keywords.append("coordinates")
        return keywords

    def getTime(self): # Tagastab aja, kui lauses oli seda mainitud
        if "tomorrow" in self.text:
            if "after" in self.text:
                return 2
            else:
                return 1
        if "today" in self.text:
            return 0
        return -1


def getResponse(text):
    global memory
    response = ""

    if not memory.hasGreeted: # Kui ei ole tervitanud siis tervitab ennast
        memory.hasGreeted = True
        return "Hello, my name is Bot!"

    sentence = Sentence(text)  # Loob lause objekti
    if memory.askForName: # Kui nime ei ole, siis küsib niikaua kuni on nime saanud
        name = sentence.findName()
        if name is not None:
            memory.userName = name
            memory.askForName = False
            return "Hello, " + name + "!"
        else:
            return "I didn't get your name."

    cityName = sentence.getCityName() # Otsitakse ja kontrollitakse linna nime
    if cityName is not None:
        memory.updateCity(cityName)

    attributes = sentence.getAttributes() # Otsitakse ja kontrollitakse atribuutide listi
    if len(attributes) > 0:
        memory.attributes = attributes

    time = sentence.getTime() # Otsitakse ja kontrollitakse aega
    if time != -1:
        memory.time = time

    if cityName is None and len(attributes) == 0 and time == -1: # Kui lauses ei ole linna nime, atribuute, ega aega, siis ei saada aru.
        return "Sorry, I didn't understand!"

    if memory.city is None: # Kui mälust puudub linn, küsitakse linna
        return "But what city?"
    if len(memory.attributes) == 0: # Kui puuduvad atribuudid siis küsitakse neid, vaikimisi arvaetakse tänast ilma
        return "But about what?"

    cityName = memory.city
    stuffBefore = False

    if any(i in memory.attributes for i in ["temp", "pressure", "humidity", "windSpeed", "windDir"]): # See if blokk väljastab ilma andmed
        times = ["Today", "Tomorrow", "Day after tomorrow"]                                               # Seda vaja, et kui ainult riiki tahetakse siis ei oleks "Tartus . Tartu asub Eestis"

        if memory.time != 0 or time != -1: # Kui kasutaja täpsustas aega, lisatakse see ka juurde või kui see ei ole täna
            response += times[memory.time] + " "

        response += "in" + cityName # Linna nimi
        parts = []
        for at in memory.attributes: # Parameetrid
            if at == "temp":
                parts.append("temperature is " + memory.getTemperature() + " degrees")
            elif at == "pressure":
                parts.append("air pressure is " + memory.getPressure() + "hPa")
            elif at == "humidity":
                parts.append("humidity is " + memory.getHumidity() + "%")
            elif at == "windSpeed":
                parts.append("wind speed is " + memory.getWindSpeed() + " m/s")
            elif at == "windDir":
                parts.append("wind blows from " + memory.getWindDirection())

        response += ", ".join(parts)
        stuffBefore = True

    if "country" in memory.attributes: # Riigi väljastus
        if stuffBefore:
            response += ". "
        response += memory.city + " is located in " + memory.getCountry()

    if "coordinates" in memory.attributes: # Koordinaatide väljastus
        if stuffBefore:
            response += ". "
        lon, lat = memory.getCoordinates()
        response += memory.city + " coordinates are " + str(lon) + " longitude and " + str(lat) + " latitude"

    return response + "."


def getDictFromUrl(url):
    stream = urllib.request.urlopen(url)
    data = json.loads(stream.read().decode())
    return data


def getCurrentWeather(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q=' + quote(city) + '&units=metric&APPID=' + APPID
    return getDictFromUrl(url)


def getForecast(city):
    url = 'http://api.openweathermap.org/data/2.5/forecast?q=' + quote(city) + '&units=metric&APPID=' + APPID
    return getDictFromUrl(url)


def getCountryByIso(iso):
    # Päring: http://prog.keeleressursid.ee/ws_riigid/index.php?iso=<ISO kood>
    # ISO kahetähelised koodid: https://en.wikipedia.org/wiki/ISO_3166-1
    # Vastus: riigi nimi (eesti keeles)
    url = "http://prog.keeleressursid.ee/ws_riigid/index.php?iso=" + iso
    stream = urllib.request.urlopen(url)
    return stream.read().decode()

APPID = '75afb38423166da380c3b8d55105538d'
memory = Memory()
with open("cities.txt", encoding="utf8") as f:
    allCities = f.readlines()

allCities = [x.strip() for x in allCities]
