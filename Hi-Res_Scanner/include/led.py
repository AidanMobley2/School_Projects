import RPi.GPIO as IO
import time

class LED:
    def init_led(self, led_amount):
        self.led_amount = led_amount
        if led_amount == 3:
            self.led_pins = [
                17,     # 655nm
                27,     # 530nm
                22      # 450nm
            ]
        if led_amount == 11:
            # These were numbered based on the physical pin number 
            # but the BCM numbering uses the GPIO numbers.
            # These need to be changed to GPIO numbers to work.
            self.led_pins = [
                3,      # 685nm
                5,      # 655nm
                7,      # 630nm
                8,      # 620nm
                10,     # 595nm
                11,     # 570nm
                12,     # 530nm
                13,     # 510nm
                15,     # 480nm
                16,     # 450nm
                18      # 405nm
            ]
    
        #IO.setwarnings(False)

        # use GPIO pin numbering
        IO.setmode(IO.BCM)
        for i in range(led_amount):
            IO.setup(self.led_pins[i], IO.OUT)
        
    
    def led_on(self, led_num):
        IO.output(self.led_pins[led_num], IO.HIGH)
    
    def led_off(self, led_num):
        IO.output(self.led_pins[led_num], IO.LOW)

    def close_led(self):
        IO.cleanup()