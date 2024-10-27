from get_all_stations import create_database, get_stations, exportTrain

if __name__ == '__main__':
    create_database()
    train_station_list = get_stations()
    exportTrain(train_station_list)