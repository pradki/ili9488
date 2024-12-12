import time
import machine
import random
import fb2rgb
from machine import Pin, SPI

#from ili9488gpt import ILI9488
from ili9488 import ILI9488
from xpt2046 import XPT2046

# https://nettigo.pl/products/wyswietlacz-lcd-tft-3-5-ze-sterownikiem-ili9488-dotykowy

spi = machine.SPI(1, baudrate=10_000_000, polarity=0, phase=0, bits=8, firstbit=0, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12))
cs = machine.Pin(5)
dc = machine.Pin(16)
rst = machine.Pin(17)

display = ILI9488(spi, cs, dc, rst)
display.mem_access_ctrl(my=0, mx=0, mv=1, ml=0, brg=1, mh=0)
#(my=1, mx=1, mv=1, ml=1, brg=None, mh=1)

miso = Pin(42)
mosi = Pin(41)
sck = Pin(6)
spi = SPI(2, baudrate=2_000_000, sck=sck, mosi=mosi, miso=miso)
cs = Pin(7, Pin.OUT)
irq = Pin(8, Pin.IN, Pin.PULL_UP)

touch = XPT2046(spi, cs, irq)

display.draw_rectangle(0, 0, 32, 48, 0xFFFF00)
display.draw_rectangle(160, 160, 80, 80, 0x00FF00)
display.draw_rectangle(310, 220, 80, 80, 0x0000FF)

import random
tb = time.time()
for x in range(10):
    scale_v = 2
    scale_h = 5
    r = random.randint(0, 0x7FFFFFFF)
    text = f'{scale_v}:{scale_h} {r:010d}'
    display.text(text, 10, 10, 'rgb', 'rgb', scale_v, scale_h)
#    buffer_c = fb2rgb.fb2rgb_rot(text, 'rgb', 'rgb', scale_v, scale_h)
#    display.draw_framebuf(buffer_c, 10, 10, len(text)*8*scale_v, 8*scale_h, 0x777777)

    scale_v = 1
    scale_h = 3
    text = f'{scale_v}:{scale_h} {x:010d}'
    display.text(text, 10, 120, 'rgb', 'rgb', scale_v, scale_h)
#    buffer_c = fb2rgb.fb2rgb_rot(text, 'rgb', 'rgb', scale_v, scale_h)
#    display.draw_framebuf(buffer_c, 10, 100, len(text)*8*scale_v, 8*scale_h, 0x777777)

te = time.time()

print(f'end: {te-tb}')

# display.draw_rectangle(250, 250, 290, 290, 0xF000)
# display.draw_rectangle(260, 260, 300, 300, 0x0FC0)
# display.draw_rectangle(110, 110, 150, 150, 0x003F)
# display.write_9bit_data(bytearra


# Narysowanie czerwonego piksela w środku ekranu
# display.draw_pixel(160, 120, 0xF800)

print(display.read_display_id_info().hex().upper())
print('color', display.read_data(0x0c, 6))

print('random')
# display.fill_screen(0xF800)  # Czerwony
print('end')

display.fill_screen(0x000000)

scale_v = 1
scale_h = 3
        
while True:
    time.sleep(0.1)
    if touch.ready:
        x, y = touch.get_pos()
        
        if -1 in [x, y]:
            continue
        # testgpt.display.draw_pixel(x, y, 0x00FF00)
        display.draw_rectangle(x, y, 8, 8, 0x00FF00)
        text = f'{scale_v}:{scale_h} x:{x:03d} y:{y:03d}   '

        display.text(text, 120, 80, 'rgb', 'rgb', scale_v, scale_h)
# end.