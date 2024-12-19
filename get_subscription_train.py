import threading
import queue
from config import AUTH_KEY
from programwithfunctions import connect_to_database
from datetime import datetime, timedelta
import requests
import os
import time

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

delayedTrainQueue = queue.Queue()

def delayed_train():
    activityIdList = []
    while True:
        try:
            delayedTrain = delayedTrainQueue.get(timeout=180)
            trainInfo, passengerInfo = delayedTrain
            
            if not more_than_5(trainInfo, passengerInfo):
                print("hej1")
                continue
            
            if not has_train_departed(trainInfo):
                print("hej2")
                delayedTrainQueue.put(delayedTrain)
            
        except queue.Empty:
            pass

def more_than_5(trainInfo, passengerInfo):
    if trainInfo[0][5] == False:
        departureTimeAndDateString = trainInfo[0][2]
    else:
        departureTimeAndDateString = trainInfo[0][5]
        
    departureTimeString = departureTimeAndDateString[11:16]    
    currentTimeString = datetime.now().strftime("%H:%M")  
    currentTime = datetime.strptime(currentTimeString, "%H:%M")
    departureTime = datetime.strptime(departureTimeString, "%H:%M")
    print(departureTime)
    print(currentTime)  
    timeDifference = currentTime - departureTime
    
    #Om tåget går inom 5 minuter
    if timedelta(minutes=0) <= timeDifference <= timedelta(minutes=5):
        return True
    
    #Om tåget har avgått
    elif timeDifference <= timedelta(minutes=0):
        departured_train(trainInfo)
        return False
    
    #Om tåget avgår inom 5 minuter
    elif timeDifference > timedelta(minutes=5):
        delayed_messages(trainInfo, passengerInfo)

def has_train_departed(trainInfo):
    if trainInfo[0][5] == False:
        departureTimeAndDateString = trainInfo[0][2]
    else:
        departureTimeAndDateString = trainInfo[0][5]
        
    departureTimeString = departureTimeAndDateString[11:16]    
    currentTimeString = datetime.now().strftime("%H:%M")  
    currentTime = datetime.strptime(currentTimeString, "%H:%M").time()
    departureTime = datetime.strptime(departureTimeString, "%H:%M").time()
    print(departureTime)
    print(currentTime)  
    if departureTime <= currentTime:
        departured_train(trainInfo)
        return True
    

def departured_train(trainInfo):
    conn = connect_to_database()
    cur = conn.cursor()
    print(trainInfo)
    trainInfo[0][2] = trainInfo[0][2][0:16]
    trainInfo[0][2] = trainInfo[0][2].replace("T", " ")    
    cur.execute('SELECT StationId FROM Station where StationSignature = ?', (trainInfo[0][0].lower(),))
    stationId = cur.fetchone()
    stationId = stationId[0]
    cur.execute('SELECT StationId FROM Station where StationSignature = ?', (trainInfo[0][1].lower(),))
    endStationId = cur.fetchone()
    endStationId = endStationId[0]
    cur.execute('SELECT TrainOwnerId FROM TrainOwner where OwnerName = ?', (trainInfo[0][8].lower(),))
    trainOwnerId = cur.fetchone()
    trainOwnerId = trainOwnerId[0]
    
    if trainInfo[0][4] == True:
        print(1)
        cur.execute("INSERT OR IGNORE INTO Train (TrainOwnerId, StationId, EndStationId, Canceled, OriginalDepartureTime) VALUES (?, ?, ?, ?, ?)", (trainOwnerId, stationId, endStationId, trainInfo[0][4], trainInfo[0][2]))
    elif trainInfo[0][5] == False:
        print(2)
        cur.execute("INSERT OR IGNORE INTO Train (TrainOwnerId, StationId, EndStationId, Canceled, OriginalDepartureTime, ActualDepartureTime) VALUES (?, ?, ?, ?, ?, ?)", (trainOwnerId, stationId, endStationId, trainInfo[0][4], trainInfo[0][2], trainInfo[0][2]))
    else:
        trainInfo[0][5] = trainInfo[0][5][0:16]
        trainInfo[0][5] = trainInfo[0][5].replace("T", " ")
        print(3)
        cur.execute("INSERT OR IGNORE INTO Train (TrainOwnerId, StationId, EndStationId, Canceled, OriginalDepartureTime, ActualDepartureTime) VALUES (?, ?, ?, ?, ?, ?)", (trainOwnerId, stationId, endStationId, trainInfo[0][4], trainInfo[0][2], trainInfo[0][5]))
    print("hej")
    conn.commit()


def delayed_messages(trainInfo, passengerInfo):
    txtFile = "textMessages.txt"
    if not os.path.exists(txtFile):
        with open(txtFile, "w", encoding="utf-8") as file:
            file.write("")
    
    departureTimeAndDate = trainInfo[0][2]
    departureTime = departureTimeAndDate[11:16]
    if trainInfo[0][5] != False:
        estimatedTimeAndDate = trainInfo[0][5]
        estimatedDepartureTime = estimatedTimeAndDate[11:16]        
    
    textMessage = f"Hello {passengerInfo[1]}, your train with original departure time {departureTime} is still delayed and is estimated to leave {estimatedDepartureTime}. We will contact you every 3 minutes."
    with open(txtFile, "a", encoding="utf-8") as file:
        file.write(textMessage + "\n")   
    pass


def send_message(trainInfo, passengerId):
    conn = connect_to_database()
    cur = conn.cursor()
    endStationSignature = trainInfo[0][0]
    stationSignature = trainInfo[0][1]

    cur.execute('SELECT * FROM Passenger WHERE PassengerId = ?', (passengerId,))
    passengerInfo = cur.fetchone()
    cur.execute('SELECT StationId FROM Station WHERE StationSignature = ?', (stationSignature.lower(),))
    stationId = cur.fetchone()
    stationId = stationId[0]
    cur.execute('SELECT StationId FROM Station WHERE StationSignature = ?', (endStationSignature.lower(),))
    endStationId = cur.fetchone()
    endStationId = endStationId[0]   
    txtFile = "textMessages.txt"
    if not os.path.exists(txtFile):
        with open(txtFile, "w", encoding="utf-8") as file:
            file.write("")
            
    departureTimeAndDate = trainInfo[0][2]
    departureTime = departureTimeAndDate[11:16]
    if trainInfo[0][5] != False:
        estimatedTimeAndDate = trainInfo[0][5]
        estimatedDepartureTime = estimatedTimeAndDate[11:16]
        
    #if the train is on time
    if all(value == False for value in trainInfo[2:7]) and trainInfo[0][5] == False:
        has_train_departed(trainInfo)
        textMessage = f"Hello {passengerInfo[1]}, your train is on time and is leaving at {departureTime}."
        
    #if the train is cancelled
    elif trainInfo[0][4] == True:
        departured_train(trainInfo)
        textMessage = f"Hello {passengerInfo[1]}, your train with departure time {departureTime} is sadly canceled."

    #if the train is delayed
    elif departureTime != estimatedDepartureTime:
        delayedTrainQueue.put((trainInfo, passengerInfo))
        textMessage = f"Hello {passengerInfo[1]}, your train with original departure time {departureTime} is estimated to leave {estimatedDepartureTime}."
    
    with open(txtFile, "a", encoding="utf-8") as file:
        file.write(textMessage + "\n")    
    

def actual_names(subscriptions):
    print(subscriptions)

    conn = connect_to_database()
    cur = conn.cursor()
    for subscription in subscriptions:  
        cur.execute('SELECT OwnerName FROM TrainOwner where TrainOwnerId LIKE ?', (subscription[2],))
        actualOwnerName = cur.fetchall()
        actualOwnerName = actualOwnerName[0][0]
        cur.execute('SELECT StationSignature FROM Station where StationId LIKE ?', (subscription[3],))
        actualStationName = cur.fetchall()
        actualStationName = actualStationName[0][0]
        cur.execute('SELECT StationSignature FROM Station where StationId LIKE ?', (subscription[4],))
        actualEndStationName = cur.fetchall()
        actualEndStationName = actualEndStationName[0][0]
        
        subscription = list(subscription)
        subscription[2] = actualOwnerName
        subscription[3] = actualStationName
        subscription[4] = actualEndStationName
        subscription = tuple(subscription)
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
                <EQ name="ToLocation.LocationName" value="{subscriptionRow[4]}"/>
                <EQ name="AdvertisedTimeAtLocation" value="{todaysDate}T{subscriptionRow[6]}:00"/>
            </AND>
            </FILTER>
            <INCLUDE>ActivityId</INCLUDE>
            <INCLUDE>InformationOwner</INCLUDE>
            <INCLUDE>LocationSignature</INCLUDE>
            <INCLUDE>ToLocation.LocationName</INCLUDE>
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
        if response.status_code == 200:
            response_data = response.json()
            for item in response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']:
                trains.append([
                    item['ToLocation'][0]['LocationName'],
                    item['LocationSignature'],
                    item['AdvertisedTimeAtLocation'],
                    item['EstimatedTimeIsPreliminary'],
                    item['Canceled'],
                    item.get('EstimatedTimeAtLocation', False),
                    item.get('PlannedEstimatedTimeAtLocation', False),
                    item['PlannedEstimatedTimeAtLocationIsValid'],
                    item['InformationOwner'],
                    item['ActivityId']])
            print(trains)
            if 'INFO' in response_data['RESPONSE']['RESULT'][0]:
                last_change_id = response_data['RESPONSE']['RESULT'][0]['INFO'].get('LASTCHANGEID')
            if len(response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']) < 50:
                if len(response_data['RESPONSE']['RESULT'][0]['TrainAnnouncement']) == 1:
                    send_message(trains, subscriptionRow[1])
                else:
                    print("0 or more than 1 trains returned")
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
            timeNow = currentTime + timedelta(minutes=-300)
            timeNowString = timeNow.strftime("%H:%M")
            timeIn5 = currentTime + timedelta(minutes=5)
            timeIn5String = timeIn5.strftime("%H:%M")
            timeIn10 = currentTime + timedelta(minutes=10)
            timeIn10String = timeIn10.strftime("%H:%M")
            timeIn15 = currentTime + timedelta(minutes=15)
            timeIn15String = timeIn15.strftime("%H:%M")
            conn = connect_to_database()
            cur = conn.cursor()
            cur.execute('SELECT * FROM Subscription WHERE DayOfTheWeek = ? AND DepartureTime IN (?, ?, ?, ?) AND Active = 1', (day, timeNowString, timeIn5String, timeIn10String, timeIn15String))
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
delayedThread = threading.Thread(target=delayed_train, daemon=True)
delayedThread.start()
print("delayedTrain thread started.")    

check_subscription_time()

def save_message_to_database():
    pass