import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del micrófono y la conexión MQTT
MICROPHONE_PIN = 14  # Pin GPIO al que está conectado el micrófono
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/microphone"  # Tópico de MQTT para controlar el micrófono
MQTT_CLIENT_ID = "microphone_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del pin para leer el estado del micrófono (salida digital)
microphone = Pin(MICROPHONE_PIN, Pin.IN)  # Entrada digital (0 o 1)

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

def read_microphone():
    """ Función para leer el estado del micrófono y devolver 1 o 0 """
    if microphone.value() == 1:  # Si el micrófono detecta sonido (valor alto)
        print("📊 Sonido detectado: 1")
        return 1  # 1 si detecta sonido
    else:
        print("📊 No se detecta sonido: 0")
        return 0  # 0 si no detecta sonido

def send_microphone_status(client, value):
    """ Función para enviar el estado del micrófono al broker MQTT """
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
                # Leer el estado del micrófono y enviarlo
                microphone_value = read_microphone()
                send_microphone_status(client, microphone_value)
                time.sleep(1)  # Esperar un segundo antes de la siguiente lectura
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
