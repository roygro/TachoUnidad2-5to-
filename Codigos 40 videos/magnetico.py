import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
MAGNETIC_SENSOR_PIN = 15  # Pin digital donde está conectado el sensor de campo magnético
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/magnetico"
MQTT_CLIENT_ID = "magnetic_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor como entrada
magnetic_sensor = Pin(MAGNETIC_SENSOR_PIN, Pin.IN, Pin.PULL_UP)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("No se pudo conectar a Wi-Fi")
    return False

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("Conectado a MQTT y publicando en:", MQTT_TOPIC)
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                sensor_state = magnetic_sensor.value()
                client.publish(MQTT_TOPIC, str(sensor_state))  # Publicar 1 o 0
                print(f"Estado del sensor enviado: {sensor_state}")
                
                time.sleep(1)  # Espera un segundo antes de la siguiente lectura
            except Exception as e:
                print("Error en loop MQTT:", e)
                break
else:
    print("No se pudo conectar a Wi-Fi.")
