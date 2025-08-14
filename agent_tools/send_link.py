import asyncio
from androidtvremote2 import AndroidTVRemote
import json

async def connect_to_tv():
    with open("config.json") as f:
        config = json.load(f)
    tv = AndroidTVRemote(
        host=config["tv_ip"],
        certfile=config["certfile"],
        keyfile=config["keyfile"],
        client_name=config["client_name"]
    )
    print("Connecting to TV...")
    await tv.async_connect()
    print("Connected!")
    await asyncio.sleep(1)  # Stabilization time
    return tv

async def sendLink(app_url):
    try:
        tv = await connect_to_tv()
        print(f"Launching app: {app_url}")
        tv.send_launch_app_command(app_url)
        return "App launched successfully"
    except Exception as e:
        return f"Error launching app: {str(e)}"
    finally:
        if 'tv' in locals():
            tv.disconnect()

async def sendLinkTest(state):
    link = state['app_link']
    task_number = state['task_number']
    print(f"Sending Link to TV: {link}")
    await asyncio.sleep(0.2)  # Small delay between repeats
    return { 'status': 'success', 'link': "", 'task_number': task_number + 1 }