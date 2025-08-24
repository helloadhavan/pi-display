import threading
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageFont, ImageDraw
from flask import Flask
from .utils import ip_address, cpu_usage, memory_usage, disk_usage, temp
from pidisplay import ads1115
from pidisplay import ina219
import os

class DisplayServer(object):
    
    def __init__(self, *args, **kwargs):
        adress = os.popen("i2cdetect -y -r 1 0x48 0x48 | egrep '48' | awk '{print $2}'").read()
        if(adress=='48\n'):
            self.ads = ads1115.ADS1115()
        else:
            self.ads = None
            
        adress = os.popen("i2cdetect -y -r 1 0x41 0x41 | egrep '41' | awk '{print $2}'").read()
        if(adress=='41\n'):
            self.ina219 = ina219.INA219(addr=0x41)
        else:
            self.ina219 = None

        adress = os.popen("i2cdetect -y -r 1 0x42 0x42 | egrep '42' | awk '{print $2}'").read()
        if(adress=='42\n'):
            self.ina = ina219.INA219(addr=0x42)
        else:
            self.ina = None
            
        # Initialize I2C and display
        i2c = busio.I2C(board.SCL, board.SDA)
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        self.display.fill(0)
        self.display.show()
        self.font = ImageFont.load_default()
        self.image = Image.new('1', (self.display.width, self.display.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=0)
        self.stats_enabled = False
        self.stats_thread = None
        self.stats_interval = 1.0
        self.enable_stats()
        
    def _run_display_stats(self):
        Charge = False
        while self.stats_enabled:
            
            self.draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=0)

            # set IP address
            top = -2
            if ip_address('eth0') is not None:
                self.draw.text((4, top), 'IP: ' + str(ip_address('eth0')), font=self.font, fill=255)
            elif ip_address('wlan0') is not None:
                self.draw.text((4, top), 'IP: ' + str(ip_address('wlan0')), font=self.font, fill=255)
            else:
                self.draw.text((4, top), 'IP: not available')

            top = 6
            
            if(self.ina != None):
                bus_voltage = self.ina.getBusVoltage_V()        # voltage on V- (load side)
                current = self.ina.getCurrent_mA()                # current in mA
                p = (bus_voltage - 6)/2.4*100
                if(p > 100):p = 100
                if(p < 0):p = 0
                if(current < 0):current = 0
                if(current > 30):
                    Charge = not Charge
                else:
                    Charge = False

                if(Charge == False):
                    self.draw.text((600, -2), ' ', font=self.font, fill=255)
                else:
                    self.draw.text((120, -2), '*', font=self.font, fill=255)
                self.draw.text((4, top),  (" %.1fV")%bus_voltage + (" %.2fA")%(current/1000) + (" %2.0f%%")%p, font=self.font, fill=255)
            elif(self.ina219 != None):
                bus_voltage = self.ina219.getBusVoltage_V()        # voltage on V- (load side)
                current = self.ina219.getCurrent_mA()                # current in mA
                p = (bus_voltage - 9)/3.6*100
                if(p > 100):p = 100
                if(p < 0):p = 0
                if(current < 0):current = 0
                if(current > 30):
                    Charge = not Charge
                else:
                    Charge = False

                if(Charge == False):
                    self.draw.text((600, -2), ' ', font=self.font, fill=255)
                else:
                    self.draw.text((120, -2), '*', font=self.font, fill=255)
                self.draw.text((4, top),  (" %.1fV")%bus_voltage + (" %.2fA")%(current/1000) + (" %2.0f%%")%p, font=self.font, fill=255)
            elif(self.ads != None):
                value=self.ads.readVoltage(4)/1000.0
                p = value/12.6*100
                if(p > 100):p = 100
                self.draw.text((4, top), 'PWR: '  + ("  %.1fV")%value + ("  %2.0f%%")%p, font=self.font, fill=255)
            else:
                self.draw.text((4, top), 'PWR No Detection' , font=self.font, fill=255)
                
            
            # set stats headers
            top = 14
            offset = 4 * 8
            headers = ['CPU', 'RAM', 'DSK', 'TMP']
            for i, header in enumerate(headers):
                self.draw.text((i * offset + 4, top), header, font=self.font, fill=255)

            # set stats fields
            top = 22
                                                            
            cpu_percent = '%2d%%' % int(round(cpu_usage() * 100.0, 1))
            ram_percent = '%2d%%' % int(round(memory_usage() * 100.0, 1))
            disk_percent = '%2d%%' % int(round(disk_usage() * 100.0, 1))
            temp_percent = '%2d' % int(round(temp(), 1))
            
            entries = [cpu_percent, ram_percent, disk_percent, temp_percent]
            for i, entry in enumerate(entries):
                self.draw.text((i * offset + 4, top), entry, font=self.font, fill=255)

            self.display.image(self.image)
            self.display.show()

            time.sleep(self.stats_interval)
            
    def enable_stats(self):
        # start stats display thread
        if not self.stats_enabled:
            self.stats_enabled = True
            self.stats_thread = threading.Thread(target=self._run_display_stats)
            self.stats_thread.start()
        
    def disable_stats(self):
        self.stats_enabled = False
        if self.stats_thread is not None:
            self.stats_thread.join()
        self.draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=0)
        self.display.image(self.image)
        self.display.show()

    def set_text(self, text):
        self.disable_stats()
        self.draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=0)
        
        lines = text.split('\n')
        top = 2
        for line in lines:
            self.draw.text((4, top), line, font=self.font, fill=255)
            top += 10
        
        self.display.image(self.image)
        self.display.show()
        

server = DisplayServer()
app = Flask(__name__)


@app.route('/stats/on')
def enable_stats():
    global server
    server.enable_stats()
    return "stats enabled"

    
@app.route('/stats/off')
def disable_stats():
    global server
    server.disable_stats()
    return "stats disabled"


@app.route('/text/<text>')
def set_text(text):
    global server
    server.set_text(text)
    return 'set text: \n\n%s' % text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=False)

