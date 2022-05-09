from flask import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['pwd'] == "admin" and request.form['isAdmin'] == "True":
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return make_response("I don't know how to protect against you " + flag), 200
        else:
            return render_template('index.html', loginFailed=True)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
