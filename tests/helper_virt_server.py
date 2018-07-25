from flask import Flask
app = Flask(__name__)
import json
import os

@app.route("/register", methods=['POST'])
def register():
    data = {
        "status": "ok",
        "username": "guac_username",
        "password": "guac_password",
    }
    return json.dumps(data)

if __name__ == '__main__':
  app.run(host=os.getenv('ADMIN_HOST', 'localhost'), port=os.getenv('ADMIN_PORT', 3331))
