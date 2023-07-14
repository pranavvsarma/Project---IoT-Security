import serial
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import uuid
import datetime
import requests, sys

clientId = "Omega_AC51"
endpoint = "a1km12bi5nlxfi-ats.iot.us-east-1.amazonaws.com"
rootCAFilePath = "/IOT/lab8/certs/Amazon-root-CA-1.pem"
privateKeyFilePath = "/IOT/lab8/certs/private.pem.key"
certFilePath = "/IOT/lab8/certs/device.pem.crt"

myMQTTClient = AWSIoTMQTTClient(clientId)

myMQTTClient.configureEndpoint(endpoint, 8883)

# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH", "PRIVATE/KEY/PATH", "CERTIFICATE/PATH")
myMQTTClient.configureCredentials(rootCAFilePath, privateKeyFilePath, certFilePath)
# For Websocket, we only need to configure the root CA
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

topic = "OmegaAC51/data/project"

QoS = 1


def customCallback(client, userdata, message):
    print(str(message.topic) + ": " + str(message.payload))


def customOnMessage(client, userdata, message):
    print(str(message.topic) + ": " + str(message.payload))


print("Connecting to: " + endpoint + " with ClientID " + clientId)

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)


def mac_address():
    mac = hex(uuid.getnode())
    return mac


def current_date_time():
    timestamp = datetime.datetime.now()
    return timestamp


# @brief: Send a read/write command to the Arduino
# @par ser: The serial port instance
# @par command: The name of the read/write command
# @ret None
def send_command(ser, command):
    ser.write(command.encode())


# @brief: Read the Serial port for a newline and return the output (data / string/ newline)
# @par ser: The serial port instance
# @ret value: Received serial transmission (newline)
def read_uart(ser):
    value = ser.readline().decode('utf-8')  # Read and print the received serial transmission
    # print(value)
    return value


# @brief: Check and wait for the Acknowledgeent from the Arduino
# @par ser: The serial port instance
# @par ack_string: The name of the acknowledgement message
# @ret: None
def check_ack(ser, ack_string):
    while (1):
        recd_ack = ser.readline().decode('utf-8')  # Read and print the received serial transmission
        print(recd_ack)

        if (recd_ack == ack_string + "\r\n"):  # Check if the recieved message is an acknowledgement message
            print("ACK received")
            break


# @brief: Configure the Serial port of the Omega board
# @par None
# @ret ser: Instantiation of Serial Port
def serial_port():
    ser = serial.Serial(
        port='/dev/ttyS1', \
        baudrate=9600, \
        parity=serial.PARITY_NONE, \
        stopbits=serial.STOPBITS_ONE, \
        bytesize=serial.EIGHTBITS, \
        timeout=None)

    return ser


def temp_light():
    ser = serial_port()
    while (1):

        time.sleep(1)
        send_command(ser, "TEMP")  # Send command to read the temperature sensor
        temperature = float(read_uart(ser))  # Read the temperature value from UART

        send_command(ser, "LIGHT")
        light = int(read_uart(ser))
        break

    return temperature, light

def weather_data():
    r = requests.get('https://api.weather.gov/points/43.0845,-77.6749')
    # r = requests.get('https://api.weather.gov/openapi.json.')
    data = r.json()
    # pprint(data)

    data1 = data['properties']['forecast']
    cwa_value = data['properties']['cwa']
    # print("Forecast Office: ", cwa_value)
    observation_stations = data['properties']['forecastOffice']
    # print("Approved observation station :",observation_stations)
    # pprint(data1)
    closest_station = requests.get(observation_stations)
    approved_observation_station = closest_station.json()['approvedObservationStations'][10]
    # print("Observation station :", approved_observation_station)
    latest_observations = requests.get('https://api.weather.gov/stations/KROC/observations/latest')
    forecast = latest_observations.json()
    time_stamp = forecast['properties']['timestamp']

    return cwa_value, approved_observation_station, forecast, time_stamp

# @brief: Consume weather API to get weather parameters
# @par None
# @ret temperature, wind & relative humidity
def temp_and_wind():

    cwa, approved_station, forecast, time_stamp = weather_data()
    t_in_C = forecast['properties']['temperature']['value']  # get temperature in C
    temperature = (t_in_C * 1.8) + 32  # convert temperature from C to F
    w_in_kph = forecast['properties']['windSpeed']['value']  # get windspeed in kph
    if w_in_kph is None:
        w_in_kph = 0
    windspeed = (w_in_kph / 1.609)  # convert windspeed in mph from kph

    rh = forecast['properties']['relativeHumidity']['value']  # get relative humidity in percent
    if rh is None:
        rh = 0
    time_stamp = forecast['properties']['timestamp']
    return temperature, windspeed, rh

# @brief: Calcuate wind chill
# @par None
# @ret ser: wind chill
def wind_chill():
    temperature, windspeed, rh = temp_and_wind()
    # temperature = (t * 1.8) + 32
    # windspeed = (w / 1.609)

    windchill = 35.74 + (0.6215 * temperature) - (35.75 * (windspeed ** 0.16)) + \
                (0.4275 * temperature * (windspeed ** 0.16))
    return windchill

# @brief: Calcuate Heat Index
# @par None
# @ret ser: heat index
def heat_index():
    temperature, windspeed, rh = temp_and_wind()
    if rh < 13 and (temperature >= 80 or temperature <= 112):
        hi = heat_index_regression()
        adjustment = ((13 - rh) / 4) * ((17 - abs(temperature - 95) / 17) ** (1 / 2))
        heatindex = hi - adjustment


    elif rh > 85 and (temperature >= 80 or temperature <= 87):
        hi = heat_index_regression()
        adjustment = ((rh - 85) / 10) * ((87 - temperature) / 5)
        heatindex = hi + adjustment
        return heatindex

# @brief: Calcuate regression of heat index
# @par None
# @ret ser: heat index regression
def heat_index_regression():
    # temp_and_wind()
    temperature, windspeed, rh = temp_and_wind()

    heatindex = -42.379 + (2.04901523 * temperature) + (10.14333127 * rh) - (0.22475541 * temperature * rh) - \
                (0.00683783 * temperature * temperature) - (0.5481717 * rh * rh) + \
                (0.00122874 * temperature * temperature * rh) + (0.00085282 * temperature * rh * rh) \
                - (0.00000199 * temperature * temperature * rh * rh)
    return heatindex

def main():
    # while(1):

    ser = serial_port()

    topic = "OmegaAC51/data/project"
    QoS = 1

    temperature, light = temp_light()
    mac = mac_address()
    cwa_value, approved_station, forecast, time_stamp = weather_data()

    # observation_stn = approved_station.split("/")[-1]
    # print("Name: SHYAM BHANUSHALI")
    # print("Co-ordinates: 43.0845°,-77.6749°")
    # print("Forecast Office: ", cwa)
    # print("Observation Station: ", observation_stn)
    # print("Timestamp: ", time_stamp)
    temperature, windspeed, rh = temp_and_wind()


    # temperature = (temp_C * 1.8) + 32  # convert temperature from C to F

    temp_C = (temperature - 32) * (5 / 9)
    windspeed_kph = (windspeed * 1.609)

    temp = "Temperature: {:.2f} °C | {:.2f} °F".format(temp_C, temperature)
    wind = "Windspeed: {:.2f} mph | {:.2f} km/h".format(windspeed, windspeed_kph)
    # print("RH: {:.2f}%".format(rh))
    print(temp)
    print("RH: {:.2f}%".format(rh))
    print(wind)

    if temperature <= 50.0 or windspeed > 3.0:
        windchill_f = wind_chill()
        # print(windchill_f)
        windchill = (windchill_f - 32) * (5 / 9)
        heatindex = "None"
        # print("WINDCHILL: ", windchill)

    else:
        hi = heat_index()
        if hi is None:
            hi = 0
        heatindex = (hi - 32) * (5 / 9)
        print("HEATINDEX :", heatindex)
        windchill = "None"


    payload = json.dumps({"WeatherData": [
                              {
                                  "Temperature": temp_C,
                                  "Windspeed": windspeed_kph,
                                  "Relative Humidity": rh,
                                  "Wind Chill": windchill,
                                  "Heat Index": heatindex,

                                  "Timestamp": time_stamp
                              }
                          ],
                          "SensorData": [
                              {
                                  "Temperature sensor value": temperature,
                                  "Light sensor value": light
                              }
                          ]
                           })
    myMQTTClient.publish(topic, payload, QoS)
    myMQTTClient.unsubscribe(topic)
    myMQTTClient.disconnect()
        # time.sleep(5)



if __name__ == "__main__":
    main()
