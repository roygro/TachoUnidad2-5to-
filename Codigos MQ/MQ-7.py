import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# 🔌 Configuración de pines y conexión Wi-Fi
MQ7_PIN = 34  # GPIO donde conectaste la salida analógica del MQ-7
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/mq7"
MQTT_CLIENT_ID = "mq7_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# 📡 Inicializar el sensor MQ-7 como ADC (entrada analógica)
mq7_sensor = ADC(Pin(MQ7_PIN))
mq7_sensor.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V en ESP32

def connect_wifi():
    """ Conecta el ESP32 a la red Wi-Fi """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    for _ in range(15):  # Esperar hasta 15 segundos
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("❌ No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    """ Conecta el ESP32 al broker MQTT """
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error al conectar MQTT:", e)
        return None

def read_mq7_sensor():
    """ Lee el porcentaje de gas basado en la lectura del ADC """
    raw_value = mq7_sensor.read()  # Obtiene valor crudo del ADC (0-4095)
    gas_percentage = (raw_value / 4095) * 100  # Convierte a porcentaje
    return round(gas_percentage, 2)  # Redondear a 2 decimales

def publish_mq7_state(client):
    """ Publica el porcentaje de gas del MQ-7 en MQTT """
    if client:
        try:
            gas_percentage = read_mq7_sensor()
            client.publish(MQTT_TOPIC, str(gas_percentage))
            print(f"📡 Porcentaje de gas enviado: {gas_percentage}%")
        except Exception as e:
            print("❌ Error al publicar:", e)

# 🔗 Conectar Wi-Fi y MQTT
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
        
        publish_mq7_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
