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
    OriginalDepartureTime DATETIME NOT NULL,
    ActualDepartureTime DATETIME NULL,
    FOREIGN KEY (TrainOwnerId) REFERENCES TrainOwner(TrainOwnerId),
    FOREIGN KEY (StationId) REFERENCES TrainOwner(StationId),
    FOREIGN KEY (EndStationId) REFERENCES TrainOwner(StationId)
);

CREATE TABLE IF NOT EXISTS Station (
    StationId INTEGER PRIMARY KEY AUTOINCREMENT,
    StationName NVARCHAR(30) NOT NULL,
    Country NVARCHAR(11) NOT NULL,
    County NVARCHAR(10) NOT NULL,
    StationSignature NVARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS Passenger (
    PassengerId INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName NVARCHAR(30) NOT NULL,
    LastName NVARCHAR(30) NOT NULL,
    Email NVARCHAR(60) NOT NULL,
    Password NVARCHAR(255) NOT NULL,
    PhoneNumber NVARCHAR(20) NOT NULL,
    Active BOOLEAN NOT NULL
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
    SubscriptionId INTEGER NOT NULL,
    SentAt DATETIME NOT NULL,
    Content NVARCHAR(100) NOT NULL,
    FOREIGN KEY (PassengerId) REFERENCES Passenger(PassengerId)
    FOREIGN KEY (SubscriptionId) REFERENCES Subscription(SubscriptionId)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_train_null_actualdeparturetime
ON Train (TrainOwnerId, StationId, EndStationId, Canceled, OriginalDepartureTime, ActualDepartureTime)
WHERE ActualDepartureTime IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_train_nonnull_actualdeparturetime
ON Train (TrainOwnerId, StationId, EndStationId, Canceled, OriginalDepartureTime)
WHERE ActualDepartureTime IS NULL;

COMMIT;