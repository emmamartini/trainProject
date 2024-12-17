BEGIN; 
CREATE TABLE IF NOT EXISTS TrainOwner (
    TrainOwnerId INTEGER PRIMARY KEY AUTOINCREMENT,
    OwnerName NVARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Train (
    TrainId INTEGER PRIMARY KEY AUTOINCREMENT,
    TrainOwnerId INTEGER NOT NULL,
    StationId INTEGER NOT NULL,
    EndStationId INTEGER NOT NULL,
    Canceled BOOLEAN NOT NULL,
    Delayed BOOLEAN NOT NULL,
    OriginalDepartureTime DATETIME NOT NULL,
    ActualDepartureTime DATETIME NULL,
    FOREIGN KEY (TrainOwnerId) REFERENCES TrainOwner(TrainOwnerId),
    FOREIGN KEY (StationId) REFERENCES TrainOwner(StationId),
    FOREIGN KEY (EndStationId) REFERENCES TrainOwner(StationId)
);

CREATE TABLE IF NOT EXISTS Station (
    StationId INTEGER PRIMARY KEY AUTOINCREMENT,
    StationName NVARCHAR(30) NOT NULL,
    Country NVARCHAR(30) NOT NULL,
    County NVARCHAR(30) NOT NULL,
    StationSignature NVARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS Passenger (
    PassengerId INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName NVARCHAR(30) NOT NULL,
    LastName NVARCHAR(30) NOT NULL,
    Email NVARCHAR(60) NOT NULL,
    Password NVARCHAR(255) NOT NULL,
    PhoneNumber NVARCHAR(20) NOT NULL,
    Active BOOLEAN
);

CREATE TABLE IF NOT EXISTS Subscription (
    SubscriptionId INTEGER PRIMARY KEY AUTOINCREMENT,
    PassengerId INTEGER NOT NULL,
    TrainOwnerId INTEGER NOT NULL,
    StationId INTEGER NOT NULL,
    EndStationId INTEGER NOT NULL,
    DayOfTheWeek INTEGER NOT NULL,
    DepartureTime NVARCHAR(5) NOT NULL,
    Active BOOLEAN NOT NULL,
    FOREIGN KEY (PassengerId) REFERENCES Passenger(PassengerId),
    FOREIGN KEY (TrainOwnerId) REFERENCES TrainOwner(TrainOwnerId),
    FOREIGN KEY (StationId) REFERENCES Station(StationId),
    FOREIGN KEY (EndStationId) REFERENCES Station(StationId)
);

CREATE TABLE IF NOT EXISTS MessageSent (
    MessageSentId INTEGER PRIMARY KEY AUTOINCREMENT,
    PassengerId INTEGER NOT NULL,
    TrainId INTEGER NOT NULL,
    SentAt DATETIME NOT NULL,
    Content NVARCHAR(100) NOT NULL,
    FOREIGN KEY (PassengerId) REFERENCES Passenger(PassengerId),
    FOREIGN KEY (TrainId) REFERENCES Train(TrainId)
);

CREATE TABLE IF NOT EXISTS TrainAnnouncement (
    TrainAnnouncementId INTEGER PRIMARY KEY AUTOINCREMENT,
    StationId INTEGER NOT NULL,
    EndStationId INTEGER NOT NULL,
    AdvertisedTime DATETIME NOT NULL,
    EstimatedTime DATETIME NULL,
    Status NVARCHAR(100) NOT NULL,
    FOREIGN KEY (StationId) REFERENCES Station(StationId),
    FOREIGN KEY (EndStationId) REFERENCES Station(StationId)
);
COMMIT;