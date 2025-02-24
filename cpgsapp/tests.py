from gpiozero import LED
from time import sleep

led = LED(17)  # Use GPIO pin 17

while True:
    led.on()  # Turn ON
    sleep(1)
    led.off()  # Turn OFF
    sleep(1)
