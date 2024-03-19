import network
import time
import rp2
import ubinascii
from machine import Pin

def blink_onboard_led(num_blinks):
    led = Pin("LED", Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

class WLAN_Connect(object):
    
    
    def __init__(self, ssid, password, country_code):
        self.ssid = ssid
        self.password = password
        self.country_code = country_code
        
    
    def connect(self, timeout=5):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        try:
            wlan.connect(self.ssid, self.password)
        except OSError as e:
            print(f"error encountered {e}")
        rp2.country(self.country_code)
        
#         if Power is True:
#             wlan.config(pm = 0xa11140)
        
        while timeout > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
        timeout -= 1
        print("waiting for connection....")
        time.sleep(1)
        
        #handle connection errors
        if wlan.status() != 3:
            raise RuntimeError('Network Connection failed!!')
        else:
            print('CONNECTED TO {}'.format(self.ssid))
            blink_onboard_led(3)
            status = wlan.ifconfig()
            print('ip = ' + status[0])
        
        
    def get_mac(self):
        mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
        print("MAC ADDRESS : {}".format(mac))
        
# USING AS A SCRIPT
# if __name__ == "__main__":
#     Wifi = WLAN_Connect('RAY VILLA', '65301115', 'IN')
#     Wifi.connect(timeout = 10, Power = False)
#     Wifi.get_mac()
        
        
        
    
    