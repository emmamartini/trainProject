from get_all_stations import create_database, get_stations, exportTrain
from get_all_train_owners import get_owners, exportOwner

if __name__ == '__main__':
    create_database()
    #train_station_list = get_stations()
    #exportTrain(train_station_list)
    train_owner_set = get_owners()
    exportOwner(train_owner_set)