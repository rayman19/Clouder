from cgitb import text
from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify, url_for, redirect
import atexit
import os
import json
import xml.etree.ElementTree as ET


tree = ET.parse('catalog.xml')
root = tree.getroot()

app = Flask(__name__, static_url_path='')

db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

port = int(os.getenv('PORT', 8000))

@app.route('/')
def index():
    tree = ET.parse('catalog.xml')
    root = tree.getroot()
    return render_template('index.html', data=root, len=len(root))

@app.route('/delete/<int:id>')
def delete(id):
    root.remove(root[id])
    with open('catalog.xml', 'wb') as f:
        tree.write(f)
        return redirect(url_for('index'))

@app.route('/insert', methods=["POST"])
def insert():
    name = request.form.get('name')
    cpu = request.form.get('cpu')
    ram = request.form.get('ram')
    hdd = request.form.get('hdd')
    price = request.form.get('price')

    server = ET.Element("server")

    name_elem = ET.SubElement(server, 'name')
    name_elem.text = name

    cpu_elem = ET.SubElement(server, 'cpu')
    cpu_elem.text = cpu

    ram_elem = ET.SubElement(server, "ram")
    ram_elem.text = ram

    hdd_elem = ET.SubElement(server, "hdd")
    hdd_elem.text = hdd

    price_elem = ET.SubElement(server, "price")
    price_elem.text = price

    root.insert(len(root), server)

    with open('catalog.xml', 'wb') as f:
        tree.write(f)
        return redirect(url_for('index'))

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
