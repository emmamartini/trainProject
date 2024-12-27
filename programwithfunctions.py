from config import AUTH_KEY
import sqlite3
import time
import bcrypt
import requests
from datetime import datetime, timedelta


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def returning():
    print("Returning...")
    print(""" """)
    time.sleep(3)


def connect_to_database():
    return sqlite3.connect("train.db")


def display_homescreen():
    listHomescreen = [
        "Welcome to the homescreen!",
        "1. Create User",
        "2. Log in",
        "3. End program",
    ]
    for i in listHomescreen:
        print(i)


def new_user(userInfo):
    conn = connect_to_database()
    cur = conn.cursor()

    cur.execute(
        "SELECT Email, PhoneNumber FROM passenger WHERE Email = ? OR PhoneNumber = ?",
        (userInfo[2], userInfo[4]),
    )
    existingData = cur.fetchone()

    if existingData is None:
        hashedPassword = hash_password(userInfo[3])
        userInfo[3] = hashedPassword
        cur.execute(
            "INSERT INTO passenger (FirstName, LastName, Email, Password, PhoneNumber, Active) VALUES (?, ?, ?, ?, ?, 1)",
            userInfo,
        )
        conn.commit()
        print("User has been created!")
    else:
        print("Oops! This email or phone number is already in use.")

    conn.close()


def gather_userInfo():
    FirstName = input("Enter your first name: ").lower().title()
    while not FirstName.isalpha():
        FirstName = input("Please enter your first name: ").lower().title()
    print(FirstName)
    LastName = input("Enter your last name: ").lower().title()
    while not LastName.isalpha():
        LastName = input("Please enter your last name: ").lower().title()
    Email = input("Enter your email address: ").lower()
    while not Email:
        Email = input("Please enter your email address: ").lower()
    Password = input("Create a password: ")
    while not Password:
        Password = input("Please enter a password: ")
    while True:
        PhoneNumber = input("Enter your phone number: ")
        while not PhoneNumber:
            PhoneNumber = input("Please enter your phone number: ")
        if PhoneNumber.isdigit():
            break
        else:
            print("Try again with numbers!")

    userInfo = [FirstName, LastName, Email, Password, PhoneNumber]
    return userInfo


def check_password(storedHash, password):
    return bcrypt.checkpw(password.encode("utf-8"), storedHash)


def log_in():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM passenger")
    existingData = cur.fetchall()

    yourPhoneNumber = input("Please write your phone number: ")
    yourPassword = input("Please write your password: ")

    if existingData:
        for info in existingData:
            if yourPhoneNumber == info[5]:
                if not check_password(info[4], yourPassword):
                    print(
                        "You are an existing user but you are using the wrong password."
                    )
                    returning()
                    break
                if check_password(info[4], yourPassword) and info[6] == 0:
                    print("Your account is inactivated.")
                    activationAnswer = (
                        input("Do you want to activate your account? Yes/No: ")
                        .lower()
                        .capitalize()
                    )
                    if activationAnswer == "Yes":
                        cur.execute(
                            "UPDATE passenger SET Active = 1 WHERE PhoneNumber = ?",
                            (info[5],),
                        )
                        print(
                            "Thank you! Your account has been activated! Please log in again"
                        )
                        conn.commit()
                    returning()
                    break
                if check_password(info[4], yourPassword) and info[6] == 1:
                    print(f"Welcome {info[1]} {info[2]}!")
                    user_dashboard(info)
        if yourPhoneNumber != info[5]:
            print("No matching phone number found!")
            returning()
    if not existingData:
        print("No matching users found!")
        returning()


def user_dashboard(userInfo):
    userList = [
        "1. See train subscriptions",
        "2. Add subscription",
        "3. Delete subscription",
        "4. Update your account",
        "5. Log out",
    ]

    while True:
        conn = connect_to_database()
        cur = conn.cursor()

        cur.execute(
            "SELECT Active FROM Passenger WHERE PassengerId = ?", (userInfo[0],)
        )
        activeStatus = cur.fetchone()
        if 0 in activeStatus:
            return

        for option in userList:
            print(option)
        userNumber = int(input("Choose one of the numbers above: "))

        if userNumber == 1:
            see_train_subscriptions(userInfo[0])
        elif userNumber == 2:
            add_subscription(userInfo[0])
        elif userNumber == 3:
            delete_subscription(userInfo[0])
        elif userNumber == 4:
            update_information(userInfo[0])
        elif userNumber == 5:
            print("Logging out...")
            break
            # ta bort no matching phone number härifrån
        else:
            print("Invalid choice.")


def see_train_subscriptions(passengerId):
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Subscription WHERE PassengerId = ? AND Active = 1",
        (passengerId,),
    )
    subscriptions = cur.fetchall()

    if not subscriptions:
        print("You have no active subscriptions.")
    else:
        for subscription in subscriptions:
            print(subscription)
    time.sleep(3)
    conn.close()


def train_existence(subscription):
    conn = connect_to_database()
    cur = conn.cursor()
    API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"
    last_change_id = 0
    subscriptionList = []
    print(subscription)
    cur.execute(
        "SELECT StationSignature FROM Station where StationId = ?", (subscription[1],)
    )
    existingStationSignature = cur.fetchone()
    existingStationSignatureValue = existingStationSignature[0]

    def next_day(weekday):
        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        weekday = weekdays[weekday]
        nextDate = datetime.now()
        while nextDate.weekday() != weekday:
            nextDate += timedelta(days=1)
        return nextDate.strftime("%Y-%m-%d")

    day = subscription[2]
    next_weekday_date = next_day(day)

    while True:
        xml_request = f"""
            <REQUEST>
              <LOGIN authenticationkey='{AUTH_KEY}'/>
              <QUERY objecttype="TrainAnnouncement" schemaversion="1.9" limit="100" changeid='{last_change_id}'>
                <FILTER>
                <AND>
                    <IN name="TypeOfTraffic.Code" value="YNA001, YNA004"/>
                    <EQ name="ActivityType" value="Avgang"/>
                    <EQ name="InformationOwner" value="{subscription[0]}"/>
                    <EQ name="LocationSignature" value="{existingStationSignatureValue}"/>
                    <EQ name="AdvertisedTimeAtLocation" value="{next_weekday_date}T{subscription[3]}:00"/>
                </AND>
                </FILTER>
                <INCLUDE>InformationOwner</INCLUDE>
                <INCLUDE>AdvertisedTimeAtLocation</INCLUDE>
                <INCLUDE>LocationSignature</INCLUDE>
                <INCLUDE>ToLocation.LocationName</INCLUDE>
              </QUERY>
            </REQUEST>
            """

        headers = {"Content-Type": "text/xml"}

        response = requests.post(API_URL, headers=headers, data=xml_request)
        if response.status_code == 200:
            response_data = response.json()
            for item in response_data["RESPONSE"]["RESULT"][0]["TrainAnnouncement"]:
                subscriptionList.append(item)
            return subscriptionList


def add_subscription(passengerId):
    conn = connect_to_database()
    cur = conn.cursor()
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    while True:
        print("You want to add a train subscription")
        subscriptionTrainOwner = input(
            "Write which train owner you want to subscribe to: "
        ).lower()
        while not subscriptionTrainOwner:
            subscriptionTrainOwner = input("Please enter the train owner: ").lower()
        cur.execute(
            "SELECT TrainOwnerId FROM TrainOwner where OwnerName = ?",
            (subscriptionTrainOwner,),
        )
        existingOwner = cur.fetchone()
        if not existingOwner:
            print("Sorry! No train owner with that name")
            cur.execute(
                "SELECT OwnerName FROM TrainOwner where OwnerName LIKE ?",
                ("%" + subscriptionTrainOwner + "%",),
            )
            similarOwner = cur.fetchall()
            if similarOwner:
                print(f"These train owners have similiar names: {similarOwner}?")
        if existingOwner:
            break
    while True:
        subscriptionStation = input(
            "Write which departure station you want to subscribe to: "
        ).lower()
        while not subscriptionStation:
            subscriptionStation = input("Please enter your departure station: ").lower()
        cur.execute(
            "SELECT StationId FROM Station where StationName = ?",
            (subscriptionStation,),
        )
        existingStation = cur.fetchone()
        if existingStation:
            break
        if not existingStation:
            print("Sorry, no station found with that name.")
            cur.execute(
                "SELECT StationName FROM Station where StationName LIKE ?",
                ("%" + subscriptionStation + "%",),
            )
            similarStation = cur.fetchall()
            if similarStation:
                print(f"These stations have similiar names: {similarStation}?")

    subscriptionDay = input(
        "Enter the day of the week you want to subscribe to: "
    ).lower()
    while not subscriptionDay in weekdays:
        subscriptionDay = input("Please enter the day of the week: ").lower()

    def format(subscriptionTime):
        if len(subscriptionTime) == 5 and subscriptionTime[2] == ":":
            hours = subscriptionTime[:2]
            minutes = subscriptionTime[3:]
            if hours.isdigit() and minutes.isdigit():
                integerHour = int(hours)
                integerMinute = int(minutes)
                if 0 <= integerHour < 24 and 0 <= integerMinute < 60:
                    return True
        else:
            return False

    subscriptionTime = input(
        "Enter the time of the day you want to subscribe to (in HH:MM-format): "
    )
    while not format(subscriptionTime):
        subscriptionTime = input("Please enter the time of the day (HH:MM): ")

    cur.execute(
        "SELECT Subscription.PassengerId, Subscription.TrainOwnerId, Subscription.StationId, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.Active FROM Subscription WHERE PassengerId = ? AND TrainOwnerId = ? AND StationId = ? AND DayOfTheWeek = ? AND DepartureTime = ?",
        (
            passengerId,
            existingOwner[0],
            existingStation[0],
            subscriptionDay,
            subscriptionTime,
        ),
    )
    existingData = cur.fetchone()
    subscriptionInfo = [
        subscriptionTrainOwner,
        existingStation[0],
        subscriptionDay,
        subscriptionTime,
    ]
    subscriptionListReturned = train_existence(subscriptionInfo)

    while True:
        subscriptionEndStation = input("Enter the end station of the train: ").lower()
        while not subscriptionEndStation:
            subscriptionEndStation = input("Please enter the end station: ").lower()
        cur.execute(
            "SELECT StationId FROM Station where StationName = ?",
            (subscriptionEndStation,),
        )
        existingEndStation = cur.fetchone()
        if existingEndStation:
            break
        if not existingEndStation:
            print("Sorry, no station found with that name.")
            cur.execute(
                "SELECT StationName FROM Station where StationName LIKE ?",
                ("%" + subscriptionEndStation + "%",),
            )
            similarEndStation = cur.fetchall()
            if similarEndStation:
                print(f"These stations have similiar names: {similarEndStation}?")

    if subscriptionListReturned:
        for endStation in subscriptionListReturned:
            cur.execute(
                "SELECT StationId, StationSignature FROM Station where StationName = ?",
                (subscriptionEndStation,),
            )
            subscriptionEndStationAndSignature = cur.fetchone()
            print(subscriptionEndStationAndSignature[0])
            print(endStation["ToLocation"][0]["LocationName"])
            if (
                subscriptionEndStationAndSignature[1]
                == endStation["ToLocation"][0]["LocationName"].lower()
            ):
                subscriptionEndStationId = subscriptionEndStationAndSignature[0]
            else:
                print("Sorry! No train found with that end station.")
                returning()
                break

            if existingData is None:
                cur.execute(
                    "INSERT OR IGNORE INTO Subscription (PassengerId, TrainOwnerId, StationId, EndStationId, DayOfTheWeek, DepartureTime, Active) VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (
                        passengerId,
                        existingOwner[0],
                        existingStation[0],
                        subscriptionEndStationId,
                        subscriptionDay,
                        subscriptionTime,
                    ),
                )
                conn.commit()
                print(
                    f"You are now subscribed to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock"
                )

            elif existingData and existingData[5] == 0:
                cur.execute(
                    "SELECT Subscription.SubscriptionId, Subscription.PassengerId, Subscription.TrainOwnerId, Subscription.StationId, Subscription.EndStationId, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.Active FROM Subscription WHERE PassengerId = ? AND TrainOwnerId = ? AND StationId = ? AND DayOfTheWeek = ? AND DepartureTime = ? AND Active = 0",
                    (
                        passengerId,
                        existingOwner[0],
                        existingStation[0],
                        subscriptionEndStationId,
                        subscriptionDay,
                        subscriptionTime,
                    ),
                )
                existingData = cur.fetchone()

                if existingData:
                    cur.execute(
                        "UPDATE Subscription SET Active = 1 WHERE SubscriptionId = ?",
                        (existingData[0],),
                    )
                    conn.commit()
                    print(
                        f"Your subscription has been reactivated to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock"
                    )

            elif existingData and existingData[5] == 1:
                if existingData:
                    print(
                        f"You are already subscribed to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock"
                    )

    else:
        print("Sorry, no match found!")
    time.sleep(1)
    returning()


def delete_subscription(passengerId):
    conn = connect_to_database()
    cur = conn.cursor()
    print("You want to delete a train subscription")
    try:
        cur.execute(
            "SELECT SubscriptionId FROM Subscription WHERE Active = 1 AND PassengerId = ?",
            (passengerId,),
        )
        allSubscriptionsQuery = cur.fetchall()
        if len(allSubscriptionsQuery) == 1:
            cur.execute(
                "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
                (allSubscriptionsQuery[0][0],),
            )
            print(
                "Thank you! You only had one active subscription and it has now been unactivated!"
            )
            conn.commit()
            returning()
            return
    except:
        print("No subscriptions found.")
        returning()
        return
    theOwner = input("From which train owner? ")
    cur.execute(
        "SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ?",
        (passengerId, theOwner),
    )
    ownerQuery = cur.fetchall()
    if len(ownerQuery) == 1:
        cur.execute(
            "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
            (ownerQuery[0][0],),
        )
        print("Thank you! Your subscription has now been unactivated!")
        conn.commit()
        returning()
        return
    if len(ownerQuery) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return
    theStation = input("From which train station? ")
    cur.execute(
        "SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Subscription.StationId FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ?",
        (passengerId, theOwner, theStation),
    )
    departureQuery = cur.fetchall()
    if len(departureQuery) == 1:
        cur.execute(
            "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
            (departureQuery[0][0],),
        )
        print("Thank you! Your subscription has now been unactivated!")
        conn.commit()
        returning()
        return
    if len(departureQuery) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return
    theDay = input("What day? ")
    cur.execute(
        "SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Station.StationName, Subscription.DayOfTheWeek FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ? AND Subscription.DayOfTheWeek = ?",
        (passengerId, theOwner, theStation, theDay),
    )
    dayQuery = cur.fetchall()
    if len(dayQuery) == 1:
        cur.execute(
            "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
            (dayQuery[0][0],),
        )
        print("Thank you! Your subscription has now been unactivated!")
        conn.commit()
        returning()
        return
    if len(dayQuery) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return
    theTime = input("Which time? ")
    cur.execute(
        "SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Station.StationName, Subscription.DayOfTheWeek, Subscription.DepartureTime FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ? AND Subscription.DayOfTheWeek = ? AND Subscription.DepartureTime = ?",
        (passengerId, theOwner, theStation, theDay, theTime),
    )
    timeQuery = cur.fetchall()
    if len(timeQuery) == 1:
        cur.execute(
            "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
            (timeQuery[0][0],),
        )
        print("Thank you! Your subscription has now been unactivated!")
        conn.commit()
        returning()
        return
    if len(timeQuery) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return
    theEndStation = input("Which end station? ")
    cur.execute(
        "SELECT Station.StationId FROM Station WHERE Station.StationName = ?",
        (theEndStation,),
    )
    endStation = cur.fetchone()
    if len(endStation) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return
    cur.execute(
        "SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Station.StationName, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.EndStationId FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ? AND Subscription.DayOfTheWeek = ? AND Subscription.DepartureTime = ? AND Subscription.EndStationId = ?",
        (passengerId, theOwner, theStation, theDay, theTime, endStation),
    )
    endstationQuery = cur.fetchall()
    if len(endStation) == 1:
        cur.execute(
            "UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?",
            (endstationQuery[0][0],),
        )
        print("Thank you! Your subscription has now been unactivated!")
        conn.commit()
        returning()
        return
    if len(endStation) == 0:
        print("No matches found in your subscriptions!")
        returning()
        return


def validate_time_format(timeString):
    if len(timeString) == 5 and timeString[2] == ":":
        hours = timeString[:2]
        minutes = timeString[3:]
        return (
            hours.isdigit()
            and minutes.isdigit()
            and 0 <= int(hours) < 24
            and 0 <= int(minutes) < 60
        )
    return False


def update_information(passengerId):
    conn = connect_to_database()
    cur = conn.cursor()

    while True:
        print("You want to update your information")
        updateList = [
            "1. Change first name",
            "2. Change last name",
            "3. Change email",
            "4. Change password",
            "5. Change phone number",
            "6. Deactivate account",
            "7. Go back",
        ]
        for k in updateList:
            print(k)
        while True:
            try:
                updateNumber = int(input("Choose one of the numbers above: "))
                while not 0 < updateNumber <= 7:
                    updateNumber = int(input("Choose one of the numbers above: "))
                if 0 < updateNumber < 8:
                    break
            except ValueError:
                print("Try again with numbers!")
        if updateNumber == 1:
            print("You want to change your first name")
            updateFirstName = (
                input("Write what you want to change it to: ").lower().title()
            )
            while not updateFirstName:
                updateFirstName = (
                    input("Write what you want to change your first name to: ")
                    .lower()
                    .title()
                )
            cur.execute(
                "UPDATE passenger SET FirstName = ? WHERE PassengerId = ?",
                (updateFirstName, passengerId),
            )
            print(
                f"Thank you! Your first name has now been updated to {updateFirstName}!"
            )
            conn.commit()
            returning()
            break
        if updateNumber == 2:
            print("You want to change your last name")
            updateLastName = (
                input("Write what you want to change it to: ").lower().title()
            )
            while not updateLastName:
                updateLastName = (
                    input("Write what you want to change your last name to: ")
                    .lower()
                    .title()
                )
            cur.execute(
                "UPDATE passenger SET LastName = ? WHERE PassengerId = ?",
                (updateLastName, passengerId),
            )
            print(
                f"Thank you! Your last name has now been updated to {updateLastName}!"
            )
            conn.commit()
            returning()
            break
        if updateNumber == 3:
            while True:
                print("You want to change your email address")
                updateEmail = input("Write what you want to change it to: ")
                while not updateEmail:
                    updateEmail = input(
                        "Write what you want to change your email address to: "
                    ).lower()
                cur.execute("SELECT * FROM passenger where Email = ?", (updateEmail,))
                existingEmail = cur.fetchone()
                if existingEmail:
                    print("This email address is already in use")
                else:
                    break
            cur.execute(
                "UPDATE passenger SET Email = ? WHERE PassengerId = ?",
                (updateEmail, passengerId),
            )
            print(
                f"Thank you! Your email address has now been updated to {updateEmail}!"
            )
            conn.commit()
            returning()
            break
        if updateNumber == 4:
            print("You want to change your password")
            updatePassword = input("Write what you want to change it to: ")
            while not updatePassword:
                updatePassword = input(
                    "Write what you want to change your password to: "
                )
            cur.execute(
                "UPDATE passenger SET Password = ? WHERE PassengerId = ?",
                (updatePassword, passengerId),
            )
            print("Thank you! Your password has now been updated!")
            conn.commit()
            returning()
            break
        if updateNumber == 5:
            while True:
                updatePhoneNumber = input("Enter your new phone number: ")
                while not updatePhoneNumber:
                    updatePhoneNumber = input("Please enter your new phone number: ")
                if not updatePhoneNumber.isdigit():
                    print("Try again with numbers!")
                    continue
                cur.execute(
                    "SELECT * FROM passenger where PhoneNumber = ?",
                    (updatePhoneNumber,),
                )
                existingPhoneNumber = cur.fetchone()
                if existingPhoneNumber:
                    print("This phone number is already in use")
                else:
                    break
            cur.execute(
                "UPDATE passenger SET PhoneNumber = ? WHERE PassengerId = ?",
                (updatePhoneNumber, passengerId),
            )
            print(
                f"Thank you! Your phone number has now been updated to {updatePhoneNumber}!"
            )
            conn.commit()
            returning()
            break
        if updateNumber == 6:
            print("You want to deactivate your account")
            deleteOrNot = input("Are you sure? Yes/No: ").lower().capitalize()
            if deleteOrNot == "Yes":
                cur.execute(
                    "UPDATE Passenger SET Active = 0 WHERE PassengerId = ?",
                    (passengerId,),
                )
                print("Your account has now been deactivated!")
                conn.commit()
                returning()
                return
            else:
                print("Your account is still active!")
                returning()
                return
        if updateNumber == 7:
            returning()
            break


def main():
    runProgram = True
    while runProgram:
        display_homescreen()

        while True:
            try:
                number = int(input("Choose one of the numbers above: "))
                if 0 < number <= 3:
                    break
                else:
                    print("Try again!")
            except ValueError:
                print("Try again with numbers!")

        if number == 1:
            print("You want to create a user.")
            userInfo = gather_userInfo()
            new_user(userInfo)
            returning()

        if number == 2:
            log_in()

        if number == 3:
            print("Ending program...")
            runProgram = False


if __name__ == "__main__":
    main()
