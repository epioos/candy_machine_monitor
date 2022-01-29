import time

import helheim

from ME.magiceden import MagicEden
from magicden_filehandler import MagicEdenFileHandler


def main():
    me_monitor = MagicEden()
    me_fh = MagicEdenFileHandler()
    last_run_timestamp_interval_monitor = 0
    while 1:
        me_monitor.check_launchpad_releases()
        me_monitor.check_launchpad_collections()
        collection_list = me_fh.read_file()
        for collection_slug in collection_list:
            me_monitor.check_collection_by_slug(collection_slug)
            time.sleep(0.5)
        if last_run_timestamp_interval_monitor < int(time.time() + int(60 * 15)):
            print("interval monitor running")
            me_monitor.check_all_collections_in_interval(collection_list)
            last_run_timestamp_interval_monitor = time.time()
        else:
            print("interval monitor not ready")


if __name__ == "__main__":
    helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')
    main()
