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


def main():
    #helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')
    #a = OpenSea()
    #a.get_collection("boredapeyachtclub")
    #for c in c_list:
    #    collection_checking(c)
    # for u in url_list:
    #     sales_checking(u)
    #for collection_name in c_list:
    #    Thread(target=start_checker, args=(collection_name,)).start()


if __name__ == '__main__':
    main()
