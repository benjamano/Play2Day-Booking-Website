from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("dummydata.htapp = Flask(__name__)ml", comments=comments)

    comments.append(request.form["contents"])
    return redirect(url_for('index'))