# デジタル水温計
# 商品名：DS18B20

import subprocess

class DS18B20:

	__sensorInfoFile = ''

	def __init__(self, sensorInfoFile):
		self.__sensorInfoFile = sensorInfoFile

	def read(self):
        sensorData = self.__get_sensor_raw()

        if sensorData is None:
            return 0
    
        temp_val = sensorData.split('=')
        return round(float(temp_val[-1]) / 1000, 1)
    
    def __get_sensor_raw():
        try:
            return subprocess.check_output(['cat', SENSOR_INFO_FILE]).decode()
        except:
            return None
