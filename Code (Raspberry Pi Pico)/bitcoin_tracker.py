# Darth Vader IoT Cryptocurrency Tracker and Display w/ Pico
#
# Raspberry Pi Pico
#
# By Kutluhan Aktar
#
# Monitor real-time cryptocurrency data and get notified when there is a price depletion or surge
# with Raspberry Pi Pico and ESP8266 ESP-01.
#
# For more information:
# https://www.theamplituhedron.com/projects/Darth_Vader_IoT_Cryptocurrency_Tracker_and_Display_w_Pico/

from machine import Pin, PWM, ADC, SPI, UART
from time import sleep
import st7789py as st7789
import vga1_16x16 as normal
import vga1_bold_16x32 as bold
import json

# Define the 'cryptocurrency_tracker' class and its functions:
class cryptocurrency_tracker:
    def __init__(self, sck=10, mosi=11, res=12, dc=13, width=240, height=240):
        # Define the UART settings:
        # RX and TX are swapped, meaning Pico TX goes to ESP-01 RX and vice versa.
        self.uart0 = UART(0, rx=Pin(17), tx=Pin(16), baudrate=115200, rxbuf=1024, timeout=2000)
        self.coin_data = 0
        # Define the ST7789 display settings:
        spi = SPI(1, baudrate=40000000, polarity=1)
        self.display = st7789.ST7789(spi, width, height, reset=Pin(res, Pin.OUT), dc=Pin(dc, Pin.OUT))
        # Define the RGB LED settings:
        self.red = PWM(Pin(22))
        self.green = PWM(Pin(21))
        self.blue = PWM(Pin(20))
        self.red.freq(1000) 
        self.green.freq(1000)
        self.blue.freq(1000)
        # Define the buzzer:
        self.buzzer = PWM(Pin(15))
        self.buzzer.freq(450)
        # Define the controls:
        self.joystick_x = ADC(Pin(26))
        self.joystick_y = ADC(Pin(27))
        self.joystick_sw = Pin(19, Pin.IN, Pin.PULL_UP)
        self.exit_button = Pin(14, Pin.IN, Pin.PULL_DOWN)
        # Define menu options and list:
        self.menu_list = ["Bitcoin", "Ethereum", "Binance Coin", "XRP", "Tether"]
        self.menu_options = [False, False, False, False, False]
        self.activated = False
        self.x = 0
    # Get information from the PHP web application via the ESP8266 ESP-01:
    def fetch_information_from_esp(self):
        incoming = bytes()
        while self.uart0.any() > 0:
            incoming += self.uart0.readline()
        # Check the incoming data before decoding:    
        if (len(incoming) and incoming.decode("utf-8")):
            incoming = incoming.decode("utf-8")
            if (incoming.find("[HTTP]") < 0 and incoming.endswith("}}\r\n")):
                self.coin_data = json.loads(incoming) 
    # Interface (menu options):
    def interface(self):
        self.display.text(bold, self.menu_list[0], 30, 20, color=st7789.color565(243,208,296), background=st7789.color565(32,32,32))
        self.display.text(bold, self.menu_list[1], 30, 60, color=st7789.color565(243,208,296), background=st7789.color565(32,32,32))
        self.display.text(bold, self.menu_list[2], 30, 100, color=st7789.color565(243,208,296), background=st7789.color565(32,32,32))
        self.display.text(bold, self.menu_list[3], 30, 140, color=st7789.color565(243,208,296), background=st7789.color565(32,32,32))
        self.display.text(bold, self.menu_list[4], 30, 180, color=st7789.color565(243,208,296), background=st7789.color565(32,32,32))
    # Change the RGB LED's color. 
    def adjust_color(self, red_x, green_x, blue_x):
        self.red.duty_u16(red_x)
        self.green.duty_u16(green_x)
        self.blue.duty_u16(blue_x)
    # Read controls:
    def read_controls(self):
        self.JX = self.joystick_x.read_u16()
        self.JY = self.joystick_y.read_u16()
        self.JSW = self.joystick_sw.value()
        self.EX = self.exit_button.value()
    # Change menu options:
    def change_menu_options(self):
        if (self.JY > 35000):
            self.x-=1
        if(self.JY < 9000):
            self.x+=1
        if(self.x > 5):
            self.x = 1
        if(self.x < 0):
            self.x = 5
        # Activate menu options:
        if(self.x == 1):
            self.menu_options = [True, False, False, False, False]
        if(self.x == 2):
            self.menu_options = [False, True, False, False, False]
        if(self.x == 3):
            self.menu_options = [False, False, True, False, False]
        if(self.x == 4):
            self.menu_options = [False, False, False, True, False]
        if(self.x == 5):
            self.menu_options = [False, False, False, False, True]
            
    # Define menu option features and functions:
    def activate_menu_option(self, i, r, g, b, row, coin_name, s_bac, i_col=st7789.color565(243,208,296), i_bac=st7789.color565(165,40,44), o_col=st7789.color565(31,32,32)):
        if(self.menu_options[i] == True):
            self.display.text(bold, self.menu_list[i], 30, row, color=i_col, background=i_bac)
            self.adjust_color(r, g, b)
            if (self.JSW == False):
                self.display.fill(s_bac)
                self.activated = True
            while self.activated:
                self.read_controls()
                # Get information from the PHP web application:
                self.fetch_information_from_esp()
                # Print information from the web application:
                if not (self.coin_data == 0):
                    self.display.text(bold, self.coin_data[coin_name]["name"], 30, 20, color=o_col, background=s_bac)
                    self.display.text(normal, str(self.coin_data[coin_name]["price"]), 30, 100, color=o_col, background=s_bac)
                    self.display.text(normal, str(self.coin_data[coin_name]["total_volume"]), 30, 135, color=o_col, background=s_bac)
                    self.display.text(normal, str(self.coin_data[coin_name]["price_change_24h"]), 30, 170, color=o_col, background=s_bac)
                    self.display.text(normal, str(self.coin_data[coin_name]["percent_change_usd_24"]), 30, 205, color=o_col, background=s_bac)
                    # Activate the buzzer:
                    if(self.coin_data[coin_name]["price_change_24h"] < 0):
                        self.buzzer.duty_u16(1000)
                else:
                    self.display.text(bold, "Refresh", 30, 20, color=o_col, background=s_bac)
                    self.display.text(normal, "Refresh", 30, 90, color=o_col, background=s_bac)
                    self.display.text(normal, "Refresh", 30, 125, color=o_col, background=s_bac)
                    self.display.text(normal, "Refresh", 30, 160, color=o_col, background=s_bac)
                    self.display.text(normal, "Refresh", 30, 205, color=o_col, background=s_bac)
                # Deactivate the buzzer:
                if(self.JX > 40000):
                    self.buzzer.duty_u16(0)
                # Exit:
                if self.EX:
                    self.activated = False
                    self.display.fill(st7789.color565(32,32,32))
                    self.buzzer.duty_u16(0)

# Define the new 'coin' class object.
coin = cryptocurrency_tracker()
coin.display.fill(st7789.color565(32,32,32))
coin.adjust_color(65025, 65025, 65025)

while True:
    # Initiate:
    coin.read_controls()
    coin.interface()
    coin.change_menu_options()
    # Menu Options:
    coin.activate_menu_option(0, r=0, g=65025, b=0, row=20, coin_name="bitcoin", s_bac=st7789.color565(209,205,218))
    coin.activate_menu_option(1, r=0, g=0, b=65025, row=60, coin_name="ethereum", s_bac=st7789.color565(243,208,296))
    coin.activate_menu_option(2, r=65025, g=0, b=0, row=100, coin_name="binancecoin", s_bac=st7789.color565(174,225,205))
    coin.activate_menu_option(3, r=65025, g=0, b=65025, row=140, coin_name="ripple", s_bac=st7789.color565(26, 219, 97))
    coin.activate_menu_option(4, r=65025, g=65025, b=0, row=180, coin_name="tether", s_bac=st7789.color565(94,176,229))
