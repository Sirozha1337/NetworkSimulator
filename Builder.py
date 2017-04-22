from flask import Flask, request
import os

app = Flask(__name__)
static_folder_root = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')

