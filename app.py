import flask

from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return flask.redirect('/home')

@app.route('/home')
def home():
    return 'hi'

if __name__ == '__main__':
    app.run()
