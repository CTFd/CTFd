from flask import Flask, request, render_template_string, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

@app.route('/')
def home():
    app.logger.info("Home page accessed")
    return render_template_string('''
        <h1>Welcome to the Vulnerable App</h1>
        <p>Use /ping?ip= to check IP availability</p>
    ''')

@app.route('/ping', methods=['GET'])
def ping():
    ip = request.args.get('ip', '')
    if not ip:
        return "No IP address provided.", 400

    cmd = f"ping -c 1 {ip}"
    result = os.popen(cmd).read()

    app.logger.info(f"Ping command executed: {cmd}")

    return render_template_string('''
        <h1>Check IP Availability</h1>
        <form method="get">
            <label>Enter IP address:</label>
            <input type="text" name="ip">
            <input type="submit" value="Ping">
        </form>
        <pre>{{ result }}</pre>
    ''', result=result)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error("Page not found: %s", (request.path))
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("Server error: %s", (str(e)))
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
