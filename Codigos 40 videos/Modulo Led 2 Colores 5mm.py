import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de los pines para controlar el LED de dos colores
RED_LED_PIN = 14  # Pin GPIO al que está conectado el LED rojo
GREEN_LED_PIN = 12  # Pin GPIO al que está conectado el LED verde
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/led"  # Tópico de MQTT para controlar el LED
MQTT_CLIENT_ID = "led_control_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración de los pines para controlar el LED de dos colores
red_led = Pin(RED_LED_PIN, Pin.OUT)  # Pin para LED rojo
green_led = Pin(GREEN_LED_PIN, Pin.OUT)  # Pin para LED verde

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

def control_led(command):
    """ Función para controlar el LED de dos colores """
    if command == 1:
        red_led.on()  # Encender el LED rojo
        green_led.off()  # Apagar el LED verde
        print("📊 LED Rojo encendido")
    elif command == 2:
        red_led.off()  # Apagar el LED rojo
        green_led.on()  # Encender el LED verde
        print("📊 LED Verde encendido")
    elif command == 0:
        red_led.off()  # Apagar el LED rojo
        green_led.off()  # Apagar el LED verde
        print("📊 LED apagado")

def send_led_status(client, value):
    """ Función para enviar el estado del LED al broker MQTT """
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
                # Leer el estado del LED y enviarlo
                # Por ejemplo, puedes controlar el LED de manera manual con valores de prueba
                led_value = 1  # 1 para rojo, 2 para verde, 0 para apagado
                control_led(led_value)
                send_led_status(client, led_value)
                time.sleep(2)  # Esperar antes de cambiar el estado del LED
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
