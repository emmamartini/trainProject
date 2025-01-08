import sqlite3
import requests
from api_key import AUTH_KEY

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"


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
            if len(response_data['RESPONSE']['RESULT'][0]['TrainStation']) < 50:
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