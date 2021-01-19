#!/usr/bin/env python3

import time
import math
import random
import colorsys

from gpiozero import Button
from unicornhatmini import UnicornHATMini

unicornhatmini = UnicornHATMini()
unicornhatmini.set_brightness(0.3)

# Digits as 3x5 pixel elements stored as 15bits
# MSB is top-left, each 5 bits are a column
digits_5x3 = [
    0b111111000111111,  # 0
    0b100011111100001,  # 1
    0b101111010111101,  # 2
    0b101011010111111,  # 3
    0b111000010011111,  # 4
    0b111011010110111,  # 5
    0b111111010100111,  # 6
    0b100001000011111,  # 7
    0b111111010111111,  # 8
    0b111001010011111   # 9
]

R = 0
G = 1
B = 2
Y = 3

key_1 = Button(17)
key_2 = Button(22)
key_3 = Button(6)

class Display():
    """Virtual Simon display class.

    This class wraps an output device (unicornhatmini) and makes it behave like a display
    with four fixed colour lights (Red, Yellow, Blue and Green) and two 3x5 numeric digits.

    """
    def __init__(self, output_device):
        self._output = output_device
        self._width, self._height = self._output.get_shape()
        self._br_red = 0
        self._br_green = 0
        self._br_blue = 0
        self._br_yellow = 0
        self._level = 0
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)
        self._minutes = 0
        self._seconds = 0
        self._digit_left_br = 1.0
        self._digit_right_br = 1.0
        self._digit_left_color = (128, 128, 128)
        self._digit_right_color = (128, 128, 128)

    def _draw_rect(self, x, y, w, h, r, g, b):
        for ry in range(h):
            for rx in range(w):
                self._output.set_pixel(x + rx, y + ry, r, g, b)

    def _draw_digit(self, digit, x, y, r, g, b):
        digit = digits_5x3[digit]
        cols = [
            (digit >> 10) & 0b11111,
            (digit >> 5) & 0b11111,
            (digit) & 0b11111
        ]
        for dx in range(3):
            col = cols[dx]
            for dy in range(5):
                if col & (1 << (4 - dy)):
                    self._output.set_pixel(x + dx, y + dy, r, g, b)

    def clear(self):
        self._output.clear()


    

    def update(self, minutes, seconds):
        self.set_digits(minutes, seconds)
        
        #minute tens digit
        minuteTens = int(self._minutes / 10)
        r, g, b = [int(c * self._digit_left_br) for c in self._digit_left_color]
        self._draw_digit(minuteTens, 1, 1, 249, 82, 255)


        minuteOnes = int(self._minutes % 10)
        r, g, b = [int(c * self._digit_left_br) for c in self._digit_left_color]
        # self._draw_digit(minuteOnes, 5, 1, 81, 168, 255)
        self._draw_digit(minuteOnes, 5, 1, 249, 82, 255)

        secondTens = int(self._seconds / 10)
        r, g, b = [int(c * self._digit_right_br) for c in self._digit_right_color]
        self._draw_digit(secondTens, 9, 1, 5, 255, 161)

        secondOnes = int(self._seconds % 10)
        r, g, b = [int(c * self._digit_right_br) for c in self._digit_right_color]
        # self._draw_digit(secondOnes, 13, 1, 255, 97, 0)
        self._draw_digit(secondOnes, 13, 1, 5, 255, 161)

        self._draw_colon(255, 0, 0)
        
        self._output.show()

        

    def _draw_colon(self, r, g, b):
        self._output.set_pixel(8, 2, r, g, b)
        self._output.set_pixel(8, 4, r, g, b)

    def set_light_brightness(self, red, green, blue, yellow):
        self._br_red = red
        self._br_green = green
        self._br_blue = blue
        self._br_yellow = yellow

    def set_digits(self, minutes, seconds):
        self._minutes = minutes
        self._seconds = seconds

    def set_digit_brightness(self, left, right):
        self._digit_left_br = left
        self._digit_right_br = right

    def set_digit_color(self, left, right):
        self._digit_left_color = left
        self._digit_right_color = right


class Timer():

    def __init__(self, display):
        self._display = display
        self._display.set_digits(5, 1)
        curTime = time.time()
        self._display.set_light_brightness(
            1, 1, 1, 1
            # self._pulse(curTime / 2),
            # self._pulse((curTime + 0.25) / 2),
            # self._pulse((curTime + 0.5) / 2),
            # self._pulse((curTime + 0.75) / 2)
        )
        self._seconds = 0
        self._minutes = 0
        self._timerCount = 0


    def _pulse(self, time):
        """Helper to produce a sine wave with a period of 1sec"""
        return (math.sin(time * 2 * math.pi - (math.pi / 2)) + 1) / 2.0

    def _hue(self, h):
        """Helper to return an RGB colour from HSV"""
        return tuple([int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)])

    def key_1(self):
        self._minutes += 1
        # print("{}x{}".format(self._minutes, self._seconds))

    def key_2(self):
        self._seconds += 30

        # increase minutes instead if over 60 seconds
        if self._seconds / 60 > 1:
            self._seconds -= 60
            self._minutes += 1
    
    def key_3(self):
        self._seconds = 0
        self._minutes = 0

    def update(self): 
        self._display.update(self._minutes, self._seconds)
        self._timerCount += 1
        if self._timerCount % 20 == 0:
            self._timerCount = 0
            if self._seconds > 0:
                self._seconds -= 1
            elif ((self._seconds == 0) and (self._minutes > 0)):
                self._minutes -= 1
                self._seconds = 59


        # curTime = time.time()
        # self._display.set_digit_brightness(
        #     self._pulse(curTime),
        #     self._pulse(curTime)
        # )
        # self._display.set_digit_color(
        #     self._hue(186),
        #     self._hue(100.44)
        # )

display = Display(output_device=unicornhatmini)
timer = Timer(display)

key_1.when_pressed = timer.key_1
key_2.when_pressed = timer.key_2
key_3.when_pressed = timer.key_3

while True:
    display.clear()
    timer.update()
    time.sleep(1.0 / 20)










