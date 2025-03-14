import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor de temperatura y conexión
TEMP_PIN = 34            # Pin para el sensor de temperatura (ajustar si es necesario)
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/temperaturaana"  # Tópico de MQTT para enviar datos del sensor de temperatura
MQTT_CLIENT_ID = "temp_sensor_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del sensor de temperatura (usando un pin analógico)
temp_sensor = ADC(Pin(TEMP_PIN))  # Usando un pin analógico para leer el valor
temp_sensor.width(ADC.WIDTH_10BIT)  # Configuración de 10 bits para mayor resolución
temp_sensor.atten(ADC.ATTN_0DB)  # Rango de 0 a 1.1V

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

def read_temp():
    """ Función para leer el valor del sensor de temperatura KY-013 """
    raw_value = temp_sensor.read()  # Leer el valor analógico
    voltage = raw_value * (3.3 / 1023)  # Convertir el valor a voltaje (3.3V para ESP32)
    
    # Convertir el voltaje a temperatura en grados Celsius para el KY-013
    temperature = voltage * 100  # El KY-013 entrega 10mV por cada grado Celsius
    
    # Redondear la temperatura a un número entero
    temperature_int = int(temperature)  # Convertir a número entero (sin decimales)
    
    print(f"📊 Temperatura: {temperature_int}°C")
    
    return temperature_int

def send_temp_status(client, value):
    """ Función para enviar el estado de la temperatura al broker MQTT """
    try:
        # Publicar el valor de la temperatura
        client.publish(MQTT_TOPIC, str(value))
        print(f"📤 Mensaje enviado: {value}°C")
    except Exception as e:
        print(f"❌ Error al enviar mensaje MQTT: {e}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                # Leer el valor de la temperatura y enviarlo
                temp_value = read_temp()
                send_temp_status(client, temp_value)
                time.sleep(2)  # Retardo entre lecturas del sensor
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
