import tkinter as tk
import paho.mqtt.client as mqtt
import time

# Set up MQTT client
mqtt_server = "10.5.104.211"
mqtt_port = 1883
mqtt_topic_led = "led_blink"
mqtt_topic_status = "status"
mqtt_client_id = "gui-client"

client = mqtt.Client(mqtt_client_id)
client.connect(mqtt_server, mqtt_port)

# Define functions to send MQTT messages
def turn_on():
    client.publish(mqtt_topic_led, "ON")

def turn_off():
    client.publish(mqtt_topic_led, "OFF")

def turn_on_delay():
    delay = int(delay_entry.get())
    client.publish(mqtt_topic_led, "ON," + str(delay))

def turn_off_delay():
    delay = int(delay_entry.get())
    client.publish(mqtt_topic_led, "OFF," + str(delay))

# Define callback function to handle MQTT message
def on_message(client, userdata, message):
    global led_state, runtime
    msg = message.payload.decode('utf-8')
    print("Received message:", msg)
    if msg.startswith("LED_STATUS"):
        led_state = msg.split(":")[1].strip()
        if led_state == "ON":
            led_label.config(text="LED state: " + led_state, fg="green")
        elif led_state == "OFF":
            led_label.config(text="LED state: " + led_state, fg="red")
    elif msg.startswith("UPTIME"):
        runtime = msg.split(":")[1].strip()
        runtime_label.config(text=f"Lama pemakaian: {runtime}s")

# Set up GUI
root = tk.Tk()
root.title("LED Control")

# Create widgets
led_label = tk.Label(root, text="LED state: -", font=("Arial", 14))
runtime_label = tk.Label(root, text="Lama pemakaian: -", font=("Arial", 14))
on_button = tk.Button(root, text="Turn On", command=turn_on, font=("Arial", 14))
off_button = tk.Button(root, text="Turn Off", command=turn_off, font=("Arial", 14))
delay_label = tk.Label(root, text="Turn On Delay (seconds):", font=("Arial", 14))
delay_entry = tk.Entry(root, font=("Arial", 14))
delay_on_button = tk.Button(root, text="Turn On with Delay", command=turn_on_delay, font=("Arial", 14))
delay_off_button = tk.Button(root, text="Turn Off with Delay", command=turn_off_delay, font=("Arial", 14))

# Place widgets on grid
led_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
runtime_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
on_button.grid(row=2, column=0, padx=10, pady=10)
off_button.grid(row=2, column=1, padx=10, pady=10)
delay_label.grid(row=3, column=0, padx=10, pady=10)
delay_entry.grid(row=3, column=1, padx=10, pady=10)
delay_on_button.grid(row=4, column=0, padx=10, pady=10)
delay_off_button.grid(row=4, column=1, padx=10, pady=10)

# Set up MQTT subscriber and start main loop
client.subscribe(mqtt_topic_status)
client.on_message = on_message
client.loop_start()

# Run GUI
root.mainloop()
