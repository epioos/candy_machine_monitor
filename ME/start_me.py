import helheim

from ME.magiceden import MagicEden
from magicden_filehandler import MagicEdenFileHandler


def main():
    me_monitor = MagicEden()
    me_fh = MagicEdenFileHandler()
    while 1:
        me_monitor.check_launchpad_releases()
        me_monitor.check_launchpad_collections()
        for collection_slug in me_fh.read_file():
            me_monitor.check_collection_by_slug(collection_slug)


if __name__ == "__main__":
    helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')
    main()
