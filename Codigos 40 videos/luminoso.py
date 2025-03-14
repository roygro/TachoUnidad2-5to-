import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
TILT_SENSOR_PIN = 14  # Pin digital donde está conectado el sensor de inclinación
LED_PIN = 13  # Pin digital donde está conectado el LED
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/inclinacionlumi<"
MQTT_CLIENT_ID = "tilt_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del sensor de inclinación como entrada con PULL_UP
tilt_sensor = Pin(TILT_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
# Configurar el pin del LED como salida
led = Pin(LED_PIN, Pin.OUT)
led.value(0)  # Inicialmente apagado

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
    """ Función para enviar el estado del sensor de inclinación a MQTT """
    sensor_state = tilt_sensor.value()  # 0 = inclinado, 1 = estable (horizontal)
    tilt_value = 1 if sensor_state == 1 else 0  # 1 cuando está en estado estable (horizontal)
    
    # Enviar el valor a MQTT
    client.publish(MQTT_TOPIC, str(tilt_value))
    print(f"📤 Estado del sensor de inclinación enviado: {tilt_value}")

    # Encender el LED si está en posición horizontal, apagar si está inclinado
    if tilt_value == 1:
        led.value(1)  # Encender LED cuando está en posición estable
    else:
        led.value(0)  # Apagar LED cuando está inclinado

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                enviar_estado()  # Enviar estado del sensor de inclinación
                time.sleep(1)  # Ajuste de tiempo para obtener lecturas constantes
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
