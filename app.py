import zipfile, os, requests, types, threading, random, string, wget, pika
from flask import Flask, request, render_template, jsonify, send_from_directory
from functools import partial

app = Flask(__name__)
app.config.from_object(__name__)

UPLOAD_FOLDER = './'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    uniqueId = randomId()
    return render_template('index.html', uniqueId = uniqueId)

def randomId():
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(10))

@app.route('/download/', methods=['POST'])
def download():
    try:
        uniqueId = request.args.to_dict().get("uniqueId")
        url = request.form.get('url')
        threading.Thread(target=download_file, args=[url, uniqueId]).start()
    except:
        print("failed")
    return "success"

def download_file(url, uniqueId):
    filename = wget.download(url, bar=partial(progress_report, uniqueId))
    os.replace("./" + filename, "./storage/" + filename)
    
    global server
    server.publish(payload="done http://152.118.148.95:20648/get_file/" + filename, routing_key=uniqueId)


@app.route('/get_file/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'] + "storage/", filename)

def progress_report(uniqueId, current, total, width):
    percent = (100*int(current))/int(total)
    global server
    server.publish(payload=str("progress " + str(percent)), routing_key=uniqueId)


class RabbitMq():

    def __init__(self, queue="hello"):
        self._credential = pika.PlainCredentials('0806444524', '0806444524')
        self._connection = pika.BlockingConnection(pika.ConnectionParameters('152.118.148.95', 5672, '/0806444524', self._credential))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange='1706039515', exchange_type='direct')

    def publish(self, payload = "", routing_key=""):

        self._channel.basic_publish(exchange="1706039515",
                                    routing_key=routing_key,
                                    body=str(payload))


if __name__ == '__main__':
    global server
    server = RabbitMq('upload')
    app.run(host='0.0.0.0', port=20648)

