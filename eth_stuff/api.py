import json
import random

import requests
from web3 import HTTPProvider, Web3
from web3.contract import Contract


class Backend:
    def __init__(self):
        self.rpc_provider = "http://89.58.6.161:8545"
        self.etherscan_api_key_list = [
            "C1NNT9HSMTTJJXTBWXWKFPHEQJ1AD5CEJT"
        ]
        self.web3 = self.load_web3_with_rpc_provider()

    def load_web3_with_rpc_provider(self) -> Web3:
        """
        Loads a web3 instance with the RPC provider from the settings file.
        :return:
        """
        if self.rpc_provider is None or self.rpc_provider == "":
            raise Exception("RPC_PROVIDER not set")
        if str(self.rpc_provider).startswith("http"):
            self.web3 = Web3(HTTPProvider(self.rpc_provider, request_kwargs={'timeout': 60}))
        elif str(self.rpc_provider).startswith("ws"):
            self.web3 = Web3(Web3.WebsocketProvider(self.rpc_provider, websocket_timeout=60))
        else:
            raise Exception("RPC_PROVIDER not valid")
        print("Connected to RPC provider:", self.web3.isConnected())
        return self.web3

    def get_contract_abi_from_etherscan(self, contract_address: str) -> list:
        """
        Gets the ABI from Etherscan.
        :param contract_address:
        :return:
        """
        ran_api_key = random.choice(self.etherscan_api_key_list)
        response = requests.get(
            url="https://api.etherscan.io/api"
                f"?module=contract"
                f"&action=getabi"
                f"&address={contract_address}"
                f"&apikey={ran_api_key}",
            headers={
                "Accept": "application/json",
                "User-Agent": "I BIMS DUDUDU"
            },
        )
        if response.status_code != 200:
            raise Exception("Could not get contract ABI from Etherscan")
        return json.loads(response.text)["result"]

    def get_checksum(self, address) -> str:
        """
        :param address:
        :return:
        """
        return self.web3.toChecksumAddress(address)

    def get_value_from_contract(self, contract: Contract, function_name: str, *args):
        """
        :param contract:
        :param function_name:
        :param args:
        :return:
        """
        return contract.functions[function_name](*args).call()

    def get_inputs_of_contract_in_function(self, contract: Contract, function_name: str):
        """
        :param contract:
        :param function_name:
        :return:
        """
        for function in contract.abi:
            if function.get("name", None) == function_name:
                found_inputs = function["inputs"]
                _inputs = [{"type": x["type"], "name": x["name"]} for x in found_inputs]
                return _inputs

    def get_outputs_of_contract_in_function(self, contract: Contract, function_name: str):
        """
        :param contract:
        :param function_name:
        :return:
        """
        for function in contract.abi:
            if function.get("name", None) == function_name:
                found_outputs = function["outputs"]
                _outputs = [{"type": x["type"], "name": x["name"]} for x in found_outputs]
                return _outputs

    def get_functions_from_contract(self, contract: Contract):
        """
        :param contract:
        :return:
        """
        # abi = contract.abi
        all_functions = []
        for func in contract.functions:
            # print(func, dir(func))
            func_name = str(func)
            inputs = self.get_inputs_of_contract_in_function(contract, func_name)
            # print(func_name, inputs)
            outputs = self.get_outputs_of_contract_in_function(contract, func_name)
            # print(func_name, outputs)
            all_functions.append({"name": func_name, "inputs": inputs, "outputs": outputs, "type": "function"})
        return all_functions

    def get_events_from_contract(self, contract: Contract):
        """
        :param contract:
        :return:
        """
        return [str(x.event_name) for x in contract.events]

    def get_contract_creator(self, contract: Contract):
        """
        :param contract:
        :return:
        """
        return self.get_value_from_contract(contract, "owner")

    def get_possible_mint_functions(self, contract_abi: list):
        """
        :param contract_abi:
        :return:
        """
        possible_mint_functions = []
        for function in contract_abi:
            if function.get("type", None) == "function" and "mint" in function.get("name", None).lower():
                possible_mint_functions.append(function.get("name", None))
        return possible_mint_functions

    def get_possible_flip_sale_functions(self, contract_abi: list):
        """
        :param contract_abi:
        :return:
        """
        possible_flip_sale_functions = []
        for function in contract_abi:
            if function.get("type", None) == "function" and \
                    ("sale" in function.get("name", None).lower() or "flip" in function.get("name", None).lower()):
                possible_flip_sale_functions.append(function.get("name", None))
        return possible_flip_sale_functions

    def get_pending_transactions_for_address(self, address: str):
        """
        :param address:
        :return:
        """
        pending_transactions = 0
        target_address = self.get_checksum(address)
        pending_block = self.web3.eth.getBlock("pending", full_transactions=True)
        for tx in pending_block["transactions"]:
            current_tx_to = self.get_checksum(tx["to"])
            if target_address == current_tx_to:
                pending_transactions += 1
        return pending_transactions


def main():
    backend = Backend()
    target_contract_address = "0x7be8076f4ea4a4ad08075c2508e481d6c946d12b"
    contract_checksum = backend.get_checksum(target_contract_address)
    pendings = backend.get_pending_transactions_for_address(contract_checksum)
    print(pendings)


# if __name__ == "__main__":
#     main()
