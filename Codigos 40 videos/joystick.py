import network
import machine
import time
from umqtt.simple import MQTTClient

# 🔹 Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# 🔹 Configuración MQTT
MQTT_BROKER = "192.168.137.202"  # IP del servidor MQTT
MQTT_TOPIC_X = "prgs/joystick"
MQTT_TOPIC_Y = "prgs/joystick/y"
MQTT_TOPIC_BTN = "prgs/joystick/button"

# 🔹 Pines del joystick
PIN_X = 34  # Eje X (entrada analógica)
PIN_Y = 35  # Eje Y (entrada analógica)
PIN_BTN = 32  # Botón del joystick (entrada digital)

# 🔹 Configurar pines
joy_x = machine.ADC(machine.Pin(PIN_X))
joy_y = machine.ADC(machine.Pin(PIN_Y))
joy_btn = machine.Pin(PIN_BTN, machine.Pin.IN, machine.Pin.PULL_UP)

# Ajustar el rango de lectura
joy_x.width(machine.ADC.WIDTH_10BIT)  # 0 - 1023
joy_y.width(machine.ADC.WIDTH_10BIT)  # 0 - 1023

# Umbrales para convertir en 0 o 1
UMBRAL_BAJO = 400  # Valor bajo del joystick
UMBRAL_ALTO = 600  # Valor alto del joystick

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
                print("❌ No se pudo conectar a Wi-Fi")
                return False
            time.sleep(1)
    print("✅ Conectado a Wi-Fi:", wifi.ifconfig())
    return True

# 🔹 Conectar WiFi
if not conectar_wifi():
    raise Exception("⚠ Error al conectar WiFi")

# 🔹 Configuración de MQTT
try:
    client = MQTTClient("ESP32_Joystick", MQTT_BROKER)
    client.connect()
    print("✅ Conectado a MQTT")
except Exception as e:
    print("❌ Error conectando a MQTT:", e)
    raise

# 🔹 Función para leer y convertir valores a 0 o 1
def leer_joystick():
    val_x = joy_x.read()
    val_y = joy_y.read()
    btn_estado = joy_btn.value()  # 0 si está presionado, 1 si está liberado

    # Convertir valores analógicos en binarios (0 o 1)
    x_bin = 0 if val_x < UMBRAL_BAJO else (1 if val_x > UMBRAL_ALTO else 0)
    y_bin = 0 if val_y < UMBRAL_BAJO else (1 if val_y > UMBRAL_ALTO else 0)

    return x_bin, y_bin, btn_estado

# 🔹 Función para enviar datos por MQTT
def enviar_datos():
    x_bin, y_bin, btn_estado = leer_joystick()
    
    client.publish(MQTT_TOPIC_X, str(x_bin))
    client.publish(MQTT_TOPIC_Y, str(y_bin))
    client.publish(MQTT_TOPIC_BTN, str(btn_estado))

    print(f"📤 Enviado - X: {x_bin}, Y: {y_bin}, Botón: {btn_estado}")

# 🔹 Bucle principal
while True:
    try:
        enviar_datos()  # Leer y enviar valores
        time.sleep(2)  # Ajusta el tiempo de muestreo
    except Exception as e:
        print("❌ Error en el bucle:", e)
