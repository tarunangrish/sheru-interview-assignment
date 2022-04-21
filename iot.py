from crypt import methods
import os
from time import time
from flask import Flask, render_template, session
import pytz
import socketio
import requests
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
import pymongo

from app import saveData

app = Flask(__name__)
sio = socketio.Client()

def getData():
    """Example of how to send server generated events to clients."""
    url = 'http://3.109.76.78:2222/xenergyData.json'
    records = ((requests.get(url)).json())['records']
    return records

def filterData(data):
    url = 'http://127.0.0.1:5000/timestamp/'
    print(requests.get(url).json())
    lastTime = ((requests.get(url)).json())['created']
    print(lastTime)

    if lastTime:
        timezone = pytz.timezone('Asia/Kolkata')
        lastTime = datetime.strptime(lastTime, '%Y-%m-%d %H:%M:%S')
        lastTime = timezone.localize(lastTime)
        lst = []
        for item in data:
            print("In for loop")
            timezone = pytz.timezone('Asia/Kolkata')
            newTime = datetime.strptime(item['created'], '%Y-%m-%d %H:%M:%S')
            newTime = newTime.astimezone(timezone)
            print(str(lastTime) + "-----------" + str(newTime))
            print(newTime > lastTime)
            if newTime > lastTime:
                print("in if else")
                lst.append(item)
        return lst
    else:
        print("Hi")
        return data


def sendData(data):
    print('Sending Data via Socket Connection...')
    sio.connect('http://127.0.0.1:5000')
    sio.emit('records', data)
    sio.disconnect()

def background():
    data = getData()
    records = filterData(data)
    if records:
        sendData(records)
        

scheduler = BackgroundScheduler()

@app.route('/')
def control():
    return render_template('control.html')


@app.route('/start/', methods=['POST', 'GET'])
def start():
    scheduler.add_job(func=background, trigger="interval", seconds=15)
    scheduler.start()
    return "Succesfully started"


@app.route('/stop/', methods=['POST', 'GET'])
def stop():
    scheduler.remove_job(func = background)
    return "Succesfully stopped"


@sio.on('PVAlerts')
def handle_message(data):
    print(data)

@sio.on('CBAlerts')
def handle_message(data):
    print(data)
@sio.on('BBAlerts')
def handle_message(data):
    print(data)
@sio.on('ResetClassesForVoltage')
def handle_message(data):
    print(data)
@sio.on('ResetClassesForCurrent')
def handle_message(data):
    print(data)
@sio.on('ResetClassesForBattery')
def handle_message(data):
    print(data)

app.debug = True
host = os.environ.get('IP', '127.0.0.1')
port = int(os.environ.get('PORT', 8091))
app.run(host=host, port=port, use_reloader = True)


