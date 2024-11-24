from create_database import create_database
from get_all_stations import get_stations, exportTrain
from get_all_train_owners import get_owners, exportOwner

if __name__ == '__main__':
    create_database()
    train_station_list = get_stations()
    exportTrain(train_station_list)
    train_owner_set = get_owners()
    exportOwner(train_owner_set)
    
    
#alla tåg som prenumereras på och som gått/blivit inställda under dagen skrivs in databasen i slutet av dagen!