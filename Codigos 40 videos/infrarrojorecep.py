import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
IR_RECEIVER_PIN = 14  # Pin digital donde está conectado el receptor IR
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/infrarrojorecep"
MQTT_CLIENT_ID = "ir_receiver_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configurar el pin del receptor IR como entrada con PULL_UP para estabilidad
ir_receiver = Pin(IR_RECEIVER_PIN, Pin.IN, Pin.PULL_UP)

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

def detectar_senal_ir():
    """
    Función para detectar señales infrarrojas mediante la medición del tiempo de pulso.
    """
    estado = ir_receiver.value()
    if estado == 0:  # Se detecta una señal
        time.sleep(0.01)  # Pequeño delay para evitar detecciones múltiples en una misma señal
        return 1  # Se detectó infrarrojo
    return 0  # No se detectó nada

def enviar_estado():
    """ Función para enviar el estado del receptor IR a MQTT """
    signal_value = detectar_senal_ir()
    
    client.publish(MQTT_TOPIC, str(signal_value))
    print(f"📤 Estado IR enviado: {signal_value}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                enviar_estado()  # Enviar estado del receptor IR
                time.sleep(0.1)  # Ajuste de tiempo para captar mejor señales rápidas
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
