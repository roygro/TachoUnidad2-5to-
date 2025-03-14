import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
RED_PIN = 12           # Pin para el color rojo del LED
GREEN_PIN = 13         # Pin para el color verde del LED
BLUE_PIN = 14          # Pin para el color azul del LED
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/ledrgb7"  # Tópico de MQTT
MQTT_CLIENT_ID = "rgb_led_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración de los pines PWM para el control de los colores del LED RGB
red_pwm = PWM(Pin(RED_PIN), freq=1000, duty=0)
green_pwm = PWM(Pin(GREEN_PIN), freq=1000, duty=0)
blue_pwm = PWM(Pin(BLUE_PIN), freq=1000, duty=0)

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
    
    try:
        color = int(mensaje)  # Convertir el mensaje a un valor entero
        set_led_color(color)
    except ValueError:
        print("❌ Error: El mensaje debe ser un número entero para el color.")

def set_led_color(color):
    """ Función para controlar el color del LED RGB con valores numéricos enteros """
    # Usamos valores enteros para definir los colores
    if color == 1:
        # Rojo
        red_pwm.duty(1023)
        green_pwm.duty(0)
        blue_pwm.duty(0)
        print("🔴 LED Rojo encendido")
    elif color == 2:
        # Verde
        red_pwm.duty(0)
        green_pwm.duty(1023)
        blue_pwm.duty(0)
        print("🟢 LED Verde encendido")
    elif color == 3:
        # Azul
        red_pwm.duty(0)
        green_pwm.duty(0)
        blue_pwm.duty(1023)
        print("🔵 LED Azul encendido")
    elif color == 4:
        # Blanco (Rojo + Verde + Azul)
        red_pwm.duty(1023)
        green_pwm.duty(1023)
        blue_pwm.duty(1023)
        print("⚪ LED Blanco encendido")
    else:
        print("❌ Color no válido. Usa números: 1 para Rojo, 2 para Verde, 3 para Azul, 4 para Blanco.")

def send_led_status(client):
    """ Función para enviar el estado del LED al broker MQTT """
    try:
        # Publicar el estado del LED
        message = "LED is set"
        client.publish(MQTT_TOPIC, message)
        print(f"📤 Mensaje enviado: {message}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                send_led_status(client)  # Enviar estado del LED
                client.check_msg()       # Escuchar mensajes MQTT
                time.sleep(2)            # Pequeño retraso
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
