import datetime
import time

#import helheim

from ME.magiceden import MagicEden
from magicden_filehandler import MagicEdenFileHandler


def main():
    me_monitor = MagicEden()
    me_fh = MagicEdenFileHandler()
    last_run_timestamp_interval_monitor = datetime.datetime.now() - datetime.timedelta(hours=1)
    print("time00: ",type((last_run_timestamp_interval_monitor + datetime.timedelta(minutes=15)).timestamp()))
    print("time15: ",type((datetime.datetime.now()).timestamp()))
    while 1:
        me_monitor.check_launchpad_releases()
        me_monitor.check_launchpad_collections()
        collection_list = me_fh.read_file()
        for collection_slug in collection_list:
            me_monitor.check_collection_by_slug(collection_slug)
            time.sleep(0.5)
        if (last_run_timestamp_interval_monitor + datetime.timedelta(minutes=15)).timestamp() < (datetime.datetime.now()).timestamp():
            print("interval monitor running")
            me_monitor.check_all_collections_in_interval(collection_list)
            last_run_timestamp_interval_monitor = datetime.datetime.now()
        else:
            print("interval monitor not ready")
        collection_names = ["quantum_traders", "solstein"]
        for collection_name in collection_names:
            try:
                new_data_response = me_monitor.scrape_new_listings_form_csv(collection_name)
                if new_data_response.get("results", None) is None:
                    continue
                me_monitor.compare_new_listings_with_csv(new_data_response)
            except Exception as e:
                print("special monitor error", e)


if __name__ == "__main__":
    #helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')
    main()
