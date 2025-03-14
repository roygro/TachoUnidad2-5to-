import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
DT_PIN = 12  # Pin Data del encoder (DT)
CLK_PIN = 14  # Pin Clock del encoder (CLK)
SW_PIN = 16   # Pin Switch del encoder (SW), si deseas usarlo
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/encoder"
MQTT_CLIENT_ID = "encoder_sensor_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Variables para el estado del encoder
encoder_position = 0  # Posición del encoder

# Configuración de pines del encoder
dt_pin = Pin(DT_PIN, Pin.IN, Pin.PULL_UP)  # Pin Data (DT) del encoder
clk_pin = Pin(CLK_PIN, Pin.IN, Pin.PULL_UP)  # Pin Clock (CLK) del encoder
sw_pin = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)  # Pin Switch (SW) del encoder

# Función para detectar el cambio en el encoder
def encoder_callback(pin):
    global encoder_position
    # Lee el estado del pin CLK para determinar la dirección
    if dt_pin.value() == 0:
        encoder_position += 1  # Gira en una dirección
    else:
        encoder_position -= 1  # Gira en la otra dirección

# Función para detectar el botón presionado (SW)
def button_callback(pin):
    if pin.value() == 0:  # Si el botón está presionado
        print("🔘 Botón presionado")

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

def send_encoder_position():
    """ Publicar la posición actual del encoder en MQTT """
    print(f"📊 Posición del encoder: {encoder_position}")
    client.publish(MQTT_TOPIC, str(encoder_position))

# Configuración de interrupciones para detectar el cambio en el encoder y el botón
dt_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)  # Interrupción para el encoder
sw_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)  # Interrupción para el botón

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                send_encoder_position()  # Enviar la posición del encoder
                time.sleep(1)  # Enviar cada segundo
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
