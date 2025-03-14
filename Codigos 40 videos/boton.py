from machine import Pin
import network
import time
import ubinascii
from umqtt.simple import MQTTClient

# Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# Configuración MQTT
MQTT_BROKER = "192.168.137.202"
MQTT_CLIENT_ID = ubinascii.hexlify(network.WLAN().config('mac')).decode()
MQTT_TOPIC = "prgs/boton"

# Conectar al WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(1)
print("Conectado a WiFi")

# Configurar MQTT
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.connect()
print("Conectado al broker MQTT")

# Configurar botón
boton = Pin(4, Pin.IN, Pin.PULL_UP)  # Usa el pin GPIO4 o cambia según tu conexión
estado = 0

while True:
    if not boton.value():  # Si el botón se presiona (activo bajo)
        estado = not estado  # Alterna entre 0 y 1
        client.publish(MQTT_TOPIC, str(estado))
        print(f"Botón presionado, estado: {estado}")
        time.sleep(0.3)  # Pequeña espera para evitar rebotes