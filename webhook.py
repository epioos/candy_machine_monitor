from discord_webhook import DiscordWebhook, DiscordEmbed
from settings import webhook_url


def send_discord_webhook(address, version, metadata, nft_name, image, description):
    webhook = DiscordWebhook(url=webhook_url)
    cm_timestamp = metadata.get("go_live_date", None)
    if cm_timestamp is not None:
        cm_timestamp = int(cm_timestamp)
        cm_timestamp_discord = f"<t:{cm_timestamp}:R>"
    else:
        cm_timestamp_discord = "not found"

    cm_machine_id = metadata.get("candy_machine_id", None)
    if cm_machine_id is not None:
        cm_machine_id_discord = cm_machine_id
    else:
        cm_machine_id_discord = "not found"
    cm_items_available = metadata.get("items_available", None)
    if cm_items_available is not None:
        cm_items_available_discord = str(int(cm_items_available))
    else:
        cm_items_available_discord = "not found"
    cm_price = metadata.get("price", None)
    if cm_price is not None:
        cm_price_discord = float(int(cm_price) / 1000000000).__round__(2).__str__() + " SOL"
    else:
        cm_price_discord = "not found"
    embed = DiscordEmbed(title="New candy machine found", color='03b2f8')
    embed.add_embed_field(name='name', value=nft_name, inline=False)
    embed.add_embed_field(name='address', value=address, inline=False)
    embed.add_embed_field(name='version', value=version, inline=False)
    embed.add_embed_field(name='machine id', value=cm_machine_id_discord, inline=False)
    embed.add_embed_field(name='go live', value=cm_timestamp_discord, inline=False)
    embed.add_embed_field(name='available items', value=cm_items_available_discord, inline=False)
    embed.add_embed_field(name='price', value=cm_price_discord, inline=False)
    if image is not None:
        embed.set_thumbnail(url=image)
    if description is not None:
        embed.add_embed_field(name='description', value=description, inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()
    # print(response.request.body)
    print("webhook", response.status_code)
