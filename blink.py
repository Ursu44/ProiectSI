import machine
import utime
import dht

dht_pin = machine.Pin(0)  
led_pin_albastru = machine.Pin(13, machine.Pin.OUT)
led_pin_rosu = machine.Pin(14, machine.Pin.OUT)

# Creare obiect DHT
dht_sensor = dht.DHT11(dht_pin)

def read_temperature_humidity():
    dht_sensor.measure()  # Efectuează măsurătorile

    temperature_celsius = dht_sensor.temperature()
    humidity_percentage = dht_sensor.humidity()

    return temperature_celsius, humidity_percentage

while True:
    temperature, humidity = read_temperature_humidity()

    print("Temperatura (Celsius): {:.1f} °C".format(temperature))
    print("Umiditate: {:.1f}%".format(humidity))
    
    uart.write("{:.1f}\n".format(temperature))
    
    if temperature<= 32 and temperature >= 19:
        led_pin_albastru.value(0)
        led_pin_rosu.value(0)
        print("da3")
    elif temperature>32:
        led_pin_albastru.value(1)
        led_pin_rosu.value(0)
        print("da1")
    elif temperature < 19:
        led_pin_rosu.value(1)
        led_pin_albastru.value(0)
        print("da2")
    utime.sleep(0.8)
