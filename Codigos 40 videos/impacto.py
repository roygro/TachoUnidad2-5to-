import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor de impacto y conexión
SENSOR_PIN = 34         # Pin para el sensor de impacto (ajustar si es necesario)
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/impacto"  # Tópico de MQTT para enviar datos del sensor
MQTT_CLIENT_ID = "impact_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del sensor de impacto (ej. usando un pin analógico)
sensor = ADC(Pin(SENSOR_PIN))  # Usando un pin analógico para leer el valor
sensor.width(ADC.WIDTH_10BIT)  # Configuración de 10 bits para mayor resolución
sensor.atten(ADC.ATTN_0DB)  # Rango de 0 a 1.1V

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

def read_impact():
    """ Función para leer los valores del sensor de impacto """
    # Leemos el valor del sensor
    sensor_value = sensor.read()
    print(f"📊 Valor del sensor: {sensor_value}")
    
    # Umbral para determinar si hay impacto o no
    threshold = 100  # Ajusta este valor según el comportamiento de tu sensor
    if sensor_value > threshold:
        print("⚠️ ¡Impacto detectado!")
        return 0  # Si hay impacto, enviamos 1
    else:
        print("🔇 No hay impacto")
        return 1  # Si no hay impacto, enviamos 0

def send_impact_status(client, status):
    """ Función para enviar el estado del sensor de impacto al broker MQTT """
    try:
        # Publicar el estado del sensor (1 para impacto, 0 para sin impacto)
        client.publish(MQTT_TOPIC, str(status))
        print(f"📤 Mensaje enviado: {status}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                # Leer el valor del sensor de impacto y enviar el estado
                impact_status = read_impact()
                send_impact_status(client, impact_status)
                time.sleep(2)  # Retardo entre lecturas del sensor
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
