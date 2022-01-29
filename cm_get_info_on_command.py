from changes_monitor import get_version_of_cm
from cms_nft import get_cms_nft
from get_cm_metadata import get_metadata_of_cm
from discord import Embed


def cm_information_embed(cm_id,metadata, image, name):
    go_live = metadata["go_live_date"]
    availabele_items = metadata["items_available"]
    redeemed_items = metadata["items_redeemed"]
    price = metadata["price"]
    if price != "":
        cm_price_discord = float(int(metadata['go_live_date']) / 1000000000).__round__(2).__str__() + " SOL"
    else:
        cm_price_discord = "not found"
    if redeemed_items == "":
        redeemed_items = "not found"
    if availabele_items == "":
        availabele_items = "not found"
    if go_live != "":
        go_live = int(go_live)
        cm_timestamp_discord = f"<t:{go_live}:R>"
    else:
        cm_timestamp_discord = "not found"

    try:
        embed = Embed(
            title=name,
            color=0x00FFA3
        )
        embed.set_author(
            name="Information found",
        )
        embed.add_field(name='Candy machine ID',
                        value=cm_id,
                        inline=False)
        embed.add_field(name='Items available',
                        value=availabele_items,
                        inline=False)

        embed.add_field(name='Items redeemed',
                        value=redeemed_items,
                        inline=False)

        embed.add_field(
            name='Price',
            value=cm_price_discord,
            inline=False
        )

        embed.add_field(
            name='Go live',
            value=cm_timestamp_discord,
            inline=False
        )

        embed.set_footer(
            text="MetaMint",
            icon_url="https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
        )
        if image != "not found":
            embed.set_image(url=image)
        return embed
    except Exception as e:
        print("couldnt get information for cm info command", e)
        return None



def send_cm_information(cm_id):
    version = get_version_of_cm(cm_id)
    cms_metadata = get_metadata_of_cm(cm_id, version)
    if cms_metadata is None:
        return None
    cms_nft = get_cms_nft(cm_id, version)
    try:
        name = cms_nft["all_nfts"]["name"]
    except:
        name = "not found"
    try:
        image = cms_nft["all_nfts"]["uri"]
    except:
        image = "not found"
    return cm_information_embed(cm_id, cms_metadata, image, name)

