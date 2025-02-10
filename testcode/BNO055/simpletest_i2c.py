# Simple Adafruit BNO055 sensor reading example.  Will print the orientation
# and calibration data every second.
#
# Copyright (c) 2015 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# import logging
# import sys
import time

import BNO055

try:

    # Create and configure the BNO sensor connection.  Make sure only ONE of the
    # below 'bno = ...' lines is uncommented:
    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    bno = BNO055(rst=18)
    # BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
    # and RST connected to pin P9_12:
    #bno = BNO055.BNO055(rst='P9_12')


    # Enable verbose debug logging if -v is passed as a parameter.
    # if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    #     logging.basicConfig(level=logging.DEBUG)

    # Initialize the BNO055 and stop if something went wrong.
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

    # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
    # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')

    # Print BNO055 software revision and other diagnostic data.
    sw, bl, accel, mag, gyro = bno.get_revision()
    print('Software version:   {0}'.format(sw))
    print('Bootloader version: {0}'.format(bl))
    print('Accelerometer ID:   0x{0:02X}'.format(accel))
    print('Magnetometer ID:    0x{0:02X}'.format(mag))
    print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    print('Reading BNO055 data, press Ctrl-C to quit...')
    while True:

        # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
        _sys, gyro, accel, mag = bno.get_calibration_status()
        # Print everything out.
        print('Gyro_cal={0} Accel_cal={1} Mag_cal={2}'.format(gyro, accel, mag))

        # Other values you can optionally read:
        
        # 4元数方位
        # Orientation as a quaternion:
        #x,y,z,w = bno.read_quaterion()
        
        # センサーの温度(←?)
        # Sensor temperature in degrees Celsius:
        # temp_c = bno.read_temp()

        # オイラー角
        # Read the Euler angles for heading, roll, pitch (all in degrees).
        # heading, roll, pitch = bno.read_euler()

        # 地磁気
        # Magnetometer data (in micro-Teslas):
        mag_x,mag_y,mag_z = bno.read_magnetometer()
        
        # ジャイロ
        # Gyroscope data (in degrees per second):
        gyro_x,gyro_y,gyro_z = bno.read_gyroscope()

        # 加速度
        # Accelerometer data (in meters per second squared):
        # x,y,z = bno.read_accelerometer()
        # Linear acceleration data (i.e. acceleration from movement, not gravity--
        # returned in meters per second squared):
        liner_accel_x,liner_accel_y,liner_accel_z = bno.read_linear_acceleration()
        # Gravity acceleration data (i.e. acceleration just from gravity--returned
        # in meters per second squared):
        gravity_x,gravity_y,gravity_z = bno.read_gravity()

        print(f"magnetometer: \nmag_x:{mag_x:.4f}  mag_y:{mag_y:.4f}  mag_z:{mag_z:.4f}")
        print(f"gyroscope: \ngyro_x:{gyro_x:.4f}  gyro_y:{gyro_y:.4f}  mag_z:{gyro_z:.4f}")
        print(f"liner_accel: \nliner_accel_x:{liner_accel_x:.4f}  liner_accel_y:{liner_accel_y:.4f}  liner_accel_z:{liner_accel_z:.4f}")
        print(f"gravity: \ngravity_x:{gravity_x:.4f}  gravity_y:{gravity_y:.4f}  gravity_z:{gravity_z:.4f}")
        print()

        time.sleep(1)

except Exception as e:
    print(f"An error occured in BNO055: {e}")