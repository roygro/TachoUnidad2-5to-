import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de la fotoresistencia y conexión
LDR_PIN = 34           # Pin para la fotoresistencia (ajustar si es necesario)
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/fotoresistencia"  # Tópico de MQTT para enviar datos del LDR
MQTT_CLIENT_ID = "ldr_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración de la fotoresistencia (LDR) usando un pin analógico
ldr_sensor = ADC(Pin(LDR_PIN))  # Usando un pin analógico para leer el valor
ldr_sensor.width(ADC.WIDTH_10BIT)  # Configuración de 10 bits para mayor resolución
ldr_sensor.atten(ADC.ATTN_0DB)  # Rango de 0 a 1.1V

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

def read_ldr():
    """ Función para leer el valor de la fotoresistencia (LDR) """
    ldr_value = ldr_sensor.read()
    print(f"📊 Valor de la LDR: {ldr_value}")
    
    # Puedes realizar algún procesamiento del valor aquí, como normalizarlo o filtrarlo si es necesario.
    return ldr_value

def send_ldr_status(client, value):
    """ Función para enviar el estado del LDR al broker MQTT """
    try:
        # Publicar el valor del LDR
        client.publish(MQTT_TOPIC, str(value))
        print(f"📤 Mensaje enviado: {value}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                # Leer el valor de la fotoresistencia y enviarlo
                ldr_value = read_ldr()
                send_ldr_status(client, ldr_value)
                time.sleep(2)  # Retardo entre lecturas del sensor
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
