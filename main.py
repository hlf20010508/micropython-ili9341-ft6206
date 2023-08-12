from machine import Pin, SPI, SoftI2C
from ili9341 import Display, color565
from ft6206 import Touch
from time import sleep

CYAN = color565(0, 255, 255)
PURPLE = color565(255, 0, 255)
WHITE = color565(255, 255, 255)

ROTATION = 180

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
display = Display(spi, cs=Pin(5), dc=Pin(2), rst=Pin(4), rotation=ROTATION)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
touch = Touch(i2c, display)

display.draw_text8x8(display.width // 2 - 32,
  display.height - 100,
  "TOUCH ME",
  WHITE,
  background=PURPLE
)

try:
  while True:
    for point in touch.position:
      display.fill_circle(*point, 4, CYAN)
    sleep(0.1)
except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Cleaning up and exiting...")
finally:
    display.cleanup()
