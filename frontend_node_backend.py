from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get-url', methods=['GET'])
def get_url():
    return jsonify({"url": "http://localhost:5000"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)