import Modules.utils as util
config = util.get_config()
on_pi = config['ON_PI']


if on_pi:
    import RPi.GPIO as GPIO
    import smbus2 as smbus
import time


class MotorController:
    def __init__(self):
        if on_pi:
            self.I2C_PIN = config['MOTOR_DRIVER']['POWER_PIN']
            self.BUS = smbus.SMBus(config['MOTOR_DRIVER']['I2C_ID'])
            self.DEVICE_ADDRESS = config['MOTOR_DRIVER']['ADDRESS']
            self.LEFT_MOTOR = config['MOTOR_DRIVER']['MOTORS']['LEFT']
            self.RIGHT_MOTOR = config['MOTOR_DRIVER']['MOTORS']['RIGHT']
        if on_pi:
            GPIO.setmode(GPIO.BCM)
            time.sleep(0.1)
            GPIO.setup(self.I2C_PIN, GPIO.OUT)
            time.sleep(0.1)


    def on(self):
        if on_pi:
            GPIO.output(self.I2C_PIN, GPIO.HIGH)


    def off(self):
        if on_pi:
            self.set_to(0, 0)
            GPIO.output(self.I2C_PIN, GPIO.LOW)


    def set_to(self, left, right, verbose=False):
        if on_pi:
            try:
                self.BUS.write_i2c_block_data(self.DEVICE_ADDRESS,self.LEFT_MOTOR,util.int_to_byte_array(-1*left))
                self.BUS.write_i2c_block_data(self.DEVICE_ADDRESS,self.RIGHT_MOTOR,util.int_to_byte_array(-1*right))
            except:
                self.on()
        if verbose:
            print("Left:", left)
            print("Right:", right)
    

    def stop(self):
        self.set_to(0, 0)


    def forward(self, speed):
        self.set_to(left=speed, right=speed)
    

    def backward(self, speed):
        self.set_to(left=speed, right=speed)


    def left_pivot(self, speed):
        self.set_to(left=-1*speed, right=speed)


    def right_pivot(self, speed):
        self.set_to(left=speed, right=-1*speed)


    def set_bias(self, bias, regular):
        self.set_to(left=regular+bias, right=regular-bias)