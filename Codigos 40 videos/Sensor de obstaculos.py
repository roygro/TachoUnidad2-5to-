import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
OBSTACLE_SENSOR_PIN = 14  # Pin de entrada del sensor de obstáculos
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/obstaculos"
MQTT_CLIENT_ID = "obstacle_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor de obstáculos como entrada
obstacle_sensor = Pin(OBSTACLE_SENSOR_PIN, Pin.IN)

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

def check_obstacle_sensor():
    """ Función para comprobar el estado del sensor de obstáculos y enviar 1 o 0 """
    sensor_value = obstacle_sensor.value()  # Lee el estado del sensor (HIGH o LOW)
    print(f"📊 Estado del sensor de obstáculos: {sensor_value}")

    # Publicar 0 si se detecta un obstáculo (LOW) o 1 si no se detecta obstáculo (HIGH)
    client.publish(MQTT_TOPIC, str(sensor_value))  # Publicar 0 o 1 en el tema MQTT

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                check_obstacle_sensor()  # Comprobar el estado del sensor de obstáculos y enviar el valor
                time.sleep(0.5)  # Comprobar cada medio segundo
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
