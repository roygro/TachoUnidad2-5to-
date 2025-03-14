import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
MQ9_PIN = 34  # GPIO donde conectaste la salida analógica del sensor MQ-9 (pin ADC)
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/mq9"
MQTT_CLIENT_ID = "mq9_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Inicializar el sensor MQ-9 como ADC (analógico)
mq9_sensor = ADC(Pin(MQ9_PIN))  # Configurar el pin ADC
mq9_sensor.atten(ADC.ATTN_0DB)  # Configurar el rango de voltaje (0-1V)

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

def read_mq9_sensor():
    # Leer el valor del sensor MQ-9 (escala de 0 a 1023)
    return mq9_sensor.read()

def publish_mq9_state(client):
    if client:
        try:
            state = read_mq9_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del sensor MQ-9 enviado:", state)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        if not wlan.isconnected():
            print("⚠️ Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("⚠️ Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_mq9_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
