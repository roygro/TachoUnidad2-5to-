import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
SENSOR_PIN = 14  # Pin de la señal del sensor de pulso
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/pulso"
MQTT_CLIENT_ID = "pulse_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor de pulso
pulse_sensor = Pin(SENSOR_PIN, Pin.IN)

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

def get_pulse_data():
    """ Función para leer datos del sensor de pulso y enviarlos por MQTT """
    pulse_state = pulse_sensor.value()  # Lee el estado del sensor (HIGH o LOW)
    print(f"📊 Estado del sensor de pulso: {pulse_state}")
    
    # Publicar el estado (0 o 1) en el tópico MQTT
    client.publish(MQTT_TOPIC, str(pulse_state))

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                get_pulse_data()  # Leer el estado del sensor y enviarlo por MQTT
                time.sleep(1)  # Leer cada segundo
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
