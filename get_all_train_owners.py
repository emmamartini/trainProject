import sqlite3
import requests
from api_key import AUTH_KEY

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"


def get_owners():
    last_change_id = 0
    train_owner_set = set()
    
    while True:
        xml_request = f"""
        <REQUEST>
          <LOGIN authenticationkey='{AUTH_KEY}'/>
          <QUERY objecttype="TrainAnnouncement" schemaversion="1.5" limit="500000" changeid='{last_change_id}'>
            <INCLUDE>InformationOwner</INCLUDE>
          </QUERY>
        </REQUEST>
        """

        headers = {'Content-Type': 'text/xml'}
        
        response = requests.post(API_URL, headers=headers, data=xml_request)
        if response.status_code == 200:
            response_data = response.json()
            for item in response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']:
                informationOwner = item.get('InformationOwner', 'Unspecified')
                
                train_owner_set.add((informationOwner))
             
            if 'INFO' in response_data['RESPONSE']['RESULT'][0]:
                last_change_id = response_data['RESPONSE']['RESULT'][0]['INFO'].get('LASTCHANGEID')
            if len(response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']) < 500000:
                return (train_owner_set)

def exportOwner(train_owner_set):
    conn = sqlite3.connect("train.db")
    cur = conn.cursor()
    for owner in train_owner_set:
        cur.execute("INSERT OR IGNORE INTO TrainOwner (OwnerName) VALUES (?)", (owner.lower(),))
        conn.commit()
    conn.close()