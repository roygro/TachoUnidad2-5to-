import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración del LED RGB y la conexión MQTT
RED_PIN = 14  # Pin GPIO para controlar el LED rojo
GREEN_PIN = 12  # Pin GPIO para controlar el LED verde
BLUE_PIN = 13  # Pin GPIO para controlar el LED azul
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/rgbled"  # Tópico de MQTT para controlar el LED RGB
MQTT_CLIENT_ID = "rgb_led_control_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración de los pines para controlar el LED RGB con PWM
red_led = PWM(Pin(RED_PIN), freq=1000)  # PWM en el pin rojo
green_led = PWM(Pin(GREEN_PIN), freq=1000)  # PWM en el pin verde
blue_led = PWM(Pin(BLUE_PIN), freq=1000)  # PWM en el pin azul

# Función para conectar a Wi-Fi
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

# Función para conectar a MQTT
def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

# Función para controlar el color del LED RGB
def control_rgb_led(red, green, blue):
    """Controla el color del LED RGB mediante PWM (0 a 1023)"""
    red_led.duty(1023 - red)  # PWM inverso para el rojo (encender con valor bajo)
    green_led.duty(1023 - green)  # PWM inverso para el verde
    blue_led.duty(1023 - blue)  # PWM inverso para el azul
    print(f"📊 LED Rojo: {red}, Verde: {green}, Azul: {blue}")

# Función para recibir los comandos de MQTT y ajustar el color del LED
def handle_mqtt_message(topic, msg):
    """Función para manejar los mensajes recibidos de MQTT"""
    print(f"📥 Mensaje recibido en {topic}: {msg.decode()}")
    try:
        # Esperar un mensaje con los valores RGB (ejemplo: "255,0,0" para rojo)
        red, green, blue = map(int, msg.decode().split(','))
        control_rgb_led(red, green, blue)  # Cambiar el color del LED RGB
    except ValueError:
        print("❌ Error: El mensaje recibido no tiene el formato correcto.")

# Función para enviar el estado del LED RGB a través de MQTT
def send_rgb_status(client, value):
    """ Función para enviar el estado del LED RGB al broker MQTT """
    try:
        client.publish(MQTT_TOPIC, str(value))
        print(f"📤 Mensaje enviado: {value}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

# Conectar a Wi-Fi y MQTT
if connect_wifi():
    client = connect_mqtt()
    if client:
        client.set_callback(handle_mqtt_message)  # Establecer la función de callback para manejar mensajes
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tópico de MQTT
        while True:
            try:
                client.check_msg()  # Comprobar si hay nuevos mensajes en el tópico
                time.sleep(1)  # Esperar un segundo antes de la siguiente lectura
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
