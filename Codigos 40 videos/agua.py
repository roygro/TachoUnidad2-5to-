import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
WATER_SENSOR_PIN = 15  # GPIO donde conectaste el sensor de agua
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/agua"
MQTT_CLIENT_ID = "water_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Inicializar el sensor como entrada digital
water_sensor = Pin(WATER_SENSOR_PIN, Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(15):
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("❌ No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def read_water_sensor():
    return water_sensor.value()  # 0 = Hay agua, 1 = No hay agua

def publish_water_state(client):
    if client:
        try:
            state = read_water_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del sensor enviado:", state)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        if not wlan.isconnected():
            print("⚠ Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("⚠ Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_water_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")