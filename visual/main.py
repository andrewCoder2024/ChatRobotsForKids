
import time
from rpi_ws281x import Adafruit_NeoPixel, Color
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from PCA9685 import PCA9685

# LED strip configuration:
LED_COUNT      = 4      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()
strip.show()

rgb = 0
f = lambda x: (-1/10000.0)*x*x + (1/50.0)*x
x = 0

Ab = AlphaBot2()

DR = 16
DL = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)

pwm = PCA9685(0x40)
pwm.setPWMFreq(50)

def main():

    tone = raw_input("Enter joy, sadness, anger, or neutral: ").lower()

    if tone == "joy":
        rgb = (0<<16) | (255<<8) | 0
        try:
            pulse = 1500
            offset = 25
            pwm.setServoPulse(0, 1500)
            while True:
                breathing_lights(rgb, 5)
                if pulse > 2000:
                    offset = -25
                elif pulse < 1500:
                    offset = 25
                pwm.setServoPulse(1,pulse)
                time.sleep(0.02)
                pulse = pulse + offset
        except KeyboardInterrupt:
            pwm.setServoPulse(0,0)
            pwm.setServoPulse(1,0)
        
    elif tone == "sadness":
        rgb = (0<<16) | (0<<8) | 128
        try:
            pulse = 1300
            offset = 10
            pwm.setServoPulse(1,2250)
            time.sleep(0.05)
            while True:
                breathing_lights(rgb, 1)
                if pulse > 1700:
                    offset = -10
                elif pulse < 1300:
                    offset = 10
                pwm.setServoPulse(0,pulse)
                time.sleep(0.02)
                pulse = pulse + offset
        except KeyboardInterrupt:
            pwm.setServoPulse(0,0)
            pwm.setServoPulse(1,0)
            
    elif tone == "anger":
        rgb = (255<<16) | (0<<8) | 0
        try:
            while True:
                breathing_lights(rgb, 3)
                DR_status = GPIO.input(DR)
                DL_status = GPIO.input(DL)
        #		print(DR_status,DL_status)
                if((DL_status == 0) or (DR_status == 0)):
                    Ab.backward()
                else:
                    Ab.stop()
        except KeyboardInterrupt:
            GPIO.cleanup()
        
    elif tone ==  "neutral":
        pass
    
    else:
        print("What is this emotion?")
        
def breathing_lights(rgb, speed):
    global x
    red = int(((rgb & 0x00ff00) >> 8) * f(x))
    green = int(((rgb & 0xff0000) >> 16) * f(x))
    blue = int((rgb & 0x0000ff) * f(x))
    _rgb = int((red << 8) | (green << 16) | blue)
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, _rgb)
        strip.show()
    time.sleep(0.02)
    x += speed
    if x >= 200:
        x = 0
                    
if __name__=="__main__":
    main()
