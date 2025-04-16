from flask import Flask, jsonify
from flask_cors import cross_origin

app = Flask(__name__)

@app.route('/get-url', methods=['GET'])
@cross_origin()
def get_url():
    #This becomes the URL of the peer node that the frontend determines the new peer will connect to
    return jsonify({"url": "http://localhost:5000"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)