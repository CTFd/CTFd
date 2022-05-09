from flask import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    cookie = request.cookies.get('isAdmin')
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['pwd'] == "admin" and cookie == "True":
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return make_response("Here's the flag, don't ask me again for it " + flag), 200
        else:
            return render_template('index.html', loginFailed=True)
    else:
        resp = make_response(render_template('index.html'))
        if not cookie:
            resp.set_cookie('isAdmin', 'False', max_age=60*60*24)
            resp.headers['location'] = url_for('login')
        return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0')
