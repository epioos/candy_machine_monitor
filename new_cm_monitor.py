from get_all_cm import get_all_cm, read_all_cm_from_file, compare_for_new_cm, write_all_cm_to_file
from webhook import send_discord_webhook
from get_cm_metadata import get_metadata_of_cm, save_metadata_to_file
from cms_nft import get_cms_nft, cms_nfts_to_file, get_data_of_uri

def main():
    all_cm_new = get_all_cm()
    all_cm_old = read_all_cm_from_file()
    new_cm_list = compare_for_new_cm(all_cm_new, all_cm_old)
    print(new_cm_list)
    print(len(new_cm_list))
    for new_cm in new_cm_list:
        metadata = get_metadata_of_cm(new_cm[0], new_cm[2])
        if metadata is None:
            continue
        save_metadata_to_file(metadata)
        cms_nfts = get_cms_nft(metadata["candy_machine_id"],new_cm[2])
        cms_nfts_to_file(cms_nfts, metadata["candy_machine_id"])
        nft_name = "not found"
        if cms_nfts != []:
            nft_name = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["name"]
            nft_uri = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["uri"]
            image, description = get_data_of_uri(nft_uri)
        else:
            image, description = None, None
        send_discord_webhook(new_cm[0],new_cm[1], metadata, nft_name, image, description)
    write_all_cm_to_file(all_cm_new)




if __name__ == '__main__':
    main()
