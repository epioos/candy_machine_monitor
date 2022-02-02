import os
import random
import sys
import time

import requests


def proxies_setup_file():
    if not os.path.isfile("proxies.txt"):
        with open("proxies.txt", "w") as file:
            file.write("")
        print("proxies.txt file creates. please fill it with proxies now")
        sys.exit()


def get_all_proxies():
    with open("./proxies.txt", "r") as file:
        proxies = []
        for line in file.readlines():
            temp_p = line.replace("\n", "").replace("\r", "").replace("\r\n", "").replace("\n\r", "").replace(" ", "")
            if temp_p not in proxies:
                proxies.append(temp_p)
        # print(len(proxies), "proxies found")
        return proxies


def proxy_string_to_proxy_header(proxy_ip):
    task_proxy = ""
    if proxy_ip != "":
        temp_proxy = proxy_ip.split(":")
        if len(temp_proxy) == 4:
            task_proxy = {
                "http": "http://" + temp_proxy[2] + ":" + temp_proxy[3] + "@" + temp_proxy[0] + ":" + temp_proxy[1],
                "https": "http://" + temp_proxy[2] + ":" + temp_proxy[3] + "@" + temp_proxy[0] + ":" + temp_proxy[1],
            }
        else:
            task_proxy = {
                "http": "http://" + temp_proxy[0] + ":" + temp_proxy[1],
                "https": "http://" + temp_proxy[0] + ":" + temp_proxy[1],
            }
    return task_proxy


def get_random_proxy():
    proxies = get_all_proxies()
    if len(proxies) > 0:
        proxy = random.choice(proxies)
        task_proxy = proxy_string_to_proxy_header(proxy)
        # print("used proxy", task_proxy)
        return task_proxy
    else:
        return None


def test_proxy(proxy, link):
    print("testing proxy:", proxy, "on", link)
    start_time = time.time()
    task_proxy = ""
    if proxy != "":
        temp_proxy = proxy.split(":")
        if len(temp_proxy) == 4:
            task_proxy = {
                "http": "http://" + temp_proxy[2] + ":" + temp_proxy[3] + "@" + temp_proxy[0] + ":" + temp_proxy[1],
                "https": "https://" + temp_proxy[2] + ":" + temp_proxy[3] + "@" + temp_proxy[0] + ":" + temp_proxy[1],
            }
        else:
            task_proxy = {
                "http": "http://" + temp_proxy[0] + ":" + temp_proxy[1],
                "https": "https://" + temp_proxy[0] + ":" + temp_proxy[1],
            }
    try:
        requests.get(link, proxies=task_proxy, timeout=120)
        execution_time = time.time() - start_time
        ms = int(execution_time * 1000)
        print("[RESULT]", "proxy:", proxy, "url:", link, "working:", True, "response time:", ms, "ms")
        return True, ms
    except Exception as e:
        print(e)
        print("[RESULT]", "proxy:", proxy, "url:", link, "working:", False, "response time:", 0, "ms")
        return False, 0


def test_all_proxies():
    working_proxies = []
    i = 0
    for x in get_all_proxies():
        try:
            working, timing = test_proxy(x, "https://kith.com")
            if working:
                working_proxies.append(x)
        except Exception as e:
            print(e)
            print(i, "proxy not working", x)
        i += 1
    with open(os.path.join("proxies.txt"), "w") as file:
        w_proxies_s = ""
        for y in working_proxies:
            w_proxies_s += y + "\n"
        file.writelines(w_proxies_s)
