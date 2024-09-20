from flask import Flask, render_template, request
from flask import current_app as app  # Alias for current running app
from flask import redirect, url_for, session
from flask import current_app
from flask import session, jsonify
import os
from werkzeug.utils import secure_filename

from backend.models import *
import datetime


@app.route("/")
def home():
    return "Hellloooo"


@app.route("/logout")
def logout():
    # Only clear the session if the admin is logged in
    if "username" in session:
        session.pop("username", None)  # Remove admin session

    # Redirect to login page for all users
    return redirect(url_for("user_login"))


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
            updated_professional = fetch_all_professional()  # fetch professionals
            return render_template(
                "admin_dashboard.html",
                admin=usr.username,
                services=services,
                professionals=updated_professional,
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


# Function to save the uploaded document
def save_document(file):
    # Get the filename and ensure it's secure
    filename = secure_filename(file.filename)

    # Get the full path where the file will be saved
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    # Save the file
    file.save(file_path)

    return file_path  # Return the file path for storing in the database




@app.route("/register", methods=["GET", "POST"])  # for the professional
def prof_register():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("pwd")
        fullname = request.form.get("full_name")
        email = request.form.get("email")
        experience = request.form.get("experience")
        formFileSm = request.files.get(
            "document"
        )  # Correcting the formFileSm to document
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        service_type = request.form.get(
            "service_type"
        )  # Capturing service type directly

        # Check if the professional already exists by email
        usr = Service_Professional.query.filter_by(email=email).first()

        if not usr:
            # If file is uploaded, save it to a specific folder (adjust paths as necessary)
            document_path = None
            if formFileSm:
                document_path = save_document(
                    formFileSm
                )  # Assuming save_document handles saving

            # Create a new service professional
            new_usr = Service_Professional(
                username=uname,
                password=password,
                name=fullname,
                email=email,
                address=address,
                experience=experience,
                document=document_path,  # Saving the file path
                pin_code=pin_code,
                service_type=service_type,  # Saving the service type
            )

            # Fetch the selected service by name from the form
            service = Service.query.filter_by(name=service_type).first()
            if service:
                # Create a new ProfessionalService entry to link the professional and the service
                professional_service = ProfessionalService(
                    professional=new_usr,
                    service=service,
                    custom_price=None,  # You can add custom price and other fields here if needed
                    custom_description=None,
                )

                # Add the new professional and their service association to the database
                db.session.add(new_usr)
                db.session.add(professional_service)
                db.session.commit()

            # Redirect to login page after successful registration
            return render_template("login.html")

        else:
            # If the professional already exists, render their dashboard
            return render_template(
                "professional_dashboard.html", professional=usr.username
            )

    # On GET request, render the service professional signup form
    available_services = (
        Service.query.all()
    )  # Fetch the available services to populate the form
    return render_template("service_prof.html", available_services=available_services)


@app.route("/services/add", methods=["GET", "POST"])
def add_service():
    service_name = request.form.get("service_name")
    description = request.form.get("description")
    base_price = request.form.get("base_price")

    new_service = Service(
        name=service_name, description=description, base_price=base_price
    )
    db.session.add(new_service)
    db.session.commit()
    # Fetch updated service list
    updated_services = fetch_all_services()
    updated_professional = fetch_all_professional()

    # Assuming the admin username is stored in the session after login
    admin_username = session.get("username")

    # Directly render admin_dashboard.html with updated services and admin details
    return render_template(
        "admin_dashboard.html",
        admin=admin_username,
        services=updated_services,
        professionals=updated_professional,
    )


@app.route("/services/edit/<int:service_id>", methods=["POST"])
def edit_service(service_id):
    new_service_name = request.form.get("service_name")
    new_description = request.form.get("description")
    new_base_price = request.form.get("base_price")

    # Fetch the service by id
    service = Service.query.filter_by(id=service_id).first()

    if service:
        # Update the service details
        service.name = new_service_name
        service.description = new_description
        service.base_price = new_base_price
        db.session.commit()

    # Redirect to login page after successful edit
    return redirect(url_for("user_login"))


@app.route("/services/delete/<int:service_id>", methods=["POST"])
def delete_service(service_id):
    service = Service.query.get(service_id)

    if service:
        db.session.delete(service)
        db.session.commit()

    # Redirect to login page after successful deletion
    return redirect(url_for("user_login"))


def fetch_all_services():
    services = Service.query.all()
    service_list = {}
    for service in services:
        service_list[service.id] = [
            service.name,
            service.base_price,
            service.description,
        ]  # Add description
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
        professional_list[professional.id] = [
            professional.name,
            professional.experience,
            professional.service_type,
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


@app.route("/professional/approve/<int:professional_id>", methods=["POST"])
def approve_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        professional.verified_status = "approved"
        db.session.commit()
    return redirect(url_for("user_login", update_dashboard=True))


@app.route("/professional/reject/<int:professional_id>", methods=["POST"])
def reject_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        professional.verified_status = "rejected"
        db.session.commit()
    return redirect(url_for("user_login"))


@app.route("/professional/delete/<int:professional_id>", methods=["POST"])
def delete_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        db.session.delete(professional)
        db.session.commit()
    return redirect(url_for("user_login", update_dashboard=True))


@app.route("/api/request_service", methods=["POST"])
def request_service():
    # Get data from the request
    service_id = request.json["service_id"]
    customer_id = request.json["customer_id"]

    # Find professionals who offer this service
    professionals = Service_Professional.query.filter_by(service_id=service_id).all()

    if professionals:
        # Select a professional (for example, the first one for simplicity)
        professional = professionals[0]

        # Create a new service request
        new_request = Service_Request(
            customer_id=customer_id,
            professional_id=professional.id,
            service_id=service_id,
        )

        # Save the request to the database
        db.session.add(new_request)
        db.session.commit()

        return jsonify({"message": "Service request submitted successfully"}), 200
    else:
        return jsonify({"message": "No professionals available for this service"}), 404


@app.route("/professional_dashboard", methods=["GET"])
def professional_dashboard():
    # Get professional details
    professional_id = session["professional_id"]

    # Fetch assigned service requests
    requests = Service_Request.query.filter_by(
        professional_id=professional_id, service_status="open"
    ).all()

    return render_template("professional_dashboard.html", requests=requests)


@app.route('/api/professional/<int:professional_id>', methods=['GET'])
def get_professional_details(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if not professional:
        return jsonify({'error': 'Professional not found'}), 404

    return jsonify({
        'name': professional.name,
        'experience': professional.experience,
        'service_type': professional.service_type,
        'address': professional.address,
        'pin_code': professional.pin_code,
        'verified_status': professional.verified_status
    })




# @app.route("/register", methods=["GET", "POST"])  # for the professional
# def prof_register():
#     if request.method == "POST":
#         uname = request.form.get("uname")
#         password = request.form.get("pwd")
#         fullname = request.form.get("full_name")
#         email = request.form.get("email")
#         experience = request.form.get("experience")
#         formFileSm = request.files.get(
#             "document"
#         )  # Correcting the formFileSm to document
#         address = request.form.get("address")
#         pin_code = request.form.get("pin_code")
#         service_type = request.form.get(
#             "service_type"
#         )  # Updated to capture service type directly

#         # Check if the professional already exists by email
#         usr = Service_Professional.query.filter_by(email=email).first()

#         if not usr:
#             # If file is uploaded, save it to a specific folder (adjust paths as necessary)
#             document_path = None
#             if formFileSm:
#                 document_path = save_document(
#                     formFileSm
#                 )  # Assuming save_document handles saving

#             # Create a new service professional
#             new_usr = Service_Professional(
#                 username=uname,
#                 password=password,
#                 name=fullname,
#                 email=email,
#                 address=address,
#                 experience=experience,
#                 document=document_path,  # Saving the file path
#                 pin_code=pin_code,
#                 service_type=service_type,  # Saving the service type
#             )

#             # Fetch the selected service by name from the form
#             service = Service.query.filter_by(name=service_type).first()
#             if service:
#                 new_usr.services.append(
#                     service
#                 )  # Associate the service with the professional

#             # Add the new professional to the database
#             db.session.add(new_usr)
#             db.session.commit()

#             # Redirect to login page after successful registration
#             return render_template("login.html")

#         else:
#             # If the professional already exists, render their dashboard
#             return render_template(
#                 "professional_dashboard.html", professional=usr.username
#             )

#     # On GET request, render the service professional signup form
#     available_services = (
#         Service.query.all()
#     )  # Fetch the available services to populate the form
#     return render_template("service_prof.html", available_services=available_services)
