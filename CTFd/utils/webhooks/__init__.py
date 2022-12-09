from flask import current_app as app
import requests

def send_discord_webhook(embeds):
#    webhook_url = "https://discordapp.com/api/webhooks/509273046582951958/BXi4pa_nXcbpGTmISJH-otPW0_MRkFcgXtxD7gWYSAcCi22QDZV-Bv62uUN305OocINl"
    webhook_url = 'https://discordapp.com/api/webhooks/757326355028246628/pGJlvMvAqGEa6yivkWulZRnHtwqYeyNUI-79vJO1fOT-dlRiyiC111n0VTDbs9H-62tR'
    if webhook_url is None:
        return

    requests.post(webhook_url, json={
        "embeds": embeds,
        "username": "CTFd"
    })
