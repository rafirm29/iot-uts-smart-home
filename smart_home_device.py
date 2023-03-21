# 135151954 / Rafi Raihansyah Munandar
# Connect to a wifi
import network

ssid = "wifi_ssid"
password = "wifi_password"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print("Connected to Wi-Fi network:", ssid)

# Import required libs
import machine
import time
import ubinascii
from umqtt.simple import MQTTClient

# MQTT parameters
mqtt_server = "192.168.137.215"
mqtt_port = 1883
mqtt_topic_led = b"led_blink"
mqtt_topic_status = b"status"
mqtt_client_id = "esp32-client"

# Pin number for LED
led = machine.Pin(2, machine.Pin.OUT)

# Set up MQTT client
client = MQTTClient(client_id=mqtt_client_id, server=mqtt_server, port=mqtt_port, keepalive=60)

# Connect to MQTT broker
client.connect()
print("Connected to %s MQTT broker" % mqtt_server)

# Define variable for LED on/off time
led_on_time = 0
last_led_time = 0
last_off_time = time.time()
    
# Define callback function to handle MQTT message
def callback(topic, msg):
    global last_led_time, last_off_time, led_on_time
    message = msg.decode('utf-8')
    print("Received message: ", message)
    if ',' in message:
        # Split the message into value and delay time
        value, delay = message.split(',')
        # Wait for the specified delay before setting the LED value
        start_loop = time.time()
        while time.time() < start_loop + int(delay):
            if value == "OFF":
                # When turning OFF with delay, continue update the ON time
                # during the delay
                print("Turning off in " + str((start_loop + int(delay)) - time.time()))
                uptime = time.time() - last_off_time
                led_on_time = last_led_time + uptime
                client.publish(mqtt_topic_status, "UPTIME:" + str(led_on_time))
            elif value == "ON":
                print("Turning on in " + str((start_loop + int(delay)) - time.time()))
            time.sleep(1)
    else:
        value = message

    # Set the LED value
    if value == "ON":
        last_off_time = time.time()
        led.on()
    elif value == "OFF":
        last_led_time = led_on_time
        led.off()

# Subscribe to LED topic commands
client.set_callback(callback)
client.subscribe(mqtt_topic_led)
print("Subscribed to topic: ", mqtt_topic_led)

# Create a publisher for device status
def publish_status():
    global led_on_time
    
    led_status = "ON" if led.value() == 1 else "OFF"
    
    if led_status == "ON":
        # Continue adding LED ON time when it's ON
        uptime = time.time() - last_off_time
        led_on_time = last_led_time + uptime
        client.publish(mqtt_topic_status, "LED_STATUS:ON")
        client.publish(mqtt_topic_status, "UPTIME:" + str(led_on_time))
    else:
        client.publish(mqtt_topic_status, "LED_STATUS:OFF")

# Wait for messages
last_ping = time.time()
last_publish = time.time()
try:
    while True:
        # Ping every 30 seconds to keep connection alive
        if time.time() - last_ping > 30:
            client.ping()
            last_ping = time.time()
        
        # Publish every 1 second
        if time.time() - last_publish > 0:
            last_publish = time.time()
            publish_status()

        client.check_msg()
finally:
    client.disconnect()