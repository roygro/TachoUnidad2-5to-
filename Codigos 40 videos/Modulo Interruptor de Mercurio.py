import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del interruptor de mercurio y la conexión MQTT
MERCURY_SENSOR_PIN = 14  # Pin GPIO al que está conectado el interruptor de mercurio
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/mercury"  # Tópico de MQTT para controlar el interruptor
MQTT_CLIENT_ID = "mercury_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del pin para leer el estado del interruptor de mercurio
mercury_switch = Pin(MERCURY_SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Entrada con resistencia pull-up interna

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

def read_mercury_switch():
    """ Función para leer el estado del interruptor de mercurio y devolver 1 o 0 """
    if mercury_switch.value() == 0:  # El interruptor está cerrado (mercursor en contacto, normalmente en posición horizontal)
        print("📊 Interruptor de mercurio cerrado: 0")
        return 0  # 0 si está cerrado
    else:
        print("📊 Interruptor de mercurio abierto: 1")
        return 1  # 1 si está abierto (en posición vertical)

def send_mercury_status(client, value):
    """ Función para enviar el estado del interruptor de mercurio al broker MQTT """
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
                # Leer el estado del interruptor de mercurio y enviarlo
                mercury_value = read_mercury_switch()
                send_mercury_status(client, mercury_value)
                time.sleep(1)  # Esperar un segundo antes de la siguiente lectura
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
