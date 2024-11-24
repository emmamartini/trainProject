from config import AUTH_KEY
from programwithfunctions import connect_to_database
from datetime import datetime, timedelta
import requests
import os
import time

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

def send_message(trainInfo):
    conn = connect_to_database()
    cur = conn.cursor()
    txtFile = "textMessages.txt"
    if not os.path.exists(txtFile):
        with open(txtFile, "w", encoding="utf-8") as file:
            file.write("")
            
    departureTimeAndDate = trainInfo[0][1]
    departureTime = departureTimeAndDate[11:16]
    if trainInfo[0][4] != False:
        estimatedTimeAndDate = trainInfo[0][4]
        estimatedDepartureTime = estimatedTimeAndDate[11:16]
        
    #if the train is on time
    if all(value == False for value in trainInfo[2:7]):
        status = "On_Time"
        print("Tåget är i tid!! God bless!")
        textMessage = f"Hello NAME, your train is on time and is leaving at {departureTime}."
        
    #if the train is cancelled
    elif trainInfo[3] == True:
        status = "Canceled"
        print("Tåget är inställt! Attans!")
        textMessage = f"Hello NAME, your train with departure time {departureTime} is sadly canceled."

    #if the train is delayed
    elif departureTime != estimatedDepartureTime:
        status = "Delayed"
        print(f"Tåget är försenat till {trainInfo[4]}")
        textMessage = f"Hello NAME, your train with original departure time {departureTime} is estimated to leave {estimatedDepartureTime}."
    
    with open(txtFile, "a", encoding="utf-8") as file:
        file.write(textMessage + "\n")
    
    if status == "Delayed":
        cur.execute("INSERT OR IGNORE INTO TrainAnnouncement (TrainId, AdvertisedTime, EstimatedTime, Status) VALUES (?, ?, ?, ?)", (passengerId, departureTime, estimatedDepartureTime, status))
        conn.commit()
    else:
        cur.execute("INSERT OR IGNORE INTO TrainAnnouncement (TrainId, AdvertisedTime, Status) VALUES (?, ?, ?, ?)", (passengerId, departureTime, status))
        conn.commit()
    
    

def actual_names(subscriptions):
    conn = connect_to_database()
    cur = conn.cursor()
    for subscription in subscriptions:
        cur.execute('SELECT OwnerName FROM TrainOwner where TrainOwnerId LIKE ?', (subscription[2],))
        actualOwnerName = cur.fetchall()
        actualOwnerName = actualOwnerName[0][0]
        cur.execute('SELECT StationSignature FROM Station where StationId LIKE ?', (subscription[3],))
        actualStationName = cur.fetchall()
        actualStationName = actualStationName[0][0]
        print(subscription)
        print(actualOwnerName)
        print(actualStationName)
        print(subscription[6])
        
        subscription = list(subscription)
        subscription[2] = actualOwnerName
        subscription = tuple(subscription)
        subscription = list(subscription)
        subscription[3] = actualStationName
        subscription = tuple(subscription)
        print(subscription)
        get_train_from_api(subscription)


def get_train_from_api(subscriptionRow):  
    trains = []
    last_change_id = 0
    todaysDate = datetime.now()
    todaysDate = todaysDate.strftime("%Y-%m-%d")
    while True:
        xml_request = f"""
        <REQUEST>
          <LOGIN authenticationkey='{AUTH_KEY}'/>
          <QUERY objecttype="TrainAnnouncement" schemaversion="1.5" limit="50" changeid='{last_change_id}'>
            <FILTER>
            <AND>
                <EQ name="ActivityType" value="Avgang"/>
                <EQ name="InformationOwner" value="{subscriptionRow[2]}"/>
                <EQ name="LocationSignature" value="{subscriptionRow[3]}"/>
                <EQ name="AdvertisedTimeAtLocation" value="{todaysDate}T{subscriptionRow[6]}:00"/>
            </AND>
            </FILTER>
            <INCLUDE>LocationSignature</INCLUDE>
            <INCLUDE>EstimatedTimeIsPreliminary</INCLUDE>
            <INCLUDE>Canceled</INCLUDE>
            <INCLUDE>EstimatedTimeAtLocation</INCLUDE>
            <INCLUDE>PlannedEstimatedTimeAtLocation</INCLUDE>
            <INCLUDE>AdvertisedTimeAtLocation</INCLUDE>
            <INCLUDE>PlannedEstimatedTimeAtLocationIsValid</INCLUDE>
          </QUERY>
        </REQUEST>
        """
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(API_URL, headers=headers, data=xml_request)
        print(response.json())
        if response.status_code == 200:
            response_data = response.json()
            for item in response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']:
                trains.append([
                    item['LocationSignature'],
                    item['AdvertisedTimeAtLocation'],
                    item['EstimatedTimeIsPreliminary'],
                    item['Canceled'],
                    item.get('EstimatedTimeAtLocation', False),
                    item.get('PlannedEstimatedTimeAtLocation', False),
                    item['PlannedEstimatedTimeAtLocationIsValid']])
            if 'INFO' in response_data['RESPONSE']['RESULT'][0]:
                last_change_id = response_data['RESPONSE']['RESULT'][0]['INFO'].get('LASTCHANGEID')
            if len(response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']) < 50:
                if len(response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']) == 1:
                    send_message(trains)
                else:
                    print("attans")
                break
        pass
    pass

def check_subscription_time():
    while True:
        dateAndTime = datetime.now()
        currentDay = dateAndTime.weekday()

        def dateToDay(weekday):
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            return weekdays[weekday]
        day = dateToDay(currentDay)

        def matching_day_and_time(day):
            currentTime = datetime.now()
            currentTimeString = currentTime.strftime("%H:%M")
            timeIn15 = currentTime + timedelta(minutes=51)
            timeIn15String = timeIn15.strftime("%H:%M")
            conn = connect_to_database()
            cur = conn.cursor()
            cur.execute('SELECT * FROM Subscription WHERE DayOfTheWeek = ? AND DepartureTime = ? AND Active = 1', (day, timeIn15String))
            subscriptions = cur.fetchall()
            return(subscriptions)

        match = matching_day_and_time(day)

        if match:
            actual_names(match)
        else:
            print("No matches found!")
        time.sleep(60)
      
    #när dagen är rätt och tiden är en kvart innan ska ett meddelande skickas till passageraren
    #skapa ett program som då och då kollar om någons tid närmar sig(separat funktion)   
    #om en tid närmar sig ska detta triggas oftare (15 min, 10 min, 5 min, varje minut) 
check_subscription_time()

def save_message_to_database():
    pass