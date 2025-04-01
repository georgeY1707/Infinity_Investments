from flask import Flask, render_template

app = Flask(__name__)


@app.route('/authPage')
def auth_page():
    return render_template('authPage.html')

@app.route('/regPage')
def reg_page():
    return render_template('regPage.html')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')