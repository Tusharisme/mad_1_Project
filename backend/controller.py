from flask import Flask, flash, render_template, request
from flask import current_app as app  # Alias for current running app
from flask import redirect, url_for, session
from flask import current_app
from flask import session, jsonify
import os
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from backend.models import *
from datetime import datetime


@app.route("/")
def home():
    return "Hellloooo"


@app.route("/logout")
def logout():
    # Clear the session for all users (admin, customer, professional)
    session.clear()  # This removes all session data

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
            session["customer_id"] = usr.id  # Store customer ID in session
            services = fetch_all_services()  # Fetch services
            updated_professional = fetch_all_professional()  # Fetch professionals
            return render_template(
                "admin_dashboard.html",
                admin=usr.username,
                services=services,
                professionals=updated_professional,
            )
        elif usr and usr.role != 0:  # Normal customer login
            session["username"] = usr.username  # Store customer username in session
            session["customer_id"] = usr.id  # Store customer ID in session
            return redirect(url_for("customer_dashboard"))
        elif not usr and usr1:  # Service professional login
            session["username"] = (
                usr1.username
            )  # Store professional username in session
            session["professional_id"] = usr1.id  # Store professional ID in session
            return redirect(url_for("professional_dashboard"))
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
        phone_no = request.form.get("phone_no")
        usr = Customer.query.filter_by(email=email, password=password).first()
        if not usr:
            new_usr = Customer(
                username=uname,
                password=password,
                name=fullname,
                email=email,
                address=address,
                pin_code=pin_code,
                phone_no=phone_no,
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
        phone_no = request.form.get("phone_no")
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
                phone_no=phone_no,
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


# @app.route("/professional/delete/<int:professional_id>", methods=["POST"])
# def delete_professional(professional_id):
#     professional = Service_Professional.query.get(professional_id)
#     if professional:
#         db.session.delete(professional)
#         db.session.commit()
#     return redirect(url_for("user_login", update_dashboard=True))
@app.route("/professional/delete/<int:professional_id>", methods=["POST"])
def delete_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        db.session.delete(
            professional
        )  # This will also delete all related service requests
        db.session.commit()
        flash("Professional and related service requests deleted successfully!")
    else:
        flash("Professional not found.")

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


# @app.route("/professional_dashboard", methods=["GET"])
# def professional_dashboard():
#     # Get professional details
#     professional_id = session["professional_id"]

#     # Fetch assigned service requests
#     requests = Service_Request.query.filter_by(
#         professional_id=professional_id, service_status="open"
#     ).all()

#     return render_template("professional_dashboard.html", requests=requests)


@app.route("/api/professional/<int:professional_id>", methods=["GET"])
def get_professional_details(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if not professional:
        return jsonify({"error": "Professional not found"}), 404

    return jsonify(
        {
            "name": professional.name,
            "experience": professional.experience,
            "service_type": professional.service_type,
            "address": professional.address,
            "pin_code": professional.pin_code,
            "verified_status": professional.verified_status,
        }
    )


# @app.route("/customer_dashboard", methods=["GET"])
# def customer_dashboard():
#     usr = Customer.query.filter_by(username=session.get("username")).first()
#     if usr:
#         # Fetch customer profile, service history, and other relevant data
#         service_history = Service_Request.query.filter_by(customer_id=usr.id).all()
#         profile_data = {
#             "name": usr.name,
#             "email": usr.email,
#             "address": usr.address,
#             "pin_code": usr.pin_code,
#         }

#         return render_template(
#             "customer_dashboard.html",
#             customer=usr.username,
#             profile=profile_data,
#             service_history=service_history,
#             # Add other data needed for the customer dashboard
#         )
#     else:
#         return redirect(url_for("user_login"))  # Redirect to login if not authenticated


@app.route("/customer_dashboard")
def customer_dashboard():
    # Assuming the logged-in customer's ID is stored in the session
    customer_id = session.get("customer_id")

    if not customer_id:
        return redirect(url_for("user_login"))

    # Fetch all available services (for the service categories section)
    services = Service.query.all()

    # Fetch all service requests for the logged-in customer (for the service history section)
    service_requests = Service_Request.query.filter_by(customer_id=customer_id).all()

    # Render the customer dashboard template with both services and service requests
    return render_template(
        "customer_dashboard.html",
        services=services,
        service_requests=service_requests,
        customer=session.get("username"),  # Assuming customer_name is stored in session
    )


@app.route("/services/<int:service_id>", methods=["GET"])
def get_service_professionals(service_id):
    service = Service.query.get_or_404(service_id)
    professionals = (
        Service_Professional.query.join(ProfessionalService)
        .filter(ProfessionalService.service_id == service_id)
        .all()
    )
    return render_template(
        "service_professionals.html", service=service, professionals=professionals
    )


@app.route("/book_service", methods=["POST"])
def book_service():
    service_id = request.form.get("service_id")
    professional_id = request.form.get("professional_id")
    customer_id = session.get("customer_id")    

    if service_id and professional_id and customer_id:
        new_request = Service_Request(
            service_id=service_id,
            customer_id=customer_id,
            professional_id=professional_id,
            date_of_request=datetime.utcnow(),
            service_status="requested",
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Service booked successfully!")
        return redirect(url_for("customer_dashboard"))
    else:
        flash("Failed to book service. Try again.")
        return redirect(url_for("customer_dashboard"))


@app.route("/search_service", methods=["POST"])
def search_service():
    search_term = request.form.get("service_name")

    # Perform a case-insensitive search for the service
    services = Service.query.filter(Service.name.ilike(f"%{search_term}%")).all()

    # If no services match the search term, return an empty list
    if not services:
        return render_template(
            "services_by_category.html",
            services=[],
            category=f"Search Results for: {search_term}",
        )

    # Render search results
    return render_template(
        "services_by_category.html",
        services=services,
        category=f"Search Results for: {search_term}",
    )


# @app.route("/close_service", methods=["POST"])
# def close_service():
#     data = request.get_json()  # or use form data
#     request_id = data.get("requestId")
#     rating = data.get("serviceRating")
#     remarks = data.get("serviceRemarks")

#     service_request = Service_Request.query.get(request_id)
#     if service_request:
#         service_request.rating = rating  # Ensure your model has this field
#         service_request.remarks = remarks
#         service_request.service_status = "closed"  # Update status if needed
#         service_request.date_of_completion = datetime.utcnow()  # Set completion date
#         db.session.commit()  # Commit the changes


#     return redirect(url_for("customer_dashboard"))  # Redirect to the dashboard
@app.route("/close_service", methods=["POST"])
def close_service():
    data = request.get_json()
    request_id = data["requestId"]
    rating = data["serviceRating"]
    remarks = data["serviceRemarks"]
    # Validate rating
    if not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    service_request = Service_Request.query.get(request_id)
    if service_request:
        # Update rating and remarks
        service_request.rating = rating
        service_request.remarks = remarks
        # Set status to closed
        service_request.service_status = "closed"
        service_request.date_of_completion = datetime.utcnow()  # Set completion date
        db.session.commit()
        return redirect(url_for("customer_dashboard"))


@app.route("/professional_dashboard")
def professional_dashboard():
    if "professional_id" in session:  # Check if professional is logged in
        professional_id = session["professional_id"]

        # Fetching service requests specific to the logged-in professional and eager load professional relationship
        service_requests = (
            Service_Request.query.options(
                joinedload(
                    Service_Request.professional
                )  # Eager load the professional relationship
            )
            .filter_by(professional_id=professional_id)
            .all()
        )
        # service_requests.service_status == "pending"

        # Fetch today's services, including both requested and accepted services
        today_services = [
            req
            for req in service_requests
            if req.service_status in ["requested", "ongoing"]
        ]
        closed_services = [
            req for req in service_requests if req.service_status == "closed"
        ]

        return render_template(
            "professional_dashboard.html",
            today_services=today_services,
            closed_services=closed_services,
            professional=session.get("username"),
        )


# @app.route("/complete_service/<int:request_id>", methods=["POST"])
# def complete_service(request_id):
#     service_request = Service_Request.query.get(request_id)
#     professional_id = session["professional_id"]


#     if service_request and service_request.professional_id == professional_id:
#         service_request.service_status = "accepted"
#         service_request.date_of_completion = datetime.utcnow()
#         db.session.commit()
#         return redirect(url_for("professional_dashboard"))
@app.route("/complete_service/<int:request_id>", methods=["POST"])
def complete_service(request_id):
    service_request = Service_Request.query.get(request_id)
    professional_id = session["professional_id"]

    if service_request and service_request.professional_id == professional_id:
        # Update status to ongoing instead of accepted
        service_request.service_status = "ongoing"
        service_request.date_of_completion = None  # Reset completion date if needed
        db.session.commit()
        return redirect(url_for("professional_dashboard"))


@app.route("/reject_service/<int:request_id>", methods=["POST"])
def reject_service(request_id):
    service_request = Service_Request.query.get(request_id)
    professional_id = session["professional_id"]

    if service_request and service_request.professional_id == professional_id:
        # db.session.delete(service_request)
        service_request.service_status = "rejected"
        service_request.date_of_completion = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("professional_dashboard"))


# @app.route("/close_service_professional/<int:request_id>", methods=["POST"])
# def close_service_professional(request_id):
#     service_request = Service_Request.query.get(request_id)
#     professional_id = session["professional_id"]

#     if service_request and service_request.professional_id == professional_id:
#         # Update status to 'completed' instead of 'closed'
#         service_request.service_status = "completed"
#         service_request.date_of_completion = datetime.utcnow()
#         db.session.commit()
#         return redirect(url_for("professional_dashboard"))


@app.route("/close_service_professional/<int:request_id>", methods=["POST"])
def close_service_professional(request_id):
    service_request = Service_Request.query.get(request_id)
    professional_id = session["professional_id"]

    if service_request and service_request.professional_id == professional_id:
        service_request.service_status = "closed"
        service_request.date_of_completion = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("professional_dashboard"))
