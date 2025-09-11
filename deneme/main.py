from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("deneme.html")


if __name__ == "__main__":
    app.run(debug=True)
