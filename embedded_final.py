import serial
import time
import requests
import broadlink
from broadlink.exceptions import NetworkTimeoutError

#Loop Timing
x_minutes = .5
minutes = x_minutes * 60

#Broadlink INFO
device_ip = 'device IPS'
device_mac = 'device mac'

device = broadlink.hello(device_ip, 80, 5)

IR_on = '2600400000011184123112121212111411311213111311131013121311131112121211141212121112121132142f13121112121212131013131112321130121411000d05000000000000'
IR_off = '2600400000011085113213111212111312311113121212121231123111131212121212121113131113111212111313111212123113111231121411111113113212000d05000000000000'

if device:
    device.auth()
    print("A Broadlink Device has beenfound")
else:
    print("No Broadlink Devices found")

# API INFO
APIkey = 'YOUR_API_KEY'
lat = "YOUR_LAT_POS"
lon = "YOUR_LON_POS"

# SERIAL
ser = serial.Serial('/dev/YOURPORT', 9600)

def send_ir_command(command):
    try:
        print("Trying")
        device.send_data(bytes.fromhex(command))
        print("Done")
    except NetworkTimeoutError:
        print("Network Timed Out")
    except Exception as e:
        print(f"Error sending IR command {e}")

def get_weather(APIkey, lon, lat):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={APIkey}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
        }
        print(f"OUTDOOR_WEATHER: {weather_info}")
        return weather_info
    else:
        print(response)
        print("Failed to fetch weather data.")
        return None

def get_indoor_temp():
    motion = False
    indoor_temp = None
    #Logic For fetching Indoor Motion
    while ser.in_waiting > 0:
		#Logic
        data = ser.readline().decode().strip()
        if "Motion" in data:
            motion = "True" in data
        if "Temperature" in data:
            indoor_temp = float(data.split("Temperature:")[1].split("Motion")[0].strip())

    print(f"INDOOR_TEMP: {indoor_temp}  MOTION:{motion}")
    return motion, indoor_temp

while True:
    weather_info = get_weather(APIkey, lon, lat)
    outdoor_temp = weather_info['temperature']
    motion, indoorTemp = get_indoor_temp()

	
    # DECISION MAKING
    # IF PEOPLE ARE HOME OR EXPECTED TO BE HOME
    if motion or (17 <= time.localtime().tm_hour < 7):
        # IF TEMP OUTSIDE IS 'EXTREME' AND TEMP INSIDE IS NOT OPTIMAL
        print("Someone's Home")
        if abs(outdoor_temp - 21) >=5 and abs(indoorTemp - 21) >= 2:
            # USE AC TO ADJUST TEMP
            print("Uncomfortable Temperature discovered")
            send_ir_command(IR_on)
        else:
            # TURN AC OFF
            print("Temperature is comfortable")
            send_ir_command(IR_off)
    else:
        # TURN AC OFF
        print("No body Home")
        send_ir_command(IR_off)
        
    #LOOP TIMING
    print(f"Waiting {minutes/60} minutes")
    time.sleep(minutes)
