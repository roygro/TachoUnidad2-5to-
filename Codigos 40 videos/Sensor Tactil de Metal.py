import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
TOUCH_SENSOR_PIN = 12  # Pin de entrada del sensor táctil de metal
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/tactiles"
MQTT_CLIENT_ID = "touch_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor táctil como entrada
touch_sensor = Pin(TOUCH_SENSOR_PIN, Pin.IN)

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

def check_touch_sensor():
    """ Función para comprobar el estado del sensor táctil de metal y enviar 1 o 0 """
    sensor_value = touch_sensor.value()  # Lee el estado del sensor (HIGH o LOW)
    print(f"📊 Estado del sensor táctil: {sensor_value}")

    # Publicar 0 si no se toca el sensor (LOW) o 1 si se toca (HIGH)
    client.publish(MQTT_TOPIC, str(sensor_value))  # Publicar 0 o 1 en el tema MQTT

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                check_touch_sensor()  # Comprobar el estado del sensor táctil y enviar el valor
                time.sleep(0.5)  # Comprobar cada medio segundo
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
