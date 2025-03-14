import time
import network
from machine import Pin
import dht
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
DHT_PIN = 4  # Pin digital donde está conectado el sensor DHT11 (GPIO4 en ESP8266/ESP32)
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/humedad"
MQTT_CLIENT_ID = "dht11_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Inicializar el sensor DHT11
sensor = dht.DHT11(Pin(DHT_PIN))

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
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

def read_dht():
    """ Lee la humedad del DHT11 """
    try:
        sensor.measure()
        humedad = sensor.humidity()
        return humedad
    except Exception as e:
        print("Error al leer el DHT11:", e)
        return None

def publish_data(client):
    if client:
        humedad = read_dht()
        if humedad is not None:
            client.publish(MQTT_TOPIC, str(humedad))
            print("Enviado:", humedad, "% de humedad")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            publish_data(client)
            time.sleep(5)  # Ajusta el tiempo de muestreo según sea necesario
else:
    print("No se pudo conectar a Wi-Fi.")
