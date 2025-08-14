import asyncio
from androidtvremote2 import AndroidTVRemote
import json


# get all data from tools.json
with open("tools.json") as f:
   tools_data = json.load(f)

keys_codes = tools_data["keys_code_map"]

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

async def sendCode(state):
    key_code = state['current_task_command']
    repeat = state['repeat']

    try:
        tv = await connect_to_tv()
        key_code = keys_codes.get(key_code, key_code)  # Map string codes
        
        for _ in range(repeat):
            print(f"Sending key code: {key_code}")
            tv.send_key_command(key_code)
            await asyncio.sleep(0.2)  # Small delay between repeats
            
        print(f"TV command executed: {key_code} (repeated {repeat}x)")
        
        return { 'status': 'success', 'command': "", 'repeat': 1 }
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return { 'status': 'error', 'command': "", 'repeat': 1 }
    finally:
        if 'tv' in locals():
            tv.disconnect()
            print("Disconnected")

# asyncio.run(sendCode({ 'current_task_command': 'VOLUME_UP', 'repeat': 5 }))

async def sendCodeTest(state):
    key_code = state['current_task_command']
    repeat = state['repeat']
    task_number = state['task_number']
    for i in range(repeat):
        print(f"Sending key code: {key_code}")
        await asyncio.sleep(0.2)  # Small delay between repeats

    return { 'status': 'success', 'command': "", 'repeat': 1, 'task_number': task_number + 1 }