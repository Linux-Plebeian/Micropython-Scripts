import machine
import time
from machine import Pin, I2C
from  ssd1306 import SSD1306_I2C
import framebuf
import sys
import ap
import images
import BUTCANITRUNDOOM
from machine import ADC
width = 128
height = 64
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
oled = SSD1306_I2C(width, height, i2c)
devices = i2c.scan()
print("I2C devices found:", [hex(device) for device in devices])
button_left = Pin(16, Pin.IN, Pin.PULL_DOWN)
button_submit = Pin(18, Pin.IN, Pin.PULL_DOWN)
button_right = Pin(21, Pin.IN, Pin.PULL_DOWN)
temp_sensor = ADC(4)
cursor_x = 5
cursor_y = 8
cursor_size = 8
line_spacing = 12
FB_ICO_TEMP = framebuf.FrameBuffer(images.ICO_TEMP, 8, 8, framebuf.MONO_HLSB)
FB_ICO_RASPI = framebuf.FrameBuffer(images.ICO_RASPI,8,8, framebuf.MONO_HLSB)
FB_ICO_PHONE = framebuf.FrameBuffer(images.ICO_PHONE,8,8, framebuf.MONO_HLSB)
FB_RASPI_BIG = framebuf.FrameBuffer(images.RasPi,64,64, framebuf.MONO_HLSB)
FB_ICO_GAME = framebuf.FrameBuffer(images.ICO_GAME,8,8, framebuf.MONO_HLSB)
oled.fill(1)
oled.blit(FB_RASPI_BIG, 32, 0 )
oled.show()
time.sleep(1)
while 1:
    oled.fill(0)

    time.sleep(0.1)
    if button_left.value():
        cursor_y-=line_spacing
    elif button_right.value():
        cursor_y+=line_spacing
    elif button_submit.value():
        if cursor_y == 8:
            ap.start(oled, button_left, button_submit, button_right)
        elif cursor_y == 20:
            adc_value = temp_sensor.read_u16()
            # Convert ADC value to voltage
            voltage = adc_value * (3.3 / 65535.0)
            # Temperature calculation based on sensor characteristics
            celsius = 27 - (voltage - 0.706) / 0.001721
            str
            StrCelsius= str(celsius)
            oled.fill(0)
            oled.text("CPU TEMP: ", 0, 0)
            for i in range(0, 120, 10):
                oled.blit(FB_ICO_TEMP,i,40,0)
            oled.text(f"{StrCelsius} C", 0, 20) 
            oled.show()
            time.sleep(2)
            

        elif cursor_y == 32:
            import pong
            import fake   
        elif cursor_y == 44:
            BUTCANITRUNDOOM.main(oled)
    oled.text(">" , cursor_x, cursor_y)
    oled.text("RASPI MS", cursor_x+cursor_size, 8)
    oled.blit(FB_ICO_RASPI,120,8,0)
    oled.text("CPU TEMP", cursor_x+cursor_size, 20)
    oled.blit(FB_ICO_TEMP,120,20,0)
    oled.text("GAME", cursor_x+cursor_size , 32)
    oled.blit(FB_ICO_GAME,120,32,0)
    oled.text("DOOM", cursor_x+cursor_size , 44)
    oled.blit(FB_ICO_GAME,120,44,0)
    if cursor_y > 64:
        oled.scroll(0, -12)
    if cursor_y < 0:
        oled.scroll(0,12)

    oled.show()
