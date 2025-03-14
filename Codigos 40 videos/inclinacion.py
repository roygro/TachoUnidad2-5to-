import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi
wifi_ssid = "LOREDO LAP"  # Cambia por tu SSID
wifi_password = "u55/5B85"  # Cambia por tu contraseña

# Configuración MQTT
mqtt_broker = "192.168.137.202"  # IP del broker MQTT
mqtt_port = 1883 
mqtt_topic = "prgs/inclinacion"  # Tema donde se publicarán los datos
mqtt_client_id = "sensor_{}".format(int(time.time()))  # ID único

# Configuración del sensor de inclinación y LED
SENSOR_PIN = 12  # Pin del sensor de inclinación
LED_PIN = 13  # Pin del LED

sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Sensor con pull-up interno
led = Pin(LED_PIN, Pin.OUT)  # LED como salida

# Conexión Wi-Fi con manejo de errores
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        
        timeout = 10  # Esperar hasta 10 segundos para la conexión
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print('Conexión Wi-Fi exitosa:', wlan.ifconfig())
    else:
        print("Error: No se pudo conectar a Wi-Fi")
        return False
    return True

# Conexión MQTT con manejo de errores
def connect_mqtt():
    try:
        client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        return None

# Enviar datos del sensor de inclinación por MQTT solo si cambian
def publish_data(client, last_state):
    if client is None:
        print("MQTT no está conectado")
        return last_state

    try:
        state = sensor.value()  # Leer el estado del sensor (0 o 1)

        # Encender o apagar el LED según el estado del sensor
        led.value(0 if state == 1 else 1)

        if state != last_state:
            payload = "{}".format(state)  # Enviar solo 0 o 1
            client.publish(mqtt_topic, payload)
            print("Estado enviado:", payload)
            return state  # Actualizar el último valor enviado
        else:
            print("Estado sin cambios, no se envía")
            return last_state
    except Exception as e:
        print("Error al leer el sensor:", e)
        return last_state

# Main
if connect_wifi():  # Conectar a Wi-Fi
    client = connect_mqtt()  # Conectar a MQTT
    last_state = None  # Último estado medido

    while True:
        last_state = publish_data(client, last_state)  # Enviar datos solo si cambia
        time.sleep(2)  # Leer cada 2 segundos
else:
    print("No se pudo establecer conexión Wi-Fi. Reinicia el dispositivo.")