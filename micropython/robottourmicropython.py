#for the raspberry pi pico family of devices running micropython

from machine import Pin, PWM
from time import sleep, sleep_us
import time
trig = Pin(7, Pin.OUT)
echo = Pin(8, Pin.IN)

def distance_cm():
    # Send a 10 nanosecond pulse
    trig.low()
    sleep_us(2)
    trig.high()
    sleep_us(10)
    trig.low()

    # Wait for echo pulse
    while echo.value() == 0:
        pass
    start = time.ticks_us()
    while echo.value() == 1:
        pass
    end = time.ticks_us()

    dur = end - start
    # Sound speed: 343 m/s → 0.0343 cm/µs. Divide by 2 for round trip.
    return (dur * 0.0343) / 2

in1A = Pin(4, Pin.OUT)
in2A = Pin(5, Pin.OUT)
pwmA = PWM(Pin(6))
pwmA.freq(1000)

in1B = Pin(9, Pin.OUT)
in2B = Pin(10, Pin.OUT)
pwmB = PWM(Pin(11))
pwmB.freq(1000)

def set_duty(pwm_obj, value):  # 0–1023 range
    try:
        pwm_obj.duty(value)
    except AttributeError:
        pwm_obj.duty_u16(int(value * 64))

def motorA_forward(speed=800):
    in1A.value(1)
    in2A.value(0)
    set_duty(pwmA, speed)

def motorA_reverse(speed=800):
    in1A.value(0)
    in2A.value(1)
    set_duty(pwmA, speed)

def motorA_stop():
    in1A.value(0)
    in2A.value(0)
    set_duty(pwmA, 0)

def motorB_forward(speed=800):
    in1B.value(1)
    in2B.value(0)
    set_duty(pwmB, speed)

def motorB_reverse(speed=800):
    in1B.value(0)
    in2B.value(1)
    set_duty(pwmB, speed)

def motorB_stop():
    in1B.value(0)
    in2B.value(0)
    set_duty(pwmB, 0)

try:
    if distance_cm() > 10:
        motorA_forward(800)
        motorB_forward(800)
        print(distance_cm())
    else:
        motorA_stop()
        motorB_stop()
except KeyboardInterrupt:
    motorA_stop()
    motorB_stop()


