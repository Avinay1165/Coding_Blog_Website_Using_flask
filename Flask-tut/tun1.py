from flask import Flask, render_template

app=Flask(__name__)

@app.route("/")

def hello():
    name="Avinay Mehta"
    return render_template("index.html", name=name)

@app.route("/name")

def name():
    return "Its Avinay Here"

@app.route("/medicine")

def medicine():
    return render_template("flask_web//index.html")

app.run(debug=True)

