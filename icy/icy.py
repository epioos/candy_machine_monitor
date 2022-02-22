import datetime

import discord
import requests
from bs4 import BeautifulSoup
from discord.embeds import Embed

bot_token = "OTMzODc3NzYwODAyMzI0NTEx.Yen7cA.3DQNHsnxVERbLlZf6knofCxl7CQ"
icy_channel_id = 929328771155263578

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    target_channel = await client.fetch_channel(icy_channel_id)
    history_list = await target_channel.history(limit=1).flatten()
    last_msg = history_list[0]
    print("last_msg", last_msg)
    # await check_collection(last_msg)


@client.event
async def on_message(message):
    if message.author != client.user:
        await check_collection(message)


async def check_collection(message):
    if message.channel.id == icy_channel_id:
        if len(message.embeds) != 0:
            embed = message.embeds[0]
            url = embed.url
            try:
                stats = scrape_stats(url)
                new_embed = send_embed(embed, stats)
            except Exception as e:
                print("error getting stats", e)
            else:
                target_channel = await client.fetch_channel(944335942850854982)
                await target_channel.send(embed=new_embed)


def scrape_stats(target_collection) -> dict:
    response = requests.get(
        target_collection,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
    )
    print(response.status_code, response.reason)
    soup = BeautifulSoup(response.text, "html.parser")
    links_div = soup.find("div", {"class": "flex flex-row flex-wrap justify-between"})
    all_links = links_div.find_all("a")
    print(len(all_links), "links found")
    found_links = []
    for link in all_links:
        if link is not None:
            target_link = link.get("href")
            link_name = link.text
            _ = {"name": link_name, "url": target_link}
            print(_)
            found_links.append(_)
    stats_div = soup.find("dl", {"class": "grid gap-5 grid-cols-2 md:grid-cols-4"})
    # print("stats_div:", stats_div)
    all_stats = stats_div.find_all("div")
    print(len(all_stats), "stats found")
    found_stats = []
    for stat in all_stats:
        if stat is not None:
            stat_name = stat.find("dt").text
            stat_value = stat.find("dd").text
            _ = {"name": stat_name, "value": stat_value}
            print(_)
            found_stats.append(_)
    return {"links": found_links, "stats": found_stats}


def send_embed(embed, stats):
    # print(dir(embed.fields))
    # embed.author.url = ""
    new_description = embed.description.split(".")[0]
    new_description += "\n\n"
    for item in stats['stats']:
        new_description += f"**{item['name']}**: {item['value']}\n"
    new_description += "\n"
    new_embed = Embed(
        title=embed.title,
        description=new_description,
        url=embed.url,
        color=embed.color
    )
    new_embed.set_author(
        name="5min Mint Alert"
    )
    # embed.description = new_description
    new_embed.set_footer(
        text="MetaMint",
        icon_url="https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
    )

    new_embed.set_thumbnail(url=embed.thumbnail.url)
    links_str = " | ".join([f'[{item["name"]}]({item["url"]})' for item in stats['links']])
    new_embed.add_field(
        name="Links:",
        value=links_str,
        inline=False
    )
    new_embed.timestamp = datetime.datetime.now()
    return new_embed


client.run(bot_token)
