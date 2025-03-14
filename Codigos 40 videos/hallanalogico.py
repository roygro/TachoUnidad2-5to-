import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
HALL_SENSOR_PIN = 34  # Pin analógico donde está conectado el sensor de efecto Hall
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/hallanalogico"
MQTT_CLIENT_ID = "hall_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor de efecto Hall como entrada analógica
hall_sensor = ADC(Pin(HALL_SENSOR_PIN))  # Crea el ADC en el pin analógico
hall_sensor.atten(ADC.ATTN_11DB)  # Cambiar a atenuación de 11db (rango de 0-3.6V)
hall_sensor.width(ADC.WIDTH_12BIT)  # Resolución de 12 bits

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
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(MQTT_TOPIC)
        print("✅ Conectado a MQTT y suscrito a:", MQTT_TOPIC)
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def mqtt_callback(topic, msg):
    """ Función que se ejecuta cuando se recibe un mensaje MQTT """
    mensaje = msg.decode("utf-8").strip().lower()
    print(f"📩 Mensaje recibido en {topic}: {mensaje}")

def enviar_estado():
    """ Función para enviar el estado del sensor de efecto Hall a MQTT """
    sensor_value = hall_sensor.read()  # Leer el valor analógico del sensor de Hall
    print(f"📊 Valor del sensor de Hall: {sensor_value}")

    # Enviar el valor a MQTT
    client.publish(MQTT_TOPIC, str(sensor_value))
    print(f"📤 Valor del sensor de Hall enviado: {sensor_value}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                enviar_estado()  # Enviar estado del sensor de Hall
                time.sleep(1)  # Ajuste de tiempo para obtener lecturas constantes
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
