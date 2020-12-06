import requests
import json
import threading
import schedule
from picamera import PiCamera
from time import sleep

rasp_id = ""
rasp_pw = ""
rasp_group = ""

access_token = ""
api_server_url = ""
image_server_url = ""

devices_json_path = ""

def get_conf():
    with open('./conf.json') as conf_json:
        conf = json.load(conf_json)
        return conf

def get_devices():
    devices_data = []
    with open(devices_json_path) as devices_json:
        devices_data = json.load(devices_json)
    return devices_data

def raspberry_connect():
    global rasp_id, rasp_pw, rasp_group, access_token, api_server_url

    headers = {'Content-Type':'application/json'}
    data = {
        'raspberry_group': rasp_group,
        'raspberry_id': rasp_id,
        'raspberry_pw': rasp_pw
    }
    res = requests.post(api_server_url + '/api/raspberry/connect', headers=headers, data=json.dumps(data))
    
    try:
        res_data = res.json()
        return res_data['access_token']
    except:
        return None

def raspberry_capture():
    camera = PiCamera()
    sleep(3)
    camera.capture('./temp.jpg')

def is_there_person():
    raspberry_capture();
    image_file = open('./temp.jpg', 'rb')
    upload = {'file':image_file}
    res = requests.post(image_server_url, files = upload)
    try:
        res_data = res.json()
        return res_data['is_there_anyone']
    except:
        return False

def device_off(device_id, device_type, unit_index):
    global api_server_url, access_token

    headers = {'Content-Type': 'application/json', 'Authentication': "Bearer " + access_token}
    data = {
        'device_id': device_id,
        'device_type': device_type,
        'on_off': False,
        'unit_index': unit_index
    }
    res = requests.post(api_server_url + '/api/device/control', headers=headers, data=json.dumps(data))
    
    if str(res.status_code)[0] == '4':
        return False

    return True

def device_all_off():
    devices = get_devices()
    for i in range(len(devices)):
        for j in range(devices[i]['unit_count']):
            chk = device_off(devices[i]['id'], devices[i]['type'], j)
            if not chk:
                return False
    return True

def schedule_run():
    if is_there_person():
        device_all_off()


def main():
    global rasp_id, rasp_pw, rasp_group, api_server_url, image_server_url, devices_json_path
    conf = get_conf()

    rasp_id = conf['rasp_id']
    rasp_pw = conf['rasp_pw']
    rasp_group = conf['rasp_group']
    api_server_url = conf['api_server_url']
    image_server_url = conf['image_server_url']
    devices_json_path = conf['devices_json_path']
    schedule_time = conf['schedule_time']

    schedule.every(schdule_time).minutes.do(schedule_run)

if __name__ == '__main__':
    main()
