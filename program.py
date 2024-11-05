import sqlite3
import time
import getpass

conn = sqlite3.connect("train.db")
cur = conn.cursor()

listHomescreen=["Welcome to the homescreen!", "1. Create User", "2. Log in", "3. End program"]

x=1
runProgram=True
while runProgram:

    for i in listHomescreen:
        print(i)
        x=+1
    if x<3:
        False
    
    while True:
        try:
            number=int(input("Choose one of the numbers above: "))
            if 0 < number <= 3:
                break
            else:
                print("Try again!")
        except ValueError:
            print("Try again with numbers!")


    if number==1:
        print("You want to create a user.")
        def newUser(userInfo):
            conn = sqlite3.connect("train.db")
            cur = conn.cursor()

            cur.execute('SELECT Email, PhoneNumber FROM passenger WHERE Email = ? OR Phonenumber = ?', (Email, PhoneNumber,))
            existingData=cur.fetchone()
        
            if existingData is None:
                cur.execute("INSERT OR IGNORE INTO passenger (FirstName, LastName, Email, Password, PhoneNumber, Active) VALUES (?, ?, ?, ?, ?, 1)", tuple(userInfo,))
                conn.commit()
                print("User has been created!")
            else:
                print("Oops! This email is already in use.")

            conn.close()

        FirstName = input("Enter your first name: ").lower().title()
        while not FirstName:
            FirstName = input("Please enter your first name: ").lower().title()

        LastName = input("Enter your last name: ").lower().title()
        while not LastName:
            LastName = input("Please enter your last name: ").lower().title()

        Email = input("Enter your email address: ").lower()
        while not Email:
            Email = input("Please enter your email address: ").lower()

        Password = getpass.getpass("Create a password: ")
        while not Password:
            Password = getpass.getpass("Please enter a password: ")

        while True:
            PhoneNumber = input("Enter your phone number: ")
            while not PhoneNumber: 
                PhoneNumber = input("Please enter your phone number: ")
            if PhoneNumber.isdigit():
                break
            else:
                print("Try again with numbers!")

        userInfo=[FirstName, LastName, Email, Password, PhoneNumber]
        newUser(userInfo)
        print("Going back to the homescreen...")
        print(""" """)
        time.sleep(1)

    if number==2:
        conn = sqlite3.connect("train.db")
        cur = conn.cursor()
        cur.execute('SELECT * FROM passenger')
        existingData=cur.fetchall()
        print("You want to log in")
        yourPhoneNumber=input("Please write your phone number: ")
        yourPassword=getpass.getpass("Please write your password: ")
        if existingData:
            for info in existingData:
                if yourPhoneNumber == info[5]:
                    if yourPassword != info[4]:
                        print("You are an existing user but you are using the wrong password.")          
                        print("Going back to the homescreen...")
                        print(""" """)
                        time.sleep(1)
                        break
                    if yourPassword == info[4] and info[6] == 0:
                        print("Your account is inactivated.") 
                        activationAnswer = input("Do you want to activate your account? Y/N: ")
                        if activationAnswer == "Y":
                            cur.execute("UPDATE passenger SET Active = 1 WHERE PhoneNumber =?", (info[5]))
                            print(f"Thank you! Your account has been activated! Please log in again")
                            conn.commit()
                            print("Going back to the homescreen...")
                            print(""" """)
                            time.sleep(1)
                            break
                        else:
                            print("Going back to the homescreen...")
                            print(""" """)
                            time.sleep(1)
                            break
                    if yourPassword == info[4] and info[6] == 1:
                        print("Logging in...")
                        print(""" """)
                        time.sleep(1)
                        print(f"Welcome {info[1]} {info[2]}!")
                        userList=["1. See train subscriptions", "2. Add subscription", "3. Delete subscription", "4. Update your account", "5. Log out"]
                        q=1
                        runUserProgram=True
                        while runUserProgram:
                            conn = sqlite3.connect("train.db")
                            cur = conn.cursor()
                            cur.execute('SELECT * FROM passenger where PassengerId = ?', (info[0],))
                            passengerInfo=cur.fetchone()
                            cur.execute('SELECT * FROM Subscription where PassengerId = ?', (info[0],))
                            trainSubscription = cur.fetchall()
                            for l in userList:
                                print(l)
                                q=+1
                            if q<5:
                                False
                            while True:
                                try:
                                    userNumber=int(input("Choose one of the numbers above: "))
                                    if 0 < userNumber <= 5:
                                        break
                                    else:
                                        print("Try again!")
                                except ValueError:
                                    print("Try again with numbers!")
                            if userNumber==1:
                                #bara där dom är aktiva!
                                print("You want to see your train subscriptions")
                                if not trainSubscription:
                                    print("Not any active subscriptions yet!")
                                else:
                                    print(trainSubscription)
                                print(""" """)
                                time.sleep(3)
                            if userNumber==2:
                                #alternativt om man kunde få en dropdownlista
                                weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                                print("You want to add a train subscription")
                                subscriptionTrainOwner = input("Write which train owner you want to subscribe to: ").lower()
                                while not subscriptionTrainOwner:
                                    subscriptionTrainOwner = input("Please enter the train owner: ").lower()
                                cur.execute('SELECT TrainOwnerId FROM TrainOwner where OwnerName = ?', (subscriptionTrainOwner,))
                                existingOwner = cur.fetchone()
                                if not existingOwner:
                                    print("Sorry! No train owner with that name")
                                    continue

                                while True: 
                                    subscriptionStation = input("Write which departure station you want to subscribe to: ").lower()
                                    while not subscriptionStation:
                                        subscriptionStation = input("Please enter your departure station: ").lower()
                                    cur.execute('SELECT StationId FROM Station where StationName = ?', (subscriptionStation,))
                                    existingStation = cur.fetchone()
                                    if existingStation:
                                        break
                                    if not existingStation:
                                        print("Sorry, no station found with that name.")
                                        cur.execute('SELECT StationName FROM Station where StationName LIKE ?', ("%" + subscriptionStation + "%",))
                                        similarStation = cur.fetchall()
                                        if similarStation:
                                            print(f"These stations have similiar names: {similarStation}?")
                                        
                                        
                                subscriptionDay = input("Enter the day of the week you want to subscribe to: ").lower()
                                while not subscriptionDay in weekdays:
                                    subscriptionDay = input("Please enter the day of the week: ").lower()
                                #kolla om det finns tåg som tidigare nämnt den dagen i veckan
                                
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

                                subscriptionTime = input("Enter the time of the day you want to subscribe to (in HH:MM-format): ")
                                while not format(subscriptionTime):
                                    subscriptionTime = input("Please enter the time of the day (HH:MM): ")
                                #kolla om det finns tåg som tidigare nämnt den tiden
                                
                                cur.execute('SELECT Subscription.PassengerId, Subscription.TrainOwnerId, Subscription.StationId, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.Active FROM Subscription WHERE PassengerId = ? AND TrainOwnerId = ? AND StationId = ? AND DayOfTheWeek = ? AND DepartureTime = ?', (info[0], existingOwner[0], existingStation[0], subscriptionDay, subscriptionTime))
                                existingData=cur.fetchone()

                                #om den inte alls finns
                                if existingData is None:
                                    cur.execute("INSERT OR IGNORE INTO Subscription (PassengerId, TrainOwnerId, StationId, DayOfTheWeek, DepartureTime, Active) VALUES (?, ?, ?, ?, ?, 1)", (info[0], existingOwner[0], existingStation[0], subscriptionDay, subscriptionTime))
                                    conn.commit()
                                    print(f"You are now subscribed to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock")
                                
                                
                                #om den är oaktiv
                                elif existingData and existingData[5] == 0:
                                    cur.execute('SELECT Subscription.SubscriptionId, Subscription.PassengerId, Subscription.TrainOwnerId, Subscription.StationId, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.Active FROM Subscription WHERE PassengerId = ? AND TrainOwnerId = ? AND StationId = ? AND DayOfTheWeek = ? AND DepartureTime = ? AND Active = 0', (info[0], existingOwner[0], existingStation[0], subscriptionDay, subscriptionTime))
                                    existingData=cur.fetchone()

                                
                                    if existingData:
                                        cur.execute("UPDATE Subscription SET Active = 1 WHERE SubscriptionId = ?", (existingData[0],))
                                        conn.commit()
                                        print(f"Your subscription has been reactivated to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock")
                                
                                #om den är aktiv    
                                elif existingData and existingData[5] == 1:
                                    cur.execute('SELECT Subscription.SubscriptionId, Subscription.PassengerId, Subscription.TrainOwnerId, Subscription.StationId, Subscription.DayOfTheWeek, Subscription.DepartureTime, Subscription.Active FROM Subscription WHERE PassengerId = ? AND TrainOwnerId = ? AND StationId = ? AND DayOfTheWeek = ? AND DepartureTime = ? AND Active = 1', (info[0], existingOwner[0], existingStation[0], subscriptionDay, subscriptionTime))
                                    existingData=cur.fetchone()
                                    if existingData:
                                        print(f"You are already subscribed to {subscriptionTrainOwner.capitalize()} in {subscriptionStation.capitalize()} on {subscriptionDay.capitalize()}s at {subscriptionTime} o'clock")
                                
                    

                                print("Going back...")
                                print(""" """)
                                time.sleep(3)
                            if userNumber==3:
                                conn = sqlite3.connect("train.db")
                                cur = conn.cursor()
                                print("You want to delete a train subscription")
                                try:
                                    cur.execute('SELECT SubscriptionId FROM Subscription WHERE Active = 1 AND PassengerId = ?', (info[0],))
                                    allSubscriptionsQuery=cur.fetchall()
                                    if len(allSubscriptionsQuery) == 1:
                                        cur.execute("UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?", (allSubscriptionsQuery[0][0],))
                                        print(f"Thank you! You only had one active subscription and it has now been unactivated!")
                                        conn.commit()
                                        continue 
                                except:
                                    print("No subscriptions found, returning to home screen")
                                    print(""" """)
                                    time.sleep(3)
                                    continue
                                theOwner = input("From which train owner? ")
                                cur.execute('SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ?', (info[0], theOwner))
                                ownerQuery=cur.fetchall()
                                if len(ownerQuery) == 1:
                                    cur.execute("UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?", (ownerQuery[0][0],))
                                    print(f"Thank you! Your subscription has now been unactivated!")
                                    conn.commit()
                                    continue
                                theStation = input ("From which train station? ")
                                cur.execute('SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Subscription.StationId FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ?', (info[0], theOwner, theStation))
                                departureQuery=cur.fetchall()
                                print(departureQuery)
                                if len(departureQuery) == 1:
                                    cur.execute("UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?", (departureQuery[0][0],))
                                    print(f"Thank you! Your subscription has now been unactivated!")
                                    conn.commit()
                                    continue
                                theDay = input("What day? ")
                                cur.execute('SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Station.StationName, Subscription.DayOfTheWeek FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ? AND Subscription.DayOfTheWeek = ?', (info[0], theOwner, theStation, theDay))
                                dayQuery=cur.fetchall()
                                print(dayQuery)
                                if len(dayQuery) == 1:
                                    cur.execute("UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?", (dayQuery[0][0],))
                                    print(f"Thank you! Your subscription has now been unactivated!")
                                    conn.commit()
                                    continue
                                theTime = input("Which time? ")
                                cur.execute('SELECT Subscription.SubscriptionId, TrainOwner.TrainOwnerId, TrainOwner.OwnerName, Station.StationName, Subscription.DayOfTheWeek, Subscription.DepartureTime FROM Subscription JOIN TrainOwner ON Subscription.TrainOwnerId = TrainOwner.TrainOwnerId JOIN Station ON Subscription.StationId = Station.StationId WHERE Active = 1 AND Subscription.PassengerId = ? AND TrainOwner.OwnerName = ? AND Station.StationName = ? AND Subscription.DayOfTheWeek = ? AND Subscription.DepartureTime = ?', (info[0], theOwner, theStation, theDay, theTime))
                                timeQuery=cur.fetchall()
                                if len(timeQuery) == 1:
                                    cur.execute("UPDATE Subscription SET Active = 0 WHERE SubscriptionId = ?", (timeQuery[0][0],))
                                    print(f"Thank you! Your subscription has now been unactivated!")
                                    conn.commit()
                                    continue
                                time.sleep(3)
                                print("Going back...")
                                print(""" """)
                                time.sleep(2)
                            if userNumber==4:
                                print("You want to update your information")
                                updateList=["1. Change first name", "2. Change last name", "3. Change email", "4. Change password", "5. Change phone number", "6. Deactivate account", "7. Go back"]                      
                                p=1
                                runUpdateProgram=True
                                while runUpdateProgram:
                                    for k in updateList:
                                        print(k)
                                        p=+1
                                    if p<7:
                                        False
                                    updateNumber=int(input("Choose one of the numbers above: "))
                                    while not 0<updateNumber <=7:
                                        updateNumber=int(input("Choose one of the numbers above: "))
                                    if updateNumber==1:
                                        print("You want to change your first name")
                                        updateFirstName=input("Write what you want to change it to: ").lower().title()
                                        while not updateFirstName:
                                            updateFirstName = input("Write what you want to change your first name to: ").lower().title()
                                        cur.execute("UPDATE passenger SET FirstName = ? WHERE PassengerId = ?", (updateFirstName, info[0]))
                                        print(f"Thank you! Your first name has now been updated to {updateFirstName}!")
                                        conn.commit()
                                        print("Going back to the homescreen...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                                    if updateNumber==2:
                                        print("You want to change your last name")
                                        updateLastName=input("Write what you want to change it to: ").lower().title()
                                        while not updateLastName:
                                            updateLastName = input("Write what you want to change your last name to: ").lower().title()                                
                                        cur.execute("UPDATE passenger SET LastName = ? WHERE PassengerId = ?", (updateLastName, info[0]))
                                        print(f"Thank you! Your last name has now been updated to {updateLastName}!")
                                        conn.commit()
                                        print("Going back to the homescreen...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                                    if updateNumber==3:
                                        while True:
                                            print("You want to change your email address")
                                            updateEmail=input("Write what you want to change it to: ")
                                            while not updateEmail:
                                                updateEmail = input("Write what you want to change your email address to: ").lower()
                                            cur.execute('SELECT * FROM passenger where Email = ?', (updateEmail,))
                                            existingEmail=cur.fetchone()
                                            if existingEmail:
                                                print("This email address is already in use")
                                            else: 
                                                break
                                        cur.execute("UPDATE passenger SET Email = ? WHERE PassengerId = ?", (updateEmail, info[0]))
                                        print(f"Thank you! Your email address has now been updated to {updateEmail}!")
                                        conn.commit()
                                        print("Going back to the homescreen...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                                    if updateNumber==4:
                                        print("You want to change your password")
                                        updatePassword=getpass.getpass("Write what you want to change it to: ")
                                        while not updatePassword:
                                            updatePassword = getpass.getpass("Write what you want to change your password to: ")
                                        cur.execute("UPDATE passenger SET Password = ? WHERE PassengerId = ?", (updatePassword, info[0]))
                                        print(f"Thank you! Your password has now been updated!")
                                        conn.commit()
                                        print("Going back to the homescreen...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                                    if updateNumber==5:
                                        while True:
                                            updatePhoneNumber = input("Enter your new phone number: ")
                                            while not updatePhoneNumber: 
                                                updatePhoneNumber = input("Please enter your new phone number: ")
                                            if not updatePhoneNumber.isdigit():
                                                print("Try again with numbers!")
                                                continue                                        
                                            cur.execute('SELECT * FROM passenger where PhoneNumber = ?', (updatePhoneNumber,))
                                            existingPhoneNumber = cur.fetchone()
                                            if existingPhoneNumber:
                                                print("This phone number is already in use")
                                            else:
                                                break
                                        cur.execute("UPDATE passenger SET PhoneNumber = ? WHERE PassengerId = ?", (updatePhoneNumber, info[0]))
                                        print(f"Thank you! Your phone number has now been updated to {updatePhoneNumber}!")
                                        conn.commit()
                                        print("Going back to the homescreen...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                                    if updateNumber==6:
                                        print("Going back...")
                                        print(""" """)
                                        time.sleep(1)
                                        break
                            if userNumber==5:
                                print("Logging out from user...")
                                print(""" """)
                                time.sleep(1)
                                break
                        break

            if yourPhoneNumber != info[5]:
                print("Sorry, you are not in the system yet. Please create a user.")
                print("Going back to the homescreen...")
                print(""" """)
                time.sleep(2)
        else:
            print("Sorry, you are not in the system yet. Please create a user.")
            print("Going back to the homescreen...")
            print(""" """)
            time.sleep(2)
        
    if number==3:
        print("The program is closing...")
        print("Bye!")
        time.sleep(1)
        runProgram=False
        

#om det är fler tåg som går den tiden får man ställa en kontrollfråga
#t.ex. vad som är tågets första/sista hållplats/tågLinjeNummer
#FromLocation; LocationName, ToLocation; LocationName, AdvertisedTrainIdent
#skapa en till kolumn på subscription som kan vara null där man kan välja slutstation