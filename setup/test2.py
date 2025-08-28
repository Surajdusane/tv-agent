from androidtvremote2 import AndroidTVRemote
import asyncio
from pathlib import Path

async def control_tv_volume():
    # TV connection details
    tv_ip = "10.34.76.1-254"
    client_name = "PythonRemoteControl"
    
    # Create a directory for certificates if it doesn't exist
    cert_dir = Path("androidtv_remote_certs")
    cert_dir.mkdir(exist_ok=True)
    
    # Certificate file paths
    certfile = str(cert_dir / "client.crt")
    keyfile = str(cert_dir / "client.key")
    
    # Initialize the remote with all required parameters
    remote = AndroidTVRemote(
        client_name=client_name,
        certfile=certfile,
        keyfile=keyfile,
        host=tv_ip  # This was the missing required parameter
    )
    
    try:
        # Generate certificates if needed
        print("Generating certificates if needed...")
        await remote.async_generate_cert_if_missing()
        
        # Connect to the TV
        print(f"Connecting to TV at {tv_ip}...")
        await remote.async_connect()
        
        # Check if connection was successful
        if remote.is_on:
            print("Successfully connected to TV!")
            
            # Increase the volume
            print("Increasing volume...")
            await remote.volume_up()
            
            # You can call this multiple times to increase more
            # await remote.volume_up()
            # await remote.volume_up()
            
        else:
            print("TV is not responding")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Disconnect when done
        if remote.is_on:
            await remote.disconnect()
            print("Disconnected from TV")

# Run the async function
asyncio.run(control_tv_volume())