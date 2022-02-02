import datetime
import io
import json
import os
import random
import ssl
import string
import time
import urllib
from threading import Thread
from urllib.request import urlopen

from colorthief import ColorThief
from discord_webhook import DiscordWebhook, DiscordEmbed

from ProxyManager import get_random_proxy
from floor_monitor import start_checker
from http_client import Client
from storage import c_list, url_list, webhooks, skip_webhook
import cloudscraper
import helheim


class OpenSea:
    def __init__(self):
        self.skip_webhook = False
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'mobile': False,
                'platform': 'windows'
            },
            requestPostHook=self.injection,
            captcha={
                'provider': 'vanaheim'
            },
            debug=True
        )
        current_path = os.path.dirname(os.path.realpath(__file__))
        bifrost_file = os.path.join(current_path, "bifrost-0.0.4.1-windows.x86_64.dll")

        self.client.adapters['https://'].ssl_context.check_hostname = False
        self.client.adapters['https://'].ssl_context.verify_mode = ssl.CERT_NONE
        #helheim.wokou(self.client, "chrome")
        self.client.bifrost_clientHello = 'chrome'
        helheim.bifrost(self.client, "./bifrost-0.0.4.1-windows.x86_64.dll")
        self.rotate_proxy()

    def rotate_proxy(self):
        try:
            new_proxy = get_random_proxy()
            self.client.proxies = new_proxy
        except:
            self.client.proxies = None
        print("rotated proxy", self.client.proxies)
        try:
            self.client.cookies.clear()
        except:
            pass

    def injection(self, session, response):
        if helheim.isChallenge(session, response):
            # solve(session, response, max_tries=5)
            return helheim.solve(session, response)
        else:
            return response

    def gen_ran_str(self, length=31):
        return ''.join(
            random.choice(string.digits + string.ascii_lowercase) for _ in range(length))

    def get_collection(self, slug):
        headers = {
            'authority': 'api.opensea.io',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'x-build-id': 'EsUCZqBbKZKmzfMmJDPT8',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'x-signed-query': self.gen_ran_str(64),
            'x-api-key': '2f6f419a083c46de9d83ce3dbe7db601',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://opensea.io',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://opensea.io/',
            'accept-language': 'de-DE,de;q=0.9',
        }

        data = {
            '{"id":"AssetSearchQuery","query":"query AssetSearchQuery(\\n  $categories: [CollectionSlug!]\\n  $chains: [ChainScalar!]\\n  $collection: CollectionSlug\\n  $collectionQuery: String\\n  $collectionSortBy: CollectionSort\\n  $collections: [CollectionSlug!]\\n  $count: Int\\n  $cursor: String\\n  $identity: IdentityInputType\\n  $includeHiddenCollections: Boolean\\n  $numericTraits: [TraitRangeType!]\\n  $paymentAssets: [PaymentAssetSymbol!]\\n  $priceFilter: PriceFilterType\\n  $query: String\\n  $resultModel: SearchResultModel\\n  $showContextMenu: Boolean ': ' false\\n  $shouldShowQuantity: Boolean = false\\n  $sortAscending: Boolean\\n  $sortBy: SearchSortBy\\n  $stringTraits: [TraitInputType!]\\n  $toggles: [SearchToggle!]\\n  $creator: IdentityInputType\\n  $assetOwner: IdentityInputType\\n  $isPrivate: Boolean\\n  $safelistRequestStatuses: [SafelistRequestStatus!]\\n) {\\n  query {\\n    ...AssetSearch_data_2hBjZ1\\n  }\\n}\\n\\nfragment AssetCardAnnotations_assetBundle on AssetBundleType {\\n  assetCount\\n}\\n\\nfragment AssetCardAnnotations_asset_3Aax2O on AssetType {\\n  assetContract {\\n    chain\\n    id\\n  }\\n  decimals\\n  ownedQuantity(identity: $identity) @include(if: $shouldShowQuantity)\\n  relayId\\n  favoritesCount\\n  isDelisted\\n  isFavorite\\n  isFrozen\\n  hasUnlockableContent\\n  ...AssetCardBuyNow_data\\n  orderData {\\n    bestAsk {\\n      orderType\\n      relayId\\n      maker {\\n        address\\n      }\\n    }\\n  }\\n  ...AssetContextMenu_data_3z4lq0 @include(if: $showContextMenu)\\n}\\n\\nfragment AssetCardBuyNow_data on AssetType {\\n  tokenId\\n  relayId\\n  assetContract {\\n    address\\n    chain\\n    id\\n  }\\n  collection {\\n    slug\\n    id\\n  }\\n  orderData {\\n    bestAsk {\\n      relayId\\n    }\\n  }\\n}\\n\\nfragment AssetCardContent_asset on AssetType {\\n  relayId\\n  name\\n  ...AssetMedia_asset\\n  assetContract {\\n    address\\n    chain\\n    openseaVersion\\n    id\\n  }\\n  tokenId\\n  collection {\\n    slug\\n    id\\n  }\\n  isDelisted\\n}\\n\\nfragment AssetCardContent_assetBundle on AssetBundleType {\\n  assetQuantities(first: 18) {\\n    edges {\\n      node {\\n        asset {\\n          relayId\\n          ...AssetMedia_asset\\n          id\\n        }\\n        id\\n      }\\n    }\\n  }\\n}\\n\\nfragment AssetCardFooter_assetBundle on AssetBundleType {\\n  ...AssetCardAnnotations_assetBundle\\n  name\\n  assetCount\\n  assetQuantities(first: 18) {\\n    edges {\\n      node {\\n        asset {\\n          collection {\\n            name\\n            relayId\\n            slug\\n            isVerified\\n            ...collection_url\\n            id\\n          }\\n          id\\n        }\\n        id\\n      }\\n    }\\n  }\\n  assetEventData {\\n    lastSale {\\n      unitPriceQuantity {\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n  }\\n  orderData {\\n    bestBid {\\n      orderType\\n      paymentAssetQuantity {\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n    bestAsk {\\n      closedAt\\n      orderType\\n      dutchAuctionFinalPrice\\n      openedAt\\n      priceFnEndedAt\\n      quantity\\n      decimals\\n      paymentAssetQuantity {\\n        quantity\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n  }\\n}\\n\\nfragment AssetCardFooter_asset_3Aax2O on AssetType {\\n  ...AssetCardAnnotations_asset_3Aax2O\\n  name\\n  tokenId\\n  collection {\\n    slug\\n    name\\n    isVerified\\n    ...collection_url\\n    id\\n  }\\n  isDelisted\\n  assetContract {\\n    address\\n    chain\\n    openseaVersion\\n    id\\n  }\\n  assetEventData {\\n    lastSale {\\n      unitPriceQuantity {\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n  }\\n  orderData {\\n    bestBid {\\n      orderType\\n      paymentAssetQuantity {\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n    bestAsk {\\n      closedAt\\n      orderType\\n      dutchAuctionFinalPrice\\n      openedAt\\n      priceFnEndedAt\\n      quantity\\n      decimals\\n      paymentAssetQuantity {\\n        quantity\\n        ...AssetQuantity_data\\n        id\\n      }\\n    }\\n  }\\n}\\n\\nfragment AssetContextMenu_data_3z4lq0 on AssetType {\\n  ...asset_edit_url\\n  ...asset_url\\n  ...itemEvents_data\\n  relayId\\n  isDelisted\\n  isEditable {\\n    value\\n    reason\\n  }\\n  isListable\\n  ownership(identity: {}) {\\n    isPrivate\\n    quantity\\n  }\\n  creator {\\n    address\\n    id\\n  }\\n  collection {\\n    isAuthorizedEditor\\n    id\\n  }\\n  imageUrl\\n  ownedQuantity(identity: {})\\n}\\n\\nfragment AssetMedia_asset on AssetType {\\n  animationUrl\\n  backgroundColor\\n  collection {\\n    displayData {\\n      cardDisplayStyle\\n    }\\n    id\\n  }\\n  isDelisted\\n  imageUrl\\n  displayImageUrl\\n}\\n\\nfragment AssetQuantity_data on AssetQuantityType {\\n  asset {\\n    ...Price_data\\n    id\\n  }\\n  quantity\\n}\\n\\nfragment AssetSearchFilter_data_3KTzFc on Query {\\n  ...CollectionFilter_data_2qccfC\\n  collection(collection: $collection) {\\n    numericTraits {\\n      key\\n      value {\\n        max\\n        min\\n      }\\n      ...NumericTraitFilter_data\\n    }\\n    stringTraits {\\n      key\\n      ...StringTraitFilter_data\\n    }\\n    id\\n  }\\n  ...PaymentFilter_data_2YoIWt\\n}\\n\\nfragment AssetSearchList_data_3Aax2O on SearchResultType {\\n  asset {\\n    assetContract {\\n      address\\n      chain\\n      id\\n    }\\n    collection {\\n      isVerified\\n      relayId\\n      id\\n    }\\n    relayId\\n    tokenId\\n    ...AssetSelectionItem_data\\n    ...asset_url\\n    id\\n  }\\n  assetBundle {\\n    relayId\\n    id\\n  }\\n  ...Asset_data_3Aax2O\\n}\\n\\nfragment AssetSearch_data_2hBjZ1 on Query {\\n  ...AssetSearchFilter_data_3KTzFc\\n  ...SearchPills_data_2Kg4Sq\\n  search(after: $cursor, chains: $chains, categories: $categories, collections: $collections, first: $count, identity: $identity, numericTraits: $numericTraits, paymentAssets: $paymentAssets, priceFilter: $priceFilter, querystring: $query, resultType: $resultModel, sortAscending: $sortAscending, sortBy: $sortBy, stringTraits: $stringTraits, toggles: $toggles, creator: $creator, isPrivate: $isPrivate, safelistRequestStatuses: $safelistRequestStatuses) {\\n    edges {\\n      node {\\n        ...AssetSearchList_data_3Aax2O\\n        __typename\\n      }\\n      cursor\\n    }\\n    totalCount\\n    pageInfo {\\n      endCursor\\n      hasNextPage\\n    }\\n  }\\n}\\n\\nfragment AssetSelectionItem_data on AssetType {\\n  backgroundColor\\n  collection {\\n    displayData {\\n      cardDisplayStyle\\n    }\\n    imageUrl\\n    id\\n  }\\n  imageUrl\\n  name\\n  relayId\\n}\\n\\nfragment Asset_data_3Aax2O on SearchResultType {\\n  asset {\\n    relayId\\n    isDelisted\\n    ...AssetCardContent_asset\\n    ...AssetCardFooter_asset_3Aax2O\\n    ...AssetMedia_asset\\n    ...asset_url\\n    ...itemEvents_data\\n    orderData {\\n      bestAsk {\\n        paymentAssetQuantity {\\n          quantityInEth\\n          id\\n        }\\n      }\\n    }\\n    id\\n  }\\n  assetBundle {\\n    relayId\\n    ...bundle_url\\n    ...AssetCardContent_assetBundle\\n    ...AssetCardFooter_assetBundle\\n    orderData {\\n      bestAsk {\\n        paymentAssetQuantity {\\n          quantityInEth\\n          id\\n        }\\n      }\\n    }\\n    id\\n  }\\n}\\n\\nfragment CollectionFilter_data_2qccfC on Query {\\n  selectedCollections: collections(first: 25, collections: $collections, includeHidden: true) {\\n    edges {\\n      node {\\n        assetCount\\n        imageUrl\\n        name\\n        slug\\n        isVerified\\n        id\\n      }\\n    }\\n  }\\n  collections(assetOwner: $assetOwner, assetCreator: $creator, onlyPrivateAssets: $isPrivate, chains: $chains, first: 100, includeHidden: $includeHiddenCollections, parents: $categories, query: $collectionQuery, sortBy: $collectionSortBy) {\\n    edges {\\n      node {\\n        assetCount\\n        imageUrl\\n        name\\n        slug\\n        isVerified\\n        id\\n        __typename\\n      }\\n      cursor\\n    }\\n    pageInfo {\\n      endCursor\\n      hasNextPage\\n    }\\n  }\\n}\\n\\nfragment CollectionModalContent_data on CollectionType {\\n  description\\n  imageUrl\\n  name\\n  slug\\n}\\n\\nfragment NumericTraitFilter_data on NumericTraitTypePair {\\n  key\\n  value {\\n    max\\n    min\\n  }\\n}\\n\\nfragment PaymentFilter_data_2YoIWt on Query {\\n  paymentAssets(first: 10) {\\n    edges {\\n      node {\\n        symbol\\n        relayId\\n        id\\n        __typename\\n      }\\n      cursor\\n    }\\n    pageInfo {\\n      endCursor\\n      hasNextPage\\n    }\\n  }\\n  PaymentFilter_collection: collection(collection: $collection) {\\n    paymentAssets {\\n      symbol\\n      relayId\\n      id\\n    }\\n    id\\n  }\\n}\\n\\nfragment Price_data on AssetType {\\n  decimals\\n  imageUrl\\n  symbol\\n  usdSpotPrice\\n  assetContract {\\n    blockExplorerLink\\n    chain\\n    id\\n  }\\n}\\n\\nfragment SearchPills_data_2Kg4Sq on Query {\\n  selectedCollections: collections(first: 25, collections: $collections, includeHidden: true) {\\n    edges {\\n      node {\\n        imageUrl\\n        name\\n        slug\\n        ...CollectionModalContent_data\\n        id\\n      }\\n    }\\n  }\\n}\\n\\nfragment StringTraitFilter_data on StringTraitType {\\n  counts {\\n    count\\n    value\\n  }\\n  key\\n}\\n\\nfragment asset_edit_url on AssetType {\\n  assetContract {\\n    address\\n    chain\\n    id\\n  }\\n  tokenId\\n  collection {\\n    slug\\n    id\\n  }\\n}\\n\\nfragment asset_url on AssetType {\\n  assetContract {\\n    address\\n    chain\\n    id\\n  }\\n  tokenId\\n}\\n\\nfragment bundle_url on AssetBundleType {\\n  slug\\n}\\n\\nfragment collection_url on CollectionType {\\n  slug\\n}\\n\\nfragment itemEvents_data on AssetType {\\n  assetContract {\\n    address\\n    chain\\n    id\\n  }\\n  tokenId\\n}\\n","variables":{"categories":null,"chains":null,"collection":"creepz-shapeshifterz","collectionQuery":null,"collectionSortBy":null,"collections":["creepz-shapeshifterz"],"count":32,"cursor":"YXJyYXljb25uZWN0aW9uOjMx","identity":null,"includeHiddenCollections":null,"numericTraits":null,"paymentAssets":null,"priceFilter":null,"query":null,"resultModel":"ASSETS","showContextMenu":true,"shouldShowQuantity":false,"sortAscending":true,"sortBy":"PRICE","stringTraits":null,"toggles":null,"creator":null,"assetOwner":null,"isPrivate":null,"safelistRequestStatuses":null}}'
        }

        response = self.client.post(
            url='https://api.opensea.io/graphql/',
            headers=headers,
            data=data
        )
        print(datetime.datetime.now(), "get_collection", slug, response.status_code, response.reason,
              response.elapsed.total_seconds(), )
        if response.status_code == 400:
            print(response.text)
        creations = []
        if response.status_code != 200:
            # self.client.rotate_proxy(new_proxy=get_random_proxy()["http"])
            print(response.text)
            self.rotate_proxy()
            return creations
        for x in response.json()["data"]["query"]["search"]["edges"]:
            # print(json.dumps(x))
            creation = self.asset_to_dict(x)
            creations.append(creation)
        print(len(creations), "creations found")
        print(creation)
        return creations

    def asset_to_dict(self, asset):
        asset = asset["node"]["asset"]
        # print("checking asset", asset)
        item = {
            "collectionAddress": asset["assetContract"]["address"],
            "token_id": asset['tokenId'],
            "collection": {
                "image": asset["collection"]["imageUrl"],
                "url": f"https://opensea.io/collection/{asset['collection']['slug']}",
                "name": asset['collection']['name']
            },
            "item": {
                "url": f"https://opensea.io/assets/{asset['assetContract']['address']}/{asset['tokenId']}",
                "image": asset["displayImageUrl"],
                "name": asset["name"] if asset[
                                             "name"] is not None else f"{asset['collection']['name']} {asset['tokenId']}",
                "isListable": asset["isListable"],
                "favoritesCount": asset["favoritesCount"],
                "hasUnlockableContent": asset["hasUnlockableContent"],
                "isFrozen": asset["isFrozen"],
                "bestAsk": {
                    "crypto": None,
                    "amount": None
                },
                "bestBid": {
                    "crypto": None,
                    "amount": None
                }
            }
        }

        try:
            spotPrice = asset["orderData"]["bestAsk"]["paymentAssetQuantity"]["asset"]["usdSpotPrice"]
            decimals = asset["orderData"]["bestAsk"]["paymentAssetQuantity"]["asset"]["decimals"]
            bestOffer = int(asset["orderData"]["bestAsk"]["paymentAssetQuantity"]["quantity"])
            _ = 10 ** decimals
            symbol = asset["orderData"]["bestAsk"]["paymentAssetQuantity"]["asset"]["symbol"]
            ask = float(bestOffer / _).__round__(6)
            realOffer = f"{ask} {symbol}"
            # print("bestAsk", realOffer)
            item["item"]["bestAsk"] = {
                "crypto": realOffer,
                "amount": None
            }
            usdPrice = float(ask * spotPrice).__round__(2)
            # print("usdPrice", usdPrice)
            if symbol in ["ETH", "WETH"]:
                item["item"]["bestAsk"]["amount"] = f"{usdPrice} USD"
        except Exception as e:
            # print("bestAsk error", e.__class__.__name__, e, asset["orderData"]["bestAsk"])
            pass

        try:
            spotPrice = asset["orderData"]["bestBid"]["paymentAssetQuantity"]["asset"]["usdSpotPrice"]
            decimals = asset["orderData"]["bestBid"]["paymentAssetQuantity"]["asset"]["decimals"]
            bestOffer = int(asset["orderData"]["bestBid"]["paymentAssetQuantity"]["quantity"])
            _ = 10 ** decimals
            symbol = asset["orderData"]["bestBid"]["paymentAssetQuantity"]["asset"]["symbol"]
            bid = float(bestOffer / _).__round__(6)
            realOffer = f"{bid} {symbol}"
            # print("bestBid", realOffer)
            item["item"]["bestBid"] = {
                "crypto": realOffer,
                "amount": None
            }
            usdPrice = float(bid * spotPrice).__round__(2)
            # print("usdPrice", usdPrice)
            if symbol in ["ETH", "WETH"]:
                item["item"]["bestBid"]["amount"] = f"{usdPrice} USD"
        except Exception as e:
            # print("bestBid error", e.__class__.__name__, e, asset["orderData"]["bestBid"])
            pass
        # print("item", item)
        return item

    def get_sales(self, collection_address, token_id):
        data = {
            "id": "EventHistoryQuery",
            "query": "query EventHistoryQuery(\n  $archetype: ArchetypeInputType\n  $bundle: BundleSlug\n  $collections: [CollectionSlug!]\n  $categories: [CollectionSlug!]\n  $chains: [ChainScalar!]\n  $eventTypes: [EventType!]\n  $cursor: String\n  $count: Int = 10\n  $showAll: Boolean = false\n  $identity: IdentityInputType\n) {\n  ...EventHistory_data_L1XK6\n}\n\nfragment AccountLink_data on AccountType {\n  address\n  config\n  user {\n    publicUsername\n    id\n  }\n  metadata {\n    discordUsername\n    id\n  }\n  ...ProfileImage_data\n  ...wallet_accountKey\n  ...accounts_url\n}\n\nfragment AssetCell_asset on AssetType {\n  collection {\n    name\n    id\n  }\n  name\n  ...AssetMedia_asset\n  ...asset_url\n}\n\nfragment AssetCell_assetBundle on AssetBundleType {\n  assetQuantities(first: 2) {\n    edges {\n      node {\n        asset {\n          collection {\n            name\n            id\n          }\n          name\n          ...AssetMedia_asset\n          ...asset_url\n          id\n        }\n        relayId\n        id\n      }\n    }\n  }\n  name\n  slug\n}\n\nfragment AssetMedia_asset on AssetType {\n  animationUrl\n  backgroundColor\n  collection {\n    displayData {\n      cardDisplayStyle\n    }\n    id\n  }\n  isDelisted\n  displayImageUrl\n}\n\nfragment AssetQuantity_data on AssetQuantityType {\n  asset {\n    ...Price_data\n    id\n  }\n  quantity\n}\n\nfragment EventHistory_data_L1XK6 on Query {\n  assetEvents(after: $cursor, bundle: $bundle, archetype: $archetype, first: $count, categories: $categories, collections: $collections, chains: $chains, eventTypes: $eventTypes, identity: $identity, includeHidden: true) {\n    edges {\n      node {\n        assetBundle @include(if: $showAll) {\n          ...AssetCell_assetBundle\n          id\n        }\n        assetQuantity {\n          asset @include(if: $showAll) {\n            ...AssetCell_asset\n            id\n          }\n          ...quantity_data\n          id\n        }\n        relayId\n        eventTimestamp\n        eventType\n        offerExpired\n        customEventName\n        devFee {\n          asset {\n            assetContract {\n              chain\n              id\n            }\n            id\n          }\n          quantity\n          ...AssetQuantity_data\n          id\n        }\n        devFeePaymentEvent {\n          ...EventTimestamp_data\n          id\n        }\n        fromAccount {\n          address\n          ...AccountLink_data\n          id\n        }\n        price {\n          quantity\n          ...AssetQuantity_data\n          id\n        }\n        endingPrice {\n          quantity\n          ...AssetQuantity_data\n          id\n        }\n        seller {\n          ...AccountLink_data\n          id\n        }\n        toAccount {\n          ...AccountLink_data\n          id\n        }\n        winnerAccount {\n          ...AccountLink_data\n          id\n        }\n        ...EventTimestamp_data\n        id\n        __typename\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment EventTimestamp_data on AssetEventType {\n  eventTimestamp\n  transaction {\n    blockExplorerLink\n    id\n  }\n}\n\nfragment Price_data on AssetType {\n  decimals\n  imageUrl\n  symbol\n  usdSpotPrice\n  assetContract {\n    blockExplorerLink\n    chain\n    id\n  }\n}\n\nfragment ProfileImage_data on AccountType {\n  imageUrl\n  address\n}\n\nfragment accounts_url on AccountType {\n  address\n  user {\n    publicUsername\n    id\n  }\n}\n\nfragment asset_url on AssetType {\n  assetContract {\n    address\n    chain\n    id\n  }\n  tokenId\n}\n\nfragment quantity_data on AssetQuantityType {\n  asset {\n    decimals\n    id\n  }\n  quantity\n}\n\nfragment wallet_accountKey on AccountType {\n  address\n}\n",
            "variables": {
                "archetype": {
                    "assetContractAddress": collection_address,
                    "tokenId": token_id
                },
                "bundle": None,
                "collections": None,
                "categories": None,
                "chains": None,
                "eventTypes": [
                    "AUCTION_SUCCESSFUL",
                ],
                "cursor": f"{self.gen_ran_str(31)}=",
                "count": 10,
                "showAll": False,
                "identity": None
            }
        }

        headers = {
            'authority': 'api.opensea.io',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': '*/*',
            'x-build-id': '8RY8xtt5ElacDG7ZtQLNB',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
            'content-type': 'application/json',
            'origin': 'https://opensea.io',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://opensea.io/',
            'accept-language': 'de-DE,de;q=0.9',
        }

        response = self.client.request(
            method="POST",
            url='https://api.opensea.io/graphql/',
            headers=headers,
            data=json.dumps(data)
        )
        sales = []
        print(datetime.datetime.now(), "get_sales", collection_address, response.status_code, response.reason,
              response.elapsed.total_seconds())
        if response.status_code != 200:
            # self.client.rotate_proxy(new_proxy=get_random_proxy()["http"])
            self.rotate_proxy()
            return sales
        edges = response.json()["data"]["assetEvents"]["edges"]
        for x in edges:
            sale = x["node"]
            # print("checking sale", json.dumps(sale))
            sale_json = self.sale_to_json(sale)
            sales.append(sale_json)
        print(len(sales), "sales found")
        return sales

    def sale_to_json(self, sale):
        s = {
            "eventTimestamp": sale["eventTimestamp"],
            "eventType": sale["eventType"],
            "offerExpired": sale["offerExpired"],
            # "collectionName": sale["assetQuantity"]["asset"]["collection"]["name"],
            # "item": {
            #    "name": None if "name" not in sale["assetQuantity"]["asset"] else sale["assetQuantity"]["asset"]["name"],
            #    "image": None if "displayImageUrl" not in sale["assetQuantity"]["asset"] else sale["assetQuantity"]["asset"]["displayImageUrl"]
            # },
            "price": {
                "crypto": None,
                "amount": None
            },
            "seller": {
                "address": None,
                "name": None
            },
            "winnerAccount": {
                "address": None,
                "name": None,
            },
            "blockExplorerLink": sale["transaction"]["blockExplorerLink"],
        }
        if sale["seller"] is not None:
            sellerAddress = sale["seller"]["address"]
            sellerName = "not found" if sale["seller"]["user"] is None else sale["seller"]["user"]["publicUsername"]
            s["seller"]["address"] = sellerAddress
            s["seller"]["name"] = sellerName
            # print("seller", sellerAddress, sellerName)
        if sale["winnerAccount"] is not None:
            buyerAddress = sale["winnerAccount"]["address"]
            buyerName = sale["winnerAccount"]["user"]["publicUsername"]
            s["winnerAccount"]["address"] = buyerAddress
            s["winnerAccount"]["name"] = buyerName
            # print("buyer", buyerAddress, buyerName)

        try:
            spotPrice = sale["price"]["asset"]["usdSpotPrice"]
            decimals = sale["price"]["asset"]["decimals"]
            bestOffer = int(sale["price"]["quantity"])
            _ = 10 ** decimals
            symbol = sale["price"]["asset"]["symbol"]
            bid = float(bestOffer / _).__round__(6)
            realOffer = f"{bid} {symbol}"
            # print("sale price", realOffer)
            s["price"] = {
                "crypto": realOffer,
                "amount": None
            }
            usdPrice = float(bid * spotPrice).__round__(2)
            # print("usdPrice", usdPrice)
            if symbol in ["ETH", "WETH"]:
                s["price"]["amount"] = f"{usdPrice} USD"
        except Exception as e:
            # print("bestBid error", e.__class__.__name__, e, asset["orderData"]["bestBid"])
            pass
        s["id"] = f"{s['seller']['address']}_{s['winnerAccount']['address']}"
        # print("sale", s)
        return s

    def send_sale_webhook(self, creation, sale, notification="new sale found"):
        if skip_webhook is True:
            return
        for wb in webhooks:
            sales_tracker_webhook = wb["sales_tracker_webhook"]
            if sales_tracker_webhook is None:
                continue
            username = wb["username"]
            footer_icon = wb["footer_icon"]
            footer_text = wb["footer_text"]
            avatar_url = wb["avatar_url"]
            item = creation.get("item")
            collection = creation.get("collection")
            webhook = DiscordWebhook(
                url=sales_tracker_webhook,
                proxies=get_random_proxy(),
                username=username,
                avatar_url=avatar_url
            )
            r_num = lambda: random.randint(0, 255)
            r_color = '0x%02X%02X%02X' % self.get_color_from_image(item.get("image"))  # % (r_num(), r_num(), r_num())
            embed = DiscordEmbed(title=f"{notification} - {item.get('name').title()}", color=r_color)
            embed.url = item.get("url")
            embed.set_author(name=f"{collection.get('name')}", url=collection.get("url"),
                             icon_url=collection.get("image"))
            embed.set_image(url=item.get("image"))
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon
            )
            embed.set_timestamp()
            price = sale.get("price")
            priceCrypto = price.get("crypto")
            priceUsdPrice = price.get("amount")
            if priceCrypto is not None:
                embed.add_embed_field(name="price", value=f'`{priceCrypto} / {priceUsdPrice}`', inline=False)
            buyer = sale.get("winnerAccount")
            embed.add_embed_field(name="buyer",
                                  value=f'[{buyer.get("name")}](https://etherscan.io/address/{buyer.get("address")})',
                                  inline=False)
            seller = sale.get("seller")
            embed.add_embed_field(name="seller",
                                  value=f'[{seller.get("name")}](https://etherscan.io/address/{seller.get("address")})',
                                  inline=False)
            embed.add_embed_field(name="when", value="Not found" if sale.get("eventTimestamp") is None else sale.get(
                "eventTimestamp").replace("T", " "), inline=False)
            embed.add_embed_field(name="etherscan", value=f"[link]({sale.get('blockExplorerLink')})", inline=False)
            # embed.add_embed_field(name='Field 2', value='dolor sit')
            webhook.add_embed(embed)
            # webhook.set_content(f"||@everyone||")
            r = 429
            while r == 429:
                try:
                    response = webhook.execute()
                    r = response.status_code
                    if r not in range(200, 300):
                        time.sleep(response.json()["retry_after"] // 1000)
                        raise Exception("not successfully sent")
                except Exception as e:
                    print("webhook error", e.__class__.__name__, e)
                    time.sleep(5)

    def get_color_from_image(self, url):
        try:
            proxy_support = urllib.request.ProxyHandler(get_random_proxy())
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)

            with urllib.request.urlopen(url) as response:
                # fd = a.urlopen(url=url)
                bla = response.read()
                # print(type(bla), len(bla), bla)
                f = io.BytesIO(bla)
                color_thief = ColorThief(f)
                c = color_thief.get_color(quality=1)
            # print("color", c)
            return c
        except:
            r_num = lambda: random.randint(0, 255)
            return r_num(), r_num(), r_num()

    def send_item_webhook(self, item, notification="new creation found"):
        if skip_webhook is True:
            return
        collection = item.get("collection")
        item = item.get("item")
        # print("item", item)
        for wb in webhooks:
            new_listing_webhook = wb["new_listing_webhook"]
            lowest_ask_webhook = wb["lowest_ask_webhook"]
            sales_tracker_webhook = wb["sales_tracker_webhook"]
            floor_webhook = wb["floor_webhook"]
            username = wb["username"]
            footer_icon = wb["footer_icon"]
            footer_text = wb["footer_text"]
            avatar_url = wb["avatar_url"]
            w_url = new_listing_webhook if notification != "new lowest ask" else lowest_ask_webhook
            if w_url is None:
                continue
            webhook = DiscordWebhook(
                url=w_url,
                proxies=get_random_proxy(),
                username=username,
                avatar_url=avatar_url
            )
            r_num = lambda: random.randint(0, 255)
            r_color = '0x%02X%02X%02X' % self.get_color_from_image(item.get("image"))  # % (r_num(), r_num(), r_num())
            embed = DiscordEmbed(title=f"{notification} - {item.get('name').title()}", color=r_color)
            embed.url = item.get("url")
            # embed.description = f"`{notification}`"
            embed.set_author(name=collection.get("name"), url=collection.get("url"), icon_url=collection.get("image"))
            embed.set_image(url=item.get("image"))
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon
            )
            embed.set_timestamp()
            bestBid = item.get("bestBid")
            bestAsk = item.get("bestAsk")
            bestAskCrypto = bestAsk.get("crypto")
            bestAskUsdPrice = bestAsk.get("amount")
            bestBidkCrypto = bestBid.get("crypto")
            bestBidUsdPrice = bestBid.get("amount")
            if bestBidkCrypto is not None:
                embed.add_embed_field(name="Best Bid", value=f'`{bestBidkCrypto} / {bestBidUsdPrice}`', inline=False)
            if bestAskCrypto is not None:
                embed.add_embed_field(name="Best Ask", value=f'`{bestAskCrypto} / {bestAskUsdPrice}`', inline=False)
            embed.add_embed_field(name="Other Info",
                                  value=f'favorites count: `{item.get("favoritesCount")}`\nhasUnlockableContent: `{item.get("hasUnlockableContent")}`\nisListable: `{item.get("isListable")}`\n',
                                  inline=False)
            # embed.add_embed_field(name='Field 2', value='dolor sit')
            webhook.add_embed(embed)
            # webhook.set_content(f"||@everyone||")
            r = 429
            while r == 429:
                try:
                    response = webhook.execute()
                    r = response.status_code
                    if r not in range(200, 300):
                        time.sleep(response.json()["retry_after"] // 1000)
                        raise Exception("not successfully sent")
                except Exception as e:
                    print("webhook error", e.__class__.__name__, e)
                    # time.sleep(5)

    def save_creation(self, collection_address, item_id, data):
        if not os.path.exists("./items/"):
            os.mkdir("./items")
        with open(f"./items/{collection_address}_{item_id}.json", "w") as file:
            file.write(json.dumps(data, indent=4))
            # print("saved creation")

    def get_creation(self, collection_address, item_id):
        try:
            with open(f"./items/{collection_address}_{item_id}.json", "r") as file:
                f_content = file.read()
                file.close()
            return json.loads(f_content)
        except:
            return None

    def save_sale(self, sale_id, data):
        if not os.path.exists("./sales/"):
            os.mkdir("./sales")
        with open(f"./sales/{sale_id}.json", "w") as file:
            file.write(json.dumps(data, indent=4))

    def get_sale(self, sale_id):
        try:
            with open(f"./sales/{sale_id}.json", "r") as file:
                f_content = file.read()
                file.close()
            return json.loads(f_content)
        except:
            return None

    def start_sales_checking(self, link):
        sp = link.split("/")
        # https://opensea.io/assets/0x495f947276749ce646f68ac8c248420045cb7b5e/27924270281123581347558680145632188646237271278990638796002432333265751769108
        collection_address = sp[4]
        token_id = sp[5]
        item = self.get_creation(collection_address, token_id)
        if item is None:
            print("not possible without having info about the collection")
            return
        while 1:
            try:
                sales = self.get_sales(collection_address, token_id)
                for sale in sales:
                    sale_id = f"{collection_address}_{token_id}_{sale['id']}"
                    # print("checking sale", sale_id, sale)
                    found_sale = self.get_sale(sale_id)
                    # sale_type = sale["eventType"]
                    # if sale_type != "SUCCESSFUL":
                    #    print("sale_type", sale_type)
                    #    break
                    # print("found_sale", found_sale)
                    if found_sale is None:
                        print("new sale", sale_id, item, sale)
                        self.send_sale_webhook(item, sale)
                        self.save_sale(sale_id, sale)
            except Exception as e:
                print("error checking sales", e.__class__.__name__, e)
            time.sleep(5)

    def start_collection_checking(self, collection_name):
        while 1:
            try:
                creations = self.get_collection(collection_name)
                for creation in creations:
                    try:
                        # print("creation", creation)
                        collection_address = creation["collectionAddress"]
                        token_id = creation["token_id"]
                        old_creation = self.get_creation(collection_address, token_id)
                        # print("old_creation", old_creation)
                        if old_creation is None:
                            # print("new creation found", creation)
                            print("new listing found for this creation", collection_address, token_id, creation)
                            self.save_creation(collection_address, token_id, creation)
                            self.send_item_webhook(creation, notification="new listing found")
                        else:
                            try:
                                new_best_ask = float(creation["item"]["bestAsk"]["amount"].split(" ")[0])
                            except:
                                new_best_ask = None
                            try:
                                old_best_ask = float(old_creation["item"]["bestAsk"]["amount"].split(" ")[0])
                            except:
                                old_best_ask = None
                            if new_best_ask is not None:
                                # self.save_creation(collection_address, token_id, creation)
                                # print(new_best_ask, old_best_ask)
                                real_new_ask = "not found" if new_best_ask is None else new_best_ask
                                real_old_ask = "not found" if old_best_ask is None else old_best_ask
                                if type(real_new_ask) not in [None, str] and type(real_old_ask) not in [None,
                                                                                                        str] and real_new_ask < real_old_ask:
                                    print("new lowest ask on creation", collection_address, token_id, creation)
                                    self.send_item_webhook(creation, notification="new lowest ask")
                                elif real_new_ask is not None and real_old_ask is not None and real_new_ask != real_old_ask:
                                    # todo remove
                                    # continue
                                    print("new listing found with different ask", collection_address,
                                          token_id, creation)
                                    self.send_item_webhook(creation, notification="new listing found")
                                self.save_creation(collection_address, token_id, creation)
                    except Exception as e:
                        print("error checking creation", e.__class__.__name__, e)
            except Exception as e:
                print("error checking collection", e.__class__.__name__, e)
            time.sleep(5)


def collection_checking(c):
    open_sea = OpenSea()
    Thread(target=open_sea.start_collection_checking, args=(c,)).start()


def sales_checking(c):
    open_sea = OpenSea()
    Thread(target=open_sea.start_sales_checking, args=(c,)).start()


def main():
    helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')
    a = OpenSea()
    a.get_collection("boredapeyachtclub")
    #for c in c_list:
    #    collection_checking(c)
    # for u in url_list:
    #     sales_checking(u)
    #for collection_name in c_list:
    #    Thread(target=start_checker, args=(collection_name,)).start()


if __name__ == '__main__':
    main()
