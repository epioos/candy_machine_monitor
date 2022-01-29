import json
import os

from theblockchainapi import TheBlockchainAPIResource, SolanaNetwork, SolanaCandyMachineContractVersion

from settings import API_ID_KEY, API_SECRET_KEY

BLOCKCHAIN_API_RESOURCE = TheBlockchainAPIResource(
    api_key_id=API_ID_KEY,
    api_secret_key=API_SECRET_KEY
)


def get_metadata_of_cm(cm_address, version):
    try:
        assert API_ID_KEY is not None
        assert API_SECRET_KEY is not None
    except AssertionError:
        raise Exception("Api key pair not found")

    try:
        versions = {
            "v1": SolanaCandyMachineContractVersion.V1,
            "v2": SolanaCandyMachineContractVersion.V2
        }

        candy_machine_id = cm_address
        try:
            metadata = BLOCKCHAIN_API_RESOURCE.get_candy_machine_metadata(
                config_address=candy_machine_id,
                network=SolanaNetwork.MAINNET_BETA,
                candy_machine_contract_version=versions[version]
            )
            #print("metadata response", type(metadata), metadata)
        except Exception as e:
            print("error getting cm metadata", e)
            return None
        else:
            if "candy_machine_id" not in metadata:
                return None
            return metadata
    except:
        return None


def save_metadata_to_file(metadata):
    try:
        os.mkdir("./metadata/")
    except:
        pass
    try:
        with open(f"./metadata/{metadata['candy_machine_id']}.json", "w") as file:
            json.dump(metadata, file)
    except Exception as e:
        print("error saving metadata to file", e)
