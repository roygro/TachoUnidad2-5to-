import network
import machine
import time
from umqtt.simple import MQTTClient

# 🔹 Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# 🔹 Configuración MQTT
MQTT_BROKER = "192.168.137.202"  # IP del servidor MQTT
MQTT_TOPIC = "prgs/ledrgb7"

# 🔹 Configuración de los pines del módulo LED de 3 colores
PIN_ROJO = 25   # GPIO para el color rojo
PIN_VERDE = 26  # GPIO para el color verde
PIN_AZUL = 27   # GPIO para el color azul

# Configurar los pines en modo salida
led_rojo = machine.Pin(PIN_ROJO, machine.Pin.OUT)
led_verde = machine.Pin(PIN_VERDE, machine.Pin.OUT)
led_azul = machine.Pin(PIN_AZUL, machine.Pin.OUT)

# 🔹 Función para conectar WiFi
def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("🔄 Conectando a WiFi...")
        wifi.connect(SSID, PASSWORD)
        tiempo_inicio = time.time()
        while not wifi.isconnected():
            if time.time() - tiempo_inicio > 10:
                print("❌ No se pudo conectar a WiFi")
                return False
            time.sleep(1)
    print("✅ Conectado a WiFi:", wifi.ifconfig())
    return True

# 🔹 Conectar WiFi
if not conectar_wifi():
    raise Exception("⚠ Error al conectar WiFi")

# 🔹 Configuración de MQTT
try:
    client = MQTTClient("ESP32_LED3C", MQTT_BROKER)
    client.connect()
    print("✅ Conectado a MQTT")
except Exception as e:
    print("❌ Error conectando a MQTT:", e)
    raise

# 🔹 Función para cambiar el color del LED
def cambiar_color(rojo, verde, azul, codigo):
    led_rojo.value(rojo)
    led_verde.value(verde)
    led_azul.value(azul)
    client.publish(MQTT_TOPIC, str(codigo))  # Envía un número como cadena
    print(f"📤 Enviado - Código de color: {codigo}")

# 🔹 Secuencia de colores con códigos numéricos
colores = [
    (1, 0, 0, 1),  # Rojo
    (0, 1, 0, 2),  # Verde
    (0, 0, 1, 3),  # Azul
    (1, 1, 0, 4),  # Amarillo
    (0, 1, 1, 5),  # Cian
    (1, 0, 1, 6),  # Magenta
    (1, 1, 1, 7),  # Blanco
    (0, 0, 0, 0)   # Apagado
]

# 🔹 Bucle principal
while True:
    try:
        for r, g, b, codigo in colores:
            cambiar_color(r, g, b, codigo)
            time.sleep(2)  # Espera 2 segundos entre cambios
    except Exception as e:
        print("❌ Error en el bucle:", e)