
from ssd1306 import SSD1306_I2C
import framebuf
import time
import random
import rp2
import sys
from machine import Pin, I2C, ADC
button_left = Pin(16, Pin.IN, Pin.PULL_DOWN)
button_submit = Pin(18, Pin.IN, Pin.PULL_DOWN)
button_right = Pin(21, Pin.IN, Pin.PULL_DOWN)
width = 128
height = 64
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
oled = SSD1306_I2C(width, height, i2c)


#game
x=1
y=1
vx=3
vy=2
sizex=5
sizey=5
psizex=20
psizey=5
posx=1
posy=58
pspeed=4
score=0
strscore=str(score)
ICO_RASPI = bytearray([0b01010110,
                       0b00111100,
                       0b0010110,
                       0b01010110,
                       0b01101010,
                       0b01010110,
                       0b00101100,
                       0b00011000])
FB_ICO_RASPI = framebuf.FrameBuffer(ICO_RASPI,8,8, framebuf.MONO_HLSB)
while True:
    oled.fill(0)
    strscore=str(score)
    oled.text(strscore,1,1)
    oled.text("___", posx, posy-4)
    oled.blit(FB_ICO_RASPI,x,y,0)
    oled.show()
    x+=vx
    y+=vy
    if button_left.value():
        posx-=4
    if button_right.value():
        posx+=4
    if button_submit.value():
        sys.exit()
    if y>63-sizey:
        y=63-sizey
        vy=-vy
        score-=100
    if y<1:
        y=1
        vy=-vy
    if x>127-sizex:
        x=127-sizex
        vx=-vx
    if x<1:
        x=1
        vx=-vx
    
    if y<=posy and y>=posy-psizey and x > posx and x < posx+psizex:
        y=posy-psizey
        vy=-vy
        score+=100
    if score<-1:
        sys.exit()
    if posx < 1:
        posx=1
    if posx > 127-psizex:
        posx=127-psizex


