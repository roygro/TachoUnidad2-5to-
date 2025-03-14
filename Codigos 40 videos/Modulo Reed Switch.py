import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del Reed Switch y la conexión MQTT
REED_PIN = 14  # Pin GPIO al que está conectado el Reed Switch
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/reedswitch"  # Tópico de MQTT para el Reed Switch
MQTT_CLIENT_ID = "reedswitch_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del pin para leer el estado del Reed Switch
reed_switch = Pin(REED_PIN, Pin.IN, Pin.PULL_UP)  # Entrada con resistencia pull-up interna

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("❌ No se pudo conectar a Wi-Fi")
    return False

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def read_reed_switch():
    """ Función para leer el estado del Reed Switch y enviar 1 o 0 """
    if reed_switch.value() == 0:  # Reed Switch cerrado (imán cerca)
        print("📊 Reed Switch cerrado: 1")
        return 1  # Enviar 1 cuando está cerrado
    else:
        print("📊 Reed Switch abierto: 0")
        return 0  # Enviar 0 cuando está abierto

def send_reed_status(client, value):
    """ Función para enviar el estado del Reed Switch al broker MQTT """
    try:
        client.publish(MQTT_TOPIC, str(value))
        print(f"📤 Mensaje enviado: {value}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                # Leer el estado del Reed Switch y enviarlo
                reed_value = read_reed_switch()
                send_reed_status(client, reed_value)
                time.sleep(1)  # Esperar un segundo antes de la siguiente lectura
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
