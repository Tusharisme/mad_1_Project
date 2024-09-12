from flask import Flask, render_template, request
from flask import current_app as app  # Alias for current running app

from backend.models import *
import datetime


@app.route("/")
def home():
    return "Hellloooo"


@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pwd")
        usr = Customer.query.filter_by(
            email=email, password=password
        ).first()  # Get existig user matched
        if usr and usr.role == 0:
            return render_template("admin_dashboard.html", admin=usr.username)
        elif usr and usr.role != 0:
            return render_template("customer_dashboard.html")
        else:
            return render_template("login.html", msg="Inavlid Credentials")
    return render_template("login.html", msg="")


@app.route("/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("pwd")
        fullname = request.form.get("full_name")
        email = request.form.get("email")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        usr = Customer.query.filter_by(email=email, password=password).first()
        if not usr:
            new_usr = Customer(
                username=uname,
                password=password,
                name=fullname,
                email=email,
                address=address,
                pin_code=pin_code,
            )
            db.session.add(new_usr)
            db.session.commit()
            return render_template("login.html")
    return render_template("signup.html")


@app.route("/register", methods=["GET", "POST"])
def prof_register():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("pwd")
        fullname = request.form.get("full_name")
        email = request.form.get("email")
        experience = request.form.get("experience")
        formFileSm = request.form.get("formFileSm")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
    return render_template("signup.html")
