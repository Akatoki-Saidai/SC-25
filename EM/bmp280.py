#coding: utf-8
# sudo apt-get update
# sudo apt install -y python-smbus
# sudo pip install smbus2

from smbus2 import SMBus
import time
import sc_logging

logger = sc_logging.get_logger(__name__)

class BMP280:
    def writeReg(self, reg_address, data):
        try:
            self.bus.write_byte_data(self.i2c_address,reg_address,data)
        except Exception as e:
            logger.exception("An error occured!")

    def get_calib_param(self):
        try:
            calib = []
        
            for i in range (0x88,0x88+24):
                calib.append(self.bus.read_byte_data(self.i2c_address,i))
            calib.append(self.bus.read_byte_data(self.i2c_address,0xA1))
            for i in range (0xE1,0xE1+7):
                calib.append(self.bus.read_byte_data(self.i2c_address,i))

            self.digT[0] = ((calib[1] << 8) | calib[0])
            self.digT[1] = ((calib[3] << 8) | calib[2])
            self.digT[2] = ((calib[5] << 8) | calib[4])
            self.digP[0] = ((calib[7] << 8) | calib[6])
            self.digP[1] = ((calib[9] << 8) | calib[8])
            self.digP[2] = ((calib[11]<< 8) | calib[10])
            self.digP[3] = ((calib[13]<< 8) | calib[12])
            self.digP[4] = ((calib[15]<< 8) | calib[14])
            self.digP[5] = ((calib[17]<< 8) | calib[16])
            self.digP[6] = ((calib[19]<< 8) | calib[18])
            self.digP[7] = ((calib[21]<< 8) | calib[20])
            self.digP[8] = ((calib[23]<< 8) | calib[22])
            self.digH[0] = ( calib[24] )
            self.digH[1] = ((calib[26]<< 8) | calib[25])
            self.digH[2] = ( calib[27] )
            self.digH[3] = ((calib[28]<< 4) | (0x0F & calib[29]))
            self.digH[4] = ((calib[30]<< 4) | ((calib[29] >> 4) & 0x0F))
            self.digH[5] = ( calib[31] )
            
            for i in range(1,2):
                if self.digT[i] & 0x8000:
                    self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1

            for i in range(1,8):
                if self.digP[i] & 0x8000:
                    self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1

            for i in range(0,6):
                if self.digH[i] & 0x8000:
                    self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1  
        except Exception as e:
            logger.exception("An error occured!")

    def readData(self):
        try:
            data = []
            for i in range (0xF7, 0xF7+8):
                data.append(self.bus.read_byte_data(self.i2c_address,i))
            pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
            temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
            # hum_raw  = (data[6] << 8)  |  data[7]
            
            
            temperature = self.compensate_T(temp_raw)
            pressure = self.compensate_P(pres_raw)
            
            logger.info("pressure : {:7.2f} hPa".format(pressure/100))
            logger.info("temp : {:6.2f} ℃".format(temperature))

            return temperature, pressure
        except Exception as e:
            logger.exception("An error occured!")

    def compensate_P(self, adc_P):
        try:
            pressure = 0.0
            
            v1 = (self.t_fine / 2.0) - 64000.0
            v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.digP[5]
            v2 = v2 + ((v1 * self.digP[4]) * 2.0)
            v2 = (v2 / 4.0) + (self.digP[3] * 65536.0)
            v1 = (((self.digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8)  + ((self.digP[1] * v1) / 2.0)) / 262144
            v1 = ((32768 + v1) * self.digP[0]) / 32768
            
            if v1 == 0:
                return 0
            pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
            if pressure < 0x80000000:
                pressure = (pressure * 2.0) / v1
            else:
                pressure = (pressure / v1) * 2
            v1 = (self.digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
            v2 = ((pressure / 4.0) * self.digP[7]) / 8192.0
            pressure = pressure + ((v1 + v2 + self.digP[6]) / 16.0)  

            # logger.info("pressure : {:7.2f} hPa".format(pressure/100))
            return pressure
        except Exception as e:
            logger.exception("An error occured!")

    def compensate_T(self, adc_T):
        try:
            v1 = (adc_T / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
            v2 = (adc_T / 131072.0 - self.digT[0] / 8192.0) * (adc_T / 131072.0 - self.digT[0] / 8192.0) * self.digT[2]
            self.t_fine = v1 + v2
            temperature = self.t_fine / 5120.0

            # logger.info("temp : {:6.2f} ℃".format(temperature/100))
            return temperature
        except Exception as e:
            logger.exception("An error occured!")

    def setup(self):
        try:
            osrs_t = 1            #Temperature oversampling x 1
            osrs_p = 1            #Pressure oversampling x 1
            # osrs_h = 1            #Humidity oversampling x 1
            mode   = 3            #Normal mode
            t_sb   = 5            #Tstandby 1000ms
            filter = 0            #Filter off
            spi3w_en = 0            #3-wire SPI Disable

            ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
            config_reg    = (t_sb << 5) | (filter << 2) | spi3w_en
            # ctrl_hum_reg  = osrs_h

            # writeReg(0xF2,ctrl_hum_reg)
            self.writeReg(0xF4,ctrl_meas_reg)
            self.writeReg(0xF5,config_reg)

            # 一応10回空測定
            for i in range(10):
                self.readData()
        except Exception as e:
            logger.exception("An error occured!")
    
    def get_baseline(self):
        try:
            baseline_values = []
            baseline_size = 100

            for i in range(baseline_size):
                _, pressure = self.readData()
                baseline_values.append(pressure)
                time.sleep(0.1)
            baseline = sum(baseline_values[:-80]) / len(baseline_values[:-80])
        
            return baseline
        except Exception as e:
            logger.exception("An error occured!")
    
    def __init__(self):
        # モジュール読み込み時に自動実行

        self.bus_number  = 1  # I2C1
        self.i2c_address = 0x76  # BMP280のアドレス(注：メモリアドレスではない)
        self.bus = SMBus(self.bus_number)
        self.digT = [0, 0, 0]  # 温度の補正パラメータ
        self.digP = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 気圧の補正パラメータ
        self.digH = [0, 0, 0, 0, 0, 0]  # 湿度の補正パラメータ(BME280の名残で書いてあるだけで，BMP280では不使用)
        self.t_fine = 0.0

        self.setup()  # 測定方法や補正方法を設定
        self.get_calib_param()  # 補正パラメータの読み取りと保存
        self.qnh = self.get_baseline()  # 高度0m地点の気圧を保存

    def get_altitude(self, qnh=1013.25, manual_temperature=None):
        try:
            # qnh = pressure at sea level where the readings are being taken.
            # The temperature should be the outdoor temperature.
            # Use the manual_temperature variable if temperature adjustments are required.
            temperature, pressure = self.readData()
            if manual_temperature is not None:
                temperature = manual_temperature
            
            if self.qnh:
                qnh = self.qnh
            
            # 気圧と温度を使った算出
            # altitude = ((pow((qnh / pressure), (1.0 / 5.257)) - 1) * (temperature + 273.15)) / 0.0065
            
            # 気圧のみの算出
            altitude = (((1 - (pow((pressure / qnh), 0.190284))) * 145366.45) / 0.3048 ) / 10
            
            logger.debug(f"altitude: {altitude}")
            return altitude
        except Exception as e:
            logger.exception("An error occured!")
    
    # eventがfalseの間，高度を測定し続ける
    def get_altitude_until_event(self, event, data):
        while event.is_set() == False:
            try:
                data["alt"] = self.get_altitude()
                time.sleep(0.1)
            except Exception as e:
                logger.exception("An error occured!")


if __name__ == '__main__':
    bmp = BMP280()
    
    while True:
        try:
            temperature, pressure = bmp.readData()
        except Exception as e:
            print(f"Unexpected error occcured: {e}")





