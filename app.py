from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from datetime import datetime
import json
import pytz
import pymongo
from bson.json_util import dumps

app = Flask(__name__)
socketIO = SocketIO(app, async_mode=None)

iotDBClient = pymongo.MongoClient("mongodb://localhost:27017/")
iotDB = iotDBClient["iotdevicedb"]
iotDBCollection = iotDB["iotdata"]

alertsList = []
voltageAlerts = []
currentAlerts = []
batteryAlerts = []

x = iotDBCollection.delete_many({})
mydict = { "vid": "XNG1037",
"latitude": "31.751144",
"longitude": "88.252587",
"avgVolt": "4.7",
"packVolt": "39",
"current": "13",
"battery": "2",
"created": "2022-04-21 08:42:24"
}
x = iotDBCollection.insert_one(mydict)
y = 2

@app.route('/')
def index():
    return render_template('index.html', async_mode = None)

@app.route('/timestamp/')
def timestamp():
    t = iotDBCollection.find()
    cursor = (t.sort([('created', -1)]).limit(1))
    for doc in cursor:
        y = doc

    list_cursor = list(y)
    json_data = dumps(y)
    return json_data

@socketIO.on('records')
def saveData(data):

    for item in data:
        lst = item['tdata'].split(',')
        timestamp = str(datetime.strptime(item['created'], '%Y-%m-%d %H:%M:%S'))
        record = [{
        'vid': lst[0],
        'latitude': lst[1],
        'longitude': lst[2],
        'avgVolt': lst[17],
        'packVolt': lst[18],
        'current': lst[19],
        'battery': lst[20],
        'created': timestamp
        }]

        try:
            print(record) 
            iotDBCollection.insert_many(record)
        except Exception as e:
            print("Exception Caught :-")
            print(e)
            
        finally:
            pass
        if float(lst[18]) >= 100:
            print('Package voltage breach for the value {}'.format(lst[18]))
            voltageAlerts.append(item)
            emit('PVAlerts',{'data': str(item), 'type': 'Voltage Breach'},broadcast=True)
            print('')
            
        if float(lst[19]) < 0:
            print('Current breach for the value {}'.format(lst[19]))
            currentAlerts.append(item)
            emit('CBAlerts',{'data': str(item), 'type': 'Current Breach'},broadcast=True)
            print('')
            
        if int(lst[20]) <= 20:
            print('Battery  breach for the value {}'.format(lst[20]))
            batteryAlerts.append(item)
            emit('BBAlerts',{'data': str(item), 'type': 'Battery Breach'},broadcast=True)
            print('')

        if float(lst[18]) < 100:
            emit('ResetClassesForVoltage',{'data': str(item), 'type': 'No Breach'},broadcast=True)

        if float(lst[19]) > 0:
            emit('ResetClassesForCurrent',{'data': str(item), 'type': 'No Breach'},broadcast=True)
            
        if int(lst[20]) > 20:
            emit('ResetClassesForBattery',{'data': str(item), 'type': 'No Breach'},broadcast=True)


if __name__ == '__main__':
    socketIO.run(app, port=5000, debug=False, use_reloader = True)