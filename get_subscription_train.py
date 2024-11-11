from config import AUTH_KEY
from programwithfunctions import connect_to_database
from datetime import datetime, timedelta
import sqlite3
import requests
import sys

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

def check_subscription_time():
    dateAndTime = datetime.datetime.now()
    currentDay = dateAndTime.weekday()
    currentTime = dateAndTime.time()
    currentTime = currentTime.strftime("%H:%M")
    currentDate = dateAndTime.strftime("%Y-%m-%d")

    def dateToDay(weekday):
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return weekdays[weekday]
    day = dateToDay(currentDay)
    print(day) 
    
    def matching_day_and_time(day, time, timein15):
        timeIn15Minutes = time + timedelta(minutes=15)
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute('SELECT * FROM Subscription WHERE DayOfTheWeek = ? AND DepartureTime BETWEEN ? AND ? Active = 1', (day, time, timein15))
        subscriptions = cur.fetchall()
        
        return True
        
    matchOrNot = matching_day_and_time()
    
    if matchOrNot
        get_subscriptions()
      
    #när dagen är rätt och tiden är en kvart innan ska ett meddelande skickas till passageraren
    #skapa ett program som då och då kollar om någons tid närmar sig(separat funktion)   
    #om en tid närmar sig ska detta triggas oftare (15 min, 10 min, 5 min, varje minut) 
check_subscription_time()


def get_subscriptions():
    #om check_subscription_time returnerar något (hela raderna som matchar) kollas det upp här!
    #då hämtar denna funktion information från databasen
    #och returnerar information till get_subscription_from_api
    pass

def get_subscription_from_api():
    pass

def send_message():
    #om tåget är i tid: on_time()
    #om tåget är sent: delayed()
    #om tåget är inställt: cancelled()
    pass

def save_message_to_database():
    pass



def get_stations():
    last_change_id = 0
    train_station_list = []
    
    while True:
        xml_request = f"""
        <REQUEST>
          <LOGIN authenticationkey='{AUTH_KEY}'/>
          <QUERY objecttype="TrainStation" namespace="rail.infrastructure" schemaversion="1.5" limit="50" changeid='{last_change_id}'>
            <INCLUDE>AdvertisedLocationName</INCLUDE>
            <INCLUDE>CountryCode</INCLUDE>
            <INCLUDE>CountyNo</INCLUDE>
            <INCLUDE>LocationSignature</INCLUDE>
          </QUERY>
        </REQUEST>
        """

        headers = {'Content-Type': 'text/xml'}
        
        response = requests.post(API_URL, headers=headers, data=xml_request)
        if response.status_code == 200:
            response_data = response.json()
            for item in response_data['RESPONSE']['RESULT'][0]['TrainStation']:
                train_station_list.append([
                    item['AdvertisedLocationName'],
                    item['CountryCode'],
                    item.get('CountyNo', 'Unspecified'),
                    item['LocationSignature']])
             
            if 'INFO' in response_data['RESPONSE']['RESULT'][0]:
                last_change_id = response_data['RESPONSE']['RESULT'][0]['INFO'].get('LASTCHANGEID')
            # Om antalet stationer är mindre än gränsen, bryt ut från loopen
            if len(response_data['RESPONSE']['RESULT'][0]['TrainStation']) < 50:  # Om vi fick färre än 50 annonser, finns det inga fler att hämta
                return (train_station_list)

def exportTrain(train_station_list):
    conn = sqlite3.connect("train.db")
    cur = conn.cursor()
    for station in train_station_list:
        StationSignature = station[3]
        cur.execute('SELECT StationSignature FROM station WHERE StationSignature = ?', (StationSignature,))
        existingData=cur.fetchone()

        if existingData is None:
            if isinstance(station[2], list):
                countyTransformed = ', '.join(map(str, station[2]))
            else:
                countyTransformed = station[2]
            stationData = [station[0].lower(), station[1], countyTransformed, station[3].lower()]
            cur.execute("INSERT OR IGNORE INTO station (StationName, Country, County, StationSignature) VALUES (?, ?, ?, ?)", stationData)
            conn.commit()
    conn.close()