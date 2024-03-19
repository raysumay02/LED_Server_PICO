from connect import WLAN_Connect
import uasyncio as asyncio
from machine import Pin
from secrets import secrets
import time
import random

ssid = secrets['ssid']
password = secrets['password']

Wifi = WLAN_Connect(ssid, password, 'IN')

# INIT LED TO CONTROL
serv_led = Pin(2, Pin.OUT)
blink_led = Pin(10, Pin.OUT)

state = 'OFF'
random_value = 0

# HTML template for the webpage
def webpage(random_value, state):
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico Web Server</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f2f2f2; color: #333; text-align: center;">
    <h1 style="margin-top: 20px;">Raspberry Pi Pico Web Server</h1>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <h2 style="margin-top: 30px; color: #007bff;">Led Control</h2>
        <form action="./lighton" style="margin-top: 10px;">
            <input type="submit" value="Light on" style="padding: 10px 20px; font-size: 16px; background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s;" />
        </form>
        <br>
        <form action="./lightoff" style="margin-top: 10px;">
            <input type="submit" value="Light off" style="padding: 10px 20px; font-size: 16px; background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s;" />
        </form>
        <p style="margin-top: 10px;">LED state: {state}</p>
        <h2 style="margin-top: 30px; color: #007bff;">Fetch New Value</h2>
        <form action="./value" style="margin-top: 10px;">
            <input type="submit" value="Fetch value" style="padding: 10px 20px; font-size: 16px; background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s;" />
        </form>
        <p style="margin-top: 10px;">Fetched value: {random_value}</p>
    </div>
</body>
</html>

            """
    
    return str(html)

# Asynchronous function to handle client's requests
async def handle_client(reader, writer):
    global state
    
    print("Client connected")
    request_line = await reader.readline()
    print('Request:', request_line)
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    print('Request:', request)
    
    # Process the request and update variables
    if request == '/lighton?':
        print('LED on')
        serv_led.value(1)
        state = 'ON'
    elif request == '/lightoff?':
        print('LED off')
        serv_led.value(0)
        state = 'OFF'
    elif request == '/value?':
        global random_value
        random_value = random.randint(0, 20)

    # Generate HTML response
    response = webpage(random_value, state)  

    # Send the HTTP response and close the connection
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')
    
    
async def blink_led():
    while True:
        blink_led.value(1)  # Toggle LED state
        await asyncio.sleep(0.5)  # Blink interval
        
        
async def main():    
#     if not init_wifi(ssid, password):
#         print('Exiting program.')
#         return
    Wifi.connect(timeout=10)
    
    # Start the server and run the event loop
    print('Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)
    asyncio.create_task(blink_led())
    
    while True:
        # Add other tasks that you might need to do in the loop
        await asyncio.sleep(5)
        print('This message will be printed every 5 seconds')
        
        
# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')
