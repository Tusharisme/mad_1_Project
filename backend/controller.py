from flask import Flask, render_template, request
from flask import current_app as app  # Alias for current running app
from flask import redirect, url_for, session

from backend.models import *
import datetime


@app.route("/")
def home():
    return "Hellloooo"


@app.route("/login", methods=["GET", "POST"])
def user_login():
    # Check if user is already logged in as admin
    if "username" in session:
        usr = Customer.query.filter_by(username=session["username"]).first()
        if usr and usr.role == 0:  # If admin is logged in
            services = fetch_all_services()
            professionals = fetch_all_professional()
            return render_template(
                "admin_dashboard.html",
                admin=usr.username,
                services=services,
                professionals=professionals,
            )

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pwd")
        usr = Customer.query.filter_by(email=email, password=password).first()
        usr1 = Service_Professional.query.filter_by(
            email=email, password=password
        ).first()

        if usr and usr.role == 0:  # Admin login
            session["username"] = usr.username  # Store admin username in session
            services = fetch_all_services()  # Fetch services
            return render_template(
                "admin_dashboard.html", admin=usr.username, services=services
            )
        elif usr and usr.role != 0:  # Normal customer login
            return render_template("customer_dashboard.html", customer=usr.username)
        elif not usr and usr1:  # Service professional login
            return render_template(
                "professional_dashboard.html", professional=usr1.username
            )
        else:
            return render_template("login.html", msg="Invalid Credentials")

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


@app.route("/register", methods=["GET", "POST"])  # for the professional
def prof_register():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("pwd")
        fullname = request.form.get("full_name")
        email = request.form.get("email")
        experience = request.form.get("experience")
        formFileSm = request.files.get("formFileSm")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        usr = Service_Professional.query.filter_by(email=email).first()
        if not usr:
            new_usr = Service_Professional(
                username=uname,
                password=password,
                name=fullname,
                email=email,
                address=address,
                experience=experience,
                document=formFileSm,
                pin_code=pin_code,
            )
            db.session.add(new_usr)
            db.session.commit()
            return render_template("login.html")
        else:
            return render_template(
                "professional_dashboard.html", professional=usr.username
            )
    return render_template("service_prof.html")


@app.route("/service", methods=["GET", "POST"])
def service_register():
    if request.method == "POST":
        name = request.form.get("service_name")
        description = request.form.get("description")
        price = request.form.get("base_price")

        # Directly create and add the new service without checking for duplicates
        new_service = Service(
            name=name,
            description=description,
            price=price,
        )
        db.session.add(new_service)
        db.session.commit()

        # Fetch updated service list
        updated_services = fetch_all_services()

        # Assuming the admin username is stored in the session after login
        admin_username = session.get("username")

        # Directly render admin_dashboard.html with updated services and admin details
        return render_template(
            "admin_dashboard.html", admin=admin_username, services=updated_services
        )

    return render_template("service.html", msg="")


def fetch_all_services():
    services = Service.query.all()
    service_list = {}
    for service in services:
        if service.id not in service_list.keys():
            service_list[service.id] = [service.name, service.price]
    return service_list


@app.route("/service/<int:service_id>", methods=["GET"])
def service_details(service_id):
    # Fetch the service details using the provided service ID
    service = Service.query.get(service_id)

    if service:
        return render_template("service_details.html", service=service)
    else:
        # If the service does not exist, return an error or redirect
        return "Service not found", 404


def fetch_all_professional():
    professionals = Service_Professional.query.all()
    professional_list = {}
    for professional in professionals:
        if professional.id not in professional_list.keys():
            professional_list[professional.id] = [
                professional.name,
                professional.experience,
            ]
    return professional_list


@app.route("/professional/<int:professional_id>", methods=["GET"])
def professional_details(professional_id):
    # Fetch the service details using the provided service ID
    professional = Service_Professional.query.get(professional_id)

    if professional:
        return render_template("professional_details.html", professional=professional)
    else:
        # If the service does not exist, return an error or redirect
        return "Service not found", 404