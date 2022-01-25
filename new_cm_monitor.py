import time

from get_all_cm import get_all_cm, read_all_cm_from_file, compare_for_new_cm, write_all_cm_to_file
from webhook import send_discord_webhook
from get_cm_metadata import get_metadata_of_cm, save_metadata_to_file
from cms_nft import get_cms_nft, cms_nfts_to_file, get_data_of_uri


def main():
    while 1:
        all_cm_new = get_all_cm()
        # print("all_cm_new:", all_cm_new)
        all_cm_old = read_all_cm_from_file()
        # print("all_cm_old:", all_cm_old)
        if all_cm_old is None:
            write_all_cm_to_file(all_cm_new)
        new_cm_list = compare_for_new_cm(all_cm_new, all_cm_old)  # ??? error when all_old_cm doesnt exist yet
        print("new_cm_list:", len(new_cm_list))
        #when running first time run this to prevent error
        write_all_cm_to_file(all_cm_new)
        for new_cm in new_cm_list:
            metadata = get_metadata_of_cm(new_cm[0], new_cm[2])
            if metadata is None:
                continue
            save_metadata_to_file(metadata)
            cms_nfts = get_cms_nft(metadata["candy_machine_id"], new_cm[2])
            if cms_nfts is None:
                continue
            cms_nfts_to_file(cms_nfts, metadata["candy_machine_id"])
            nft_name = "not found"
            if cms_nfts:
                try:
                    nft_name = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["name"]
                    nft_uri = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["uri"]
                except:
                    nft_name = cms_nfts["all_nfts"][0]["name"]
                    nft_uri = cms_nfts["all_nfts"][0]["uri"]
                image, description = get_data_of_uri(nft_uri)
            else:
                image, description = None, None
            send_discord_webhook(new_cm[0], new_cm[1], metadata, nft_name, image, description)
        write_all_cm_to_file(all_cm_new)
        print("will sleep ")
        time.sleep(30)
        print("sleep end")


if __name__ == '__main__':
    main()

