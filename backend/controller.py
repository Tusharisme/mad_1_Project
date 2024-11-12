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
    return render_template("homepage.html")


@app.route("/logout")
def logout():
    # Clear the session for all users (admin, customer, professional)
    session.clear()  # This removes all session data

    # Redirect to login page for all users
    return redirect(url_for("user_login"))


@app.route("/login", methods=["GET", "POST"])
def user_login():
    # Check if user is already logged in
    if "username" in session:
        return redirect(
            url_for("admin_dashboard")
            if session.get("role") == 0
            else (
                "customer_dashboard"
                if session.get("role") == 1
                else "professional_dashboard"
            )
        )

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pwd")

        # Fetch user as admin
        usr = Customer.query.filter_by(email=email).first()

        # Check if user is an admin
        if usr and usr.password == password and usr.role == 0:  # Admin login
            session["username"] = usr.username  # Store admin username in session
            session["customer_id"] = usr.id  # Store customer ID in session
            session["role"] = usr.role  # Store user role in session
            return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard

        # Fetch user as a service professional
        usr1 = Service_Professional.query.filter_by(email=email).first()

        # Check if user is a normal customer
        if usr and usr.password == password and usr.role != 0:  # Normal customer login
            session["username"] = usr.username  # Store customer username in session
            session["customer_id"] = usr.id  # Store customer ID in session
            session["role"] = usr.role  # Store user role in session
            return redirect(url_for("customer_dashboard"))

        # Check if user is a service professional
        elif usr1 and usr1.password == password:  # Service professional login
            session["username"] = (
                usr1.username
            )  # Store professional username in session
            session["professional_id"] = usr1.id  # Store professional ID in session
            return redirect(url_for("professional_dashboard"))

        # Invalid credentials message
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
        gender = request.form.get("gender")  # Get the gender from the form

        # Assign profile picture based on the selected gender
        if gender == "Male":
            profile_pic = "/static/images/male.png"  # Path to male profile picture
        elif gender == "Female":
            profile_pic = "/static/images/female.jpg"  # Path to female profile picture
        else:
            profile_pic = (
                "/static/images/default.jpg"  # Fallback in case gender is not specified
            )

        existing_user = (
            db.session.query(Customer.email)
            .filter_by(email=email)
            .union(db.session.query(Service_Professional.email).filter_by(email=email))
            .first()
        )

        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("user_login"))

        # Check if it's the first customer
        first_customer = Customer.query.first()
        if first_customer is None:  # No customers exist, make the new user an admin
            role = 0  # Admin role
        else:
            role = 1  # Customer role

        # Create the new user
        new_usr = Customer(
            username=uname,
            password=password,
            name=fullname,
            email=email,
            address=address,
            pin_code=pin_code,
            phone_no=phone_no,
            role=role,
            gender=gender,  # Save the gender to the database
            profile_pic=profile_pic,  # Save the profile picture path to the database
        )

        db.session.add(new_usr)
        db.session.commit()
        # Create a wallet for the new customer
        if role == 1:
            new_wallet = Wallet(customer_id=new_usr.id, balance=0.0)
            db.session.add(new_wallet)
            db.session.commit()

        return redirect(url_for("user_login"))

    return render_template("signup.html")


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
        gender = request.form.get("gender")  # Get the gender from the form

        # Assign profile picture based on the selected gender
        if gender == "Male":
            profile_pic = "/static/images/male.png"  # Path to male profile picture
        elif gender == "Female":
            profile_pic = "/static/images/female.jpg"  # Path to female profile picture
        else:
            profile_pic = (
                "/static/images/default.jpg"  # Fallback in case gender is not specified
            )
        # Use `or_` to check if the email exists in either Customer or Service_Professional
        existing_user = (
            db.session.query(Customer.email)
            .filter_by(email=email)
            .union(db.session.query(Service_Professional.email).filter_by(email=email))
            .first()
        )

        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("user_login"))

        if not existing_user:
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
                gender=gender,  # Save the gender to the database
                profile_pic=profile_pic,  # Save the profile picture path to the database
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
                "professional_dashboard.html", professional=existing_user.username
            )

    # On GET request, render the service professional signup form
    available_services = (
        Service.query.all()
    )  # Fetch the available services to populate the form
    return render_template("service_prof.html", available_services=available_services)


# =========================================  Admin  ========================================================


@app.route("/admin_dashboard")
def admin_dashboard():
    if (
        "username" in session and session.get("role") == 0
    ):  # Check if logged in as admin
        # Fetch services and count the number of professionals offering each service
        services_with_pro_count = (
            db.session.query(
                Service,
                func.count(ProfessionalService.professional_id).label(
                    "professional_count"
                ),
            )
            .outerjoin(
                ProfessionalService, Service.id == ProfessionalService.service_id
            )
            .group_by(Service.id)
            .all()
        )

        # Fetch all professionals with their full details
        professionals = db.session.query(Service_Professional).all()

        # Fetch all service requests
        service_requests = Service_Request.query.all()
        service_requests.sort(key=lambda request: request.id, reverse=True)

        # Fetch all customers
        customers = Customer.query.filter(Customer.role == 1).all()

        # Calculate the average rating for professionals
        for professional in professionals:
            professional_id = professional.id
            professional.average_rating = update_professional_rating(professional_id)

        # Calculate the average rating for customers
        for customer in customers:
            customer_id = customer.id
            customer.average_rating = update_customer_rating(customer_id)

        # Pass services with professional count to the template
        return render_template(
            "admin_dashboard.html",
            admin=session["username"],
            services=services_with_pro_count,
            professionals=professionals,
            customers=customers,
            service_requests=service_requests,
        )
    else:
        return redirect(url_for("user_login"))  # Redirect to login if not an admin


@app.route("/admin/summary", methods=["GET"])
def admin_summary():
    # Assuming the session contains the admin's username
    admin = session.get("username")
    return render_template("admin_summary.html", admin=admin)


@app.route("/admin/summary/api", methods=["GET"])
def admin_summary_api():
    # Fetch the data for customer ratings and service request summary
    customer_ratings = fetch_customer_ratings()
    service_request_summary = fetch_service_request_summary()

    return jsonify(
        {
            "customer_ratings": customer_ratings,
            "service_request_summary": service_request_summary,
        }
    )


@app.route("/search_admin", methods=["GET"])
def search_admin():
    entity = request.args.get("entity")
    criteria = request.args.get("criteria")
    query = request.args.get("query")
    rating_filter = request.args.get("rating")  # For rating filter
    rating_condition = request.args.get("rating_condition")

    results = []

    if entity == "service":
        if not query:
            results = Service.query.all()
        else:
            if criteria == "name":
                results = Service.query.filter(Service.name.ilike(f"%{query}%")).all()
            elif criteria == "base_price":
                results = Service.query.filter(Service.base_price == query).all()
            elif criteria == "description":
                results = Service.query.filter(
                    Service.description.ilike(f"%{query}%")
                ).all()

    elif entity == "professional":
        if not query and rating_filter:
            # Filter professionals by average_rating if rating_filter is provided
            if rating_condition == "high":
                results = Service_Professional.query.filter(
                    Service_Professional.average_rating >= float(rating_filter)
                ).all()
            elif rating_condition == "low":
                results = Service_Professional.query.filter(
                    Service_Professional.average_rating <= float(rating_filter)
                ).all()
            else:
                results = Service_Professional.query.all()
        else:
            if criteria == "name":
                results = Service_Professional.query.filter(
                    Service_Professional.name.ilike(f"%{query}%")
                ).all()
            elif criteria == "experience":
                results = Service_Professional.query.filter(
                    Service_Professional.experience == query
                ).all()
            elif criteria == "average_rating":
                if rating_filter:
                    if rating_condition == "high":
                        results = Service_Professional.query.filter(
                            Service_Professional.average_rating >= float(rating_filter)
                        ).all()
                    elif rating_condition == "low":
                        results = Service_Professional.query.filter(
                            Service_Professional.average_rating <= float(rating_filter)
                        ).all()
            elif criteria == "verified_status":
                results = Service_Professional.query.filter(
                    Service_Professional.verified_status.ilike(f"%{query}%")
                ).all()
            elif criteria == "blocked_status":
                block_value = True if query.lower() == "blocked" else False
                results = Service_Professional.query.filter(
                    Service_Professional.block_status == block_value
                ).all()
            else:
                results = Service_Professional.query.all()

    elif entity == "service_request":
        if not query:
            results = Service_Request.query.all()
        else:
            if criteria == "customer_name":
                results = (
                    Service_Request.query.join(Customer)
                    .filter(Customer.name.ilike(f"%{query}%"))
                    .all()
                )
            elif criteria == "service_status":
                results = Service_Request.query.filter(
                    Service_Request.service_status.ilike(f"%{query}%")
                ).all()

    elif entity == "customer":
        if not query:
            results = Customer.query.filter(Customer.role == 1).all()
        else:
            if criteria == "name":
                results = Customer.query.filter(
                    Customer.role == 1, Customer.name.ilike(f"%{query}%")
                ).all()
            elif criteria == "email":
                results = Customer.query.filter(
                    Customer.role == 1, Customer.email.ilike(f"%{query}%")
                ).all()
            elif criteria == "phone":
                results = Customer.query.filter(
                    Customer.role == 1, Customer.phone_no.ilike(f"%{query}%")
                ).all()

    return render_template(
        "search_results.html",
        results=results,
        category=f"Search Results for {entity.capitalize()}",
        entity=entity,
    )


@app.route("/customer/<int:customer_id>", methods=["GET"])
def customer_details(customer_id):
    # Your logic to display customer details
    customer = Customer.query.get(customer_id)
    if customer:
        return render_template("customer_details.html", customer=customer)
    else:
        flash("Customer not found.", "danger")
        return redirect(url_for("admin_dashboard"))


@app.route("/block_customer/<int:customer_id>", methods=["POST"])
def block_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.is_blocked = True  # Set the is_blocked field to True
    db.session.commit()
    flash("Customer has been blocked successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/unblock_customer/<int:customer_id>", methods=["POST"])
def unblock_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.is_blocked = False  # Set the is_blocked field to False
    db.session.commit()
    flash("Customer has been Unblocked successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/professional/block/<int:professional_id>", methods=["POST"])
def block_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        professional.block_status = True  # Set the block status to True
        db.session.commit()
        flash("Professional has been blocked successfully.", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for("admin_dashboard"))  # Redirect back to the admin dashboard


@app.route("/professional/unblock/<int:professional_id>", methods=["POST"])
def unblock_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        professional.block_status = False  # Set the block status to False
        db.session.commit()
        flash("Professional has been unblocked successfully.", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for("admin_dashboard"))  # Redirect back to the admin dashboard


# ============================================  Professional Routes  ============================================


@app.route("/professional_dashboard")
def professional_dashboard():
    if "professional_id" in session:  # Check if professional is logged in
        professional_id = session["professional_id"]
        professional = Service_Professional.query.get(professional_id)

        # Initialize the message variable
        message = None

        if professional:
            # Check the professional's verification and block status
            if professional.verified_status == "Not verified yet":
                message = "Your admin verification is under process."
            elif professional.verified_status == "approved":
                service_requests = Service_Request.query.filter_by(
                    professional_id=professional_id
                ).all()
                # Check if there are any service requests
                if not any(
                    req.service_status in ["requested", "accepted"]
                    for req in service_requests
                ):
                    flash(
                        "Your application has been approved. Please wait for service Requests.",
                        "success",
                    )
            elif professional.verified_status == "rejected":
                message = "Your application has been rejected. Please change your profile info."
            elif professional.block_status:
                message = "You have been blocked by admin and cannot book any services."

        # Fetching service requests specific to the logged-in professional
        service_requests = (
            Service_Request.query.options(
                joinedload(
                    Service_Request.professional
                )  # Eager load the professional relationship
            )
            .filter_by(professional_id=professional_id)
            .all()
        )

        # Fetch unique pin codes based on customers from the service requests
        pin_codes = (
            db.session.query(Customer.pin_code)
            .join(Service_Request)
            .filter(Service_Request.professional_id == professional_id)
            .distinct()
            .all()
        )
        pin_codes = [pin[0] for pin in pin_codes]  # Extracting pin codes from tuples

        # Fetch today's services, including both requested and accepted services
        today_services = [
            req
            for req in service_requests
            if req.service_status in ["requested", "accepted"]
        ]
        closed_services = [
            req for req in service_requests if req.service_status == "closed"
        ]

        return render_template(
            "professional_dashboard.html",
            today_services=today_services,
            closed_services=closed_services,
            message=message,  # This will always have a value
            pin_codes=pin_codes,
            professional=session["username"],
        )

    return redirect(url_for("user_login"))  # Redirect if not logged in


@app.route("/search_customers", methods=["GET"])
def search_customers():
    entity = request.args.get("entity")
    pin_code = request.args.get("pin_code")
    customer_name = request.args.get("customer_name")
    date_of_service = request.args.get("date_of_service")
    date_of_closing = request.args.get("date_of_closing")
    # query = request.args.get("query")

    service_requests_query = Service_Request.query.filter(
        Service_Request.professional_id == session["professional_id"]
    )

    # Filter by entity type
    if entity == "pin_code" and pin_code:
        service_requests_query = service_requests_query.filter(
            Service_Request.customer.has(pin_code=pin_code)
        )

    elif entity == "customer_name" and customer_name:
        service_requests_query = service_requests_query.filter(
            Service_Request.customer.has(Customer.name.ilike(f"%{customer_name}%"))
        )

    elif entity == "date_of_service" and date_of_service:
        try:
            date_of_service_obj = datetime.strptime(date_of_service, "%Y-%m-%d")
            service_requests_query = service_requests_query.filter(
                Service_Request.date_of_request == date_of_service_obj
            )
        except ValueError:
            print("Invalid date format for date of service. Please use YYYY-MM-DD.")

    elif entity == "date_of_closing" and date_of_closing:
        try:
            date_of_closing_obj = datetime.strptime(date_of_closing, "%Y-%m-%d")
            service_requests_query = service_requests_query.filter(
                Service_Request.date_of_completion >= date_of_closing_obj,
                Service_Request.date_of_completion
                < date_of_closing_obj.replace(hour=23, minute=59, second=59),
            )
        except ValueError:
            print("Invalid date format for closing date. Please use YYYY-MM-DD.")

    # Fetch the matching service requests
    service_requests = service_requests_query.all()

    # Initialize a set to collect unique customers
    matching_customers = set()

    for service_request in service_requests:
        matching_customers.add(
            service_request.customer
        )  # Use a set to avoid duplicates

    return render_template(
        "matching_customers.html",
        customers=list(matching_customers),
        category="Matching Customers",
    )


@app.route("/accept_service/<int:service_request_id>", methods=["POST"])
def accept_service(service_request_id):
    service_request = Service_Request.query.get(service_request_id)
    professional_id = session.get("professional_id")

    if service_request:
        service_request.service_status = "accepted"
        db.session.commit()

        # Retrieve the payment record
        payment = Payment.query.filter_by(service_request_id=service_request_id).first()
        if payment:
            payment.is_transferred = True
            payment.payment_status = "completed"

            # Find the custom price for this service request if it exists
            professional_service = ProfessionalService.query.filter_by(
                professional_id=service_request.professional_id,
                service_id=service_request.service_id,
            ).first()

            # Use custom price if set; otherwise, use base price
            amount_to_transfer = (
                professional_service.custom_price
                if professional_service and professional_service.custom_price
                else professional_service.service.base_price
            )

            # Update the payment record with the correct amount
            payment.amount = (
                amount_to_transfer  # Update the payment with the correct amount
            )

            # Fetch or create the professional's wallet
            professional_wallet = ProfessionalWallet.query.filter_by(
                professional_id=service_request.professional_id
            ).first()

            if not professional_wallet:
                professional_wallet = ProfessionalWallet(
                    professional_id=service_request.professional_id, balance=0
                )
                db.session.add(professional_wallet)

            # Transfer the calculated amount to the professional's wallet
            professional_wallet.balance += amount_to_transfer
            db.session.commit()

            flash(
                "Service request accepted and payment transferred to professional.",
                "success",
            )
            return redirect(url_for("professional_dashboard"))

    flash("Service request not found.", "danger")
    return redirect(url_for("professional_dashboard"))


@app.route("/reject_service/<int:service_id>", methods=["POST"])
def reject_service(service_id):
    service_request = Service_Request.query.get(service_id)

    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for("professional_dashboard"))

    if service_request.service_status == "requested":
        service_request.service_status = "rejected"

        # Fetch the related payment
        payment = Payment.query.filter_by(service_request_id=service_id).first()

        if payment:
            # Update payment status to "Refunded"
            payment.payment_status = "Refunded"

            # Calculate refund amount (custom price if available, else base price)
            professional_service = ProfessionalService.query.filter_by(
                professional_id=service_request.professional_id,
                service_id=service_request.service_id,
            ).first()

            refund_amount = (
                professional_service.custom_price
                if professional_service and professional_service.custom_price
                else professional_service.service.base_price
            )

            # Update customer's wallet balance
            wallet = Wallet.query.filter_by(
                customer_id=service_request.customer_id
            ).first()
            if wallet:
                wallet.balance += refund_amount
            else:
                # Create wallet if it doesn't exist
                wallet = Wallet(
                    customer_id=service_request.customer_id, balance=refund_amount
                )
                db.session.add(wallet)

            # Update the payment amount to the refunded amount
            payment.amount = (
                refund_amount  # Update the payment amount to reflect the refund
            )

        db.session.commit()
        flash("Service has been rejected and payment refunded.", "success")
    else:
        flash("Service cannot be rejected at this stage.", "warning")

    return redirect(url_for("professional_dashboard"))


@app.route("/professional_dashboard/summary")
def professional_summary():
    professional_id = session.get("professional_id")

    # Ratings data
    ratings_data = (
        db.session.query(Service_Request.rating, func.count(Service_Request.rating))
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.rating.isnot(None),
        )
        .group_by(Service_Request.rating)
        .all()
    )

    # Service status data (including requested services)
    service_status_data = {
        "requested": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "requested",
        )
        .count(),
        "accepted": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "accepted",
        )
        .count(),
        "rejected": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "rejected",
        )
        .count(),
        "completed": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "closed",
        )
        .count(),
    }

    # Prepare data in a JSON-friendly structure
    ratings_chart_data = {
        "labels": [str(r[0]) for r in ratings_data],  # Ensure they are strings
        "values": [r[1] for r in ratings_data],
    }
    status_chart_data = {
        "labels": list(service_status_data.keys()),
        "values": list(service_status_data.values()),
    }
    # Pass the data to the template
    return render_template(
        "professional_summary.html",
        ratings_data=ratings_chart_data,
        status_data=status_chart_data,
        professional=session["username"],
    )


@app.route("/professional_dashboard/summary/api")
def professional_summary_api():
    professional_id = session.get("professional_id")

    # Fetch ratings data
    ratings_data = (
        db.session.query(Service_Request.rating, func.count(Service_Request.rating))
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.rating.isnot(None),
        )
        .group_by(Service_Request.rating)
        .all()
    )

    # Fetch service status data (including requested services)
    service_status_data = {
        "requested": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "requested",
        )
        .count(),
        "accepted": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "accepted",
        )
        .count(),
        "rejected": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "rejected",
        )
        .count(),
        "completed": db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "closed",
        )
        .count(),
    }

    # Prepare data in a JSON-friendly structure
    ratings_chart_data = {
        "labels": [str(r[0]) for r in ratings_data],  # Ensure they are strings
        "values": [r[1] for r in ratings_data],
    }
    status_chart_data = {
        "labels": list(service_status_data.keys()),
        "values": list(service_status_data.values()),
    }

    return jsonify(
        {
            "ratings_data": ratings_chart_data,
            "status_data": status_chart_data,
        }
    )


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
        professional.block_status = (
            False  # Ensure the professional is unblocked upon approval
        )
        db.session.commit()
        flash("Professional approved successfully!", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(
        url_for("admin_dashboard")
    )  # Redirect to admin dashboard or another appropriate route


@app.route("/professional/reject/<int:professional_id>", methods=["POST"])
def reject_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)
    if professional:
        professional.verified_status = "rejected"
        # You can choose to block the professional or set additional flags if needed
        professional.block_status = True  # Block the professional upon rejection
        db.session.commit()
        flash(
            "Professional rejected. Please inform them to update their profile info.",
            "warning",
        )
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard


@app.route("/professional/delete/<int:professional_id>", methods=["POST"])
def delete_professional(professional_id):
    professional = Service_Professional.query.get(professional_id)

    if professional:
        # Check if the professional has an uploaded document
        if professional.document:
            document_path = os.path.join(
                current_app.root_path, "static", "uploads", professional.document
            )

            # Ensure the file exists before trying to delete it
            if os.path.exists(document_path):
                os.remove(document_path)  # Delete the document from the file system

        # Proceed to delete the professional from the database
        db.session.delete(professional)
        db.session.commit()

        flash(
            "Professional and related service requests deleted successfully!", "success"
        )
    else:
        flash("Professional not found.", "danger")

    return redirect(url_for("admin_dashboard"))


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


@app.route("/professional/profile", methods=["GET"])
def professional_profile():
    # Fetch the currently logged-in professional
    professional = Service_Professional.query.filter_by(
        id=session["professional_id"]
    ).first()

    if not professional:
        flash("Professional not found", "danger")
        return redirect(url_for("home"))

    # Fetch services associated with the professional
    professional_services = ProfessionalService.query.filter_by(
        professional_id=professional.id
    ).all()

    return render_template(
        "professional_profile.html",
        professional=professional,
        professional_services=professional_services,
    )


@app.route("/professional/profile/update", methods=["POST"])
def update_professional_profile():
    professional_id = session.get("professional_id")
    professional = Service_Professional.query.filter_by(id=professional_id).first()

    if not professional:
        flash("Professional not found", "danger")
        return redirect(url_for("professional_profile"))

    # Get the form data
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    address = request.form.get("address")
    pin_code = request.form.get("pin_code")
    gender = request.form.get("gender")  # Get the gender from the form

    # Check if the new username already exists in both tables, excluding the current professional
    existing_username_professional = Service_Professional.query.filter(
        Service_Professional.username == username,
        Service_Professional.id != professional_id,
    ).first()
    existing_username_customer = Customer.query.filter(
        Customer.username == username
    ).first()

    # Check if the new email already exists in both tables, excluding the current professional
    existing_email_professional = Service_Professional.query.filter(
        Service_Professional.email == email, Service_Professional.id != professional_id
    ).first()
    existing_email_customer = Customer.query.filter(Customer.email == email).first()

    if existing_username_professional or existing_username_customer:
        flash("Username already exists. Please choose a different one.", "danger")
        return redirect(url_for("professional_profile"))

    if existing_email_professional or existing_email_customer:
        flash("Email address already exists. Please choose a different one.", "danger")
        return redirect(url_for("professional_profile"))
    # Handle profile picture upload
    if "profile_pic" in request.files:
        file = request.files["profile_pic"]
        if file:
            professional_pic_path = save_professional_pic(file)  # Save the customer pic
            professional.profile_pic = f"/static/professional_pic/{professional_pic_path}"  # Save the path in the database

    # Update the professional's information
    professional.name = name
    professional.username = username
    professional.email = email
    professional.address = address
    professional.pin_code = pin_code
    professional.gender = gender  # Update the gender

    # Commit changes to the database
    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for("professional_profile"))


@app.route("/professional/profile/update_services", methods=["POST"])
def update_professional_services():
    professional_id = session.get("professional_id")
    if professional_id:
        professional_services = ProfessionalService.query.filter_by(
            professional_id=professional_id
        ).all()

        for service in professional_services:
            custom_price = request.form.get(f"custom_price_{service.service_id}")
            custom_description = request.form.get(
                f"custom_description_{service.service_id}"
            )
            custom_time_required = request.form.get(f"custom_time_{service.service_id}")
            base_price = service.service.base_price

            if custom_price:
                service.custom_price = custom_price
            if custom_description:
                service.custom_description = custom_description
            if custom_time_required:
                service.custom_time_required = custom_time_required
            if custom_price < str(base_price):
                flash(
                    "You cannot enter a custom price less than the base price.",
                    "danger",
                )
                return redirect(
                    url_for("professional_profile")
                )  # Redirect back to the profile

        db.session.commit()
        flash("Services updated successfully!", "success")
    return redirect(url_for("professional_profile"))


@app.route("/professional_payments")
def professional_payments():
    professional_id = session.get(
        "professional_id"
    )  # Assuming professional_id is stored in session

    if not professional_id:
        flash("Professional not logged in!", "danger")
        return redirect(url_for("login"))

    professional = Service_Professional.query.filter_by(id=professional_id).first()

    if not professional:
        flash("Professional not found!", "danger")
        return redirect(url_for("professional_dashboard"))

    # Fetch payments related to the professional, joining with Customer and ProfessionalService to get customer name and custom price
    payments = (
        db.session.query(
            Payment,
            Customer.name.label("customer_name"),
            ProfessionalService.custom_price,
        )
        .join(Customer, Payment.customer_id == Customer.id)
        .join(Service_Request, Payment.service_request_id == Service_Request.id)
        .join(
            ProfessionalService,
            (ProfessionalService.professional_id == professional_id)
            & (ProfessionalService.service_id == Service_Request.service_id),
        )
        .filter(Payment.professional_id == professional_id)
        .all()
    )

    # Get the wallet balance, defaulting to 0 if wallet doesn't exist
    wallet = ProfessionalWallet.query.filter_by(professional_id=professional_id).first()
    wallet_balance = wallet.balance if wallet else 0.0

    # Prepare payment details to pass to the template
    payment_details = []
    for row in payments:
        payment = row[0]  # Payment object
        customer_name = row[1]  # Customer name
        custom_price = row[2]  # Custom price

        # Determine the actual amount to show (payment amount or custom price if payment is missing)
        paid_amount = (
            payment.amount if payment.amount else (custom_price if custom_price else 0)
        )

        payment_details.append(
            {
                "payment": payment,
                "customer_name": customer_name,
                "paid_amount": paid_amount,  # Always show the paid amount or fallback to custom price if no payment was made
                "payment_status": payment.payment_status,
            }
        )

    # Render the template with the updated payment details
    return render_template(
        "professional_payments.html",
        payments=payment_details,
        wallet_balance=wallet_balance,
        professional=professional,
    )


# ============================================  Service Routes  ============================================


@app.route("/services/add", methods=["GET", "POST"])
def add_service():
    if request.method == "POST":
        service_name = request.form.get("service_name")
        description = request.form.get("description")
        base_price = request.form.get("base_price")
        base_time_required = request.form.get("base_time_required")

        # Handle the service picture upload
        service_pic = None
        if "service_pic" in request.files:
            file = request.files["service_pic"]
            if file and file.filename:  # Ensure a file is uploaded
                service_pic = save_service_picture(file)

        # Create and add new service
        new_service = Service(
            name=service_name,
            description=description,
            base_price=base_price,
            base_time_required=base_time_required,
            service_pic=(
                f"/static/service_pics/{service_pic}" if service_pic else None
            ),  # Store service picture path
        )
        db.session.add(new_service)
        db.session.commit()

        flash("Service added successfully!", "success")  # Flash message for feedback

        # Redirect to the admin dashboard after adding the service
        return redirect(url_for("admin_dashboard"))


@app.route("/services/edit/<int:service_id>", methods=["POST"])
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)

    service.name = request.form.get("service_name")
    service.description = request.form.get("description")
    service.base_price = request.form.get("base_price")
    service.base_time_required = request.form.get("base_time_required")

    # Handle the service picture upload
    if "service_pic" in request.files:
        file = request.files["service_pic"]
        if file and file.filename:  # Check if a file was uploaded
            filename = save_service_picture(file)  # Save the file and get the filename
            service.service_pic = (
                f"/static/service_pics/{filename}"  # Update the picture path
            )

    db.session.commit()
    flash("Service updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/services/delete/<int:service_id>", methods=["POST"])
def delete_service(service_id):
    service = Service.query.get(service_id)

    if service:
        db.session.delete(service)
        db.session.commit()

    # Redirect to login page after successful deletion
    return redirect(url_for("user_login"))


@app.route("/service/<int:service_id>", methods=["GET"])
def service_details(service_id):
    # Fetch the service details using the provided service ID
    service = Service.query.get(service_id)

    if service:
        return render_template("service_details.html", service=service)
    else:
        # If the service does not exist, return an error or redirect
        return "Service not found", 404


@app.route("/service_request/<int:request_id>", methods=["GET"])
def service_request_details(request_id):
    service_request = Service_Request.query.get(request_id)

    if not service_request:
        flash(f"Service request with ID {request_id} not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    # Fetch related customer, professional, and service details
    customer = Customer.query.get(service_request.customer_id)
    professional = Service_Professional.query.get(service_request.professional_id)
    service = Service.query.get(service_request.service_id)

    return render_template(
        "service_request_details.html",
        service_request=service_request,
        customer=customer,
        professional=professional,
        service=service,
    )


@app.route("/service_request_customer/<int:request_id>", methods=["GET"])
def service_request_customer(request_id):
    service_request = Service_Request.query.get(request_id)

    if not service_request:
        flash(f"Service request with ID {request_id} not found.", "danger")
        return redirect(url_for("customer_dashboard"))

    # Fetch related customer, professional, and service details
    customer = Customer.query.get(service_request.customer_id)
    professional = Service_Professional.query.get(service_request.professional_id)
    service = Service.query.get(service_request.service_id)

    return render_template(
        "service_request_customer.html",
        service_request=service_request,
        customer=customer,
        professional=professional,
        service=service,
    )


@app.route("/service_request_professional/<int:request_id>", methods=["GET"])
def service_request_professional(request_id):
    service_request = Service_Request.query.get(request_id)

    if not service_request:
        flash(f"Service request with ID {request_id} not found.", "danger")
        return redirect(url_for("professional_dashboard"))

    # Fetch related customer, professional, and service details
    customer = Customer.query.get(service_request.customer_id)
    professional = Service_Professional.query.get(service_request.professional_id)
    service = Service.query.get(service_request.service_id)

    return render_template(
        "service_request_professional.html",
        service_request=service_request,
        customer=customer,
        professional=professional,
        service=service,
    )


# ========================================  Customer Routes =======================================


@app.route("/customer_dashboard")
def customer_dashboard():
    # Assuming the logged-in customer's ID is stored in the session
    customer_id = session.get("customer_id")
    customer = Customer.query.get(customer_id)

    if not customer_id:
        return redirect(url_for("user_login"))

    # Fetch all available services (for the service categories section)
    services = Service.query.all()

    # Fetch distinct pin codes from the Service_Professional model
    pin_codes = db.session.query(Service_Professional.pin_code).distinct().all()
    pin_codes = [pin[0] for pin in pin_codes]  # Extract pin codes from query results

    # Fetch all service requests for the logged-in customer (for the service history section)
    service_requests = Service_Request.query.filter_by(customer_id=customer_id).all()
    # Sort the requests by ID in descending order
    service_requests.sort(key=lambda request: request.id, reverse=True)
    if customer.is_blocked:
        block_message = (
            "You have been blocked by the admin and cannot book any services."
        )
    else:
        block_message = ""

    # Render the customer dashboard template with both services and service requests
    return render_template(
        "customer_dashboard.html",
        block_message=block_message,
        services=services,
        service_requests=service_requests,
        pin_codes=pin_codes,
        customer=session.get("username"),  # Assuming customer_name is stored in session
    )


@app.route("/services/<int:service_id>", methods=["GET"])
def get_service_professionals(service_id):
    service = Service.query.get_or_404(service_id)
    customer = Customer.query.get(session["customer_id"])
    # Fetch professionals along with their custom services related to the current service
    professionals = (
        db.session.query(Service_Professional, ProfessionalService)
        .join(
            ProfessionalService,
            ProfessionalService.professional_id == Service_Professional.id,
        )
        .filter(
            ProfessionalService.service_id == service_id,
            Service_Professional.verified_status
            == "approved",  # Filter for approved professionals
        )
        .all()
    )

    return render_template(
        "service_professionals.html",
        service=service,
        professionals=professionals,
        customer=customer,
    )


@app.route("/book_service", methods=["POST"])
def book_service():
    service_id = request.form.get("service_id")
    professional_id = request.form.get("professional_id")
    customer_id = session.get("customer_id")
    requested_date = request.form.get("requested_date")  # Fetch requested date
    requested_time = request.form.get("requested_time")  # Fetch requested time

    # Fetch the customer from the database to check their blocked status
    customer = Customer.query.get(customer_id)

    # Check if the customer is blocked
    if customer.is_blocked:
        flash("You cannot book services as your account has been blocked.", "danger")
        return redirect(url_for("customer_dashboard"))

    # Convert requested_date and requested_time to correct format
    try:
        requested_date_obj = datetime.strptime(requested_date, "%Y-%m-%d").date()
        requested_time_obj = datetime.strptime(requested_time, "%H:%M").time()
    except ValueError:
        flash("Invalid date or time format.", "danger")
        return redirect(url_for("customer_dashboard"))

    # Check if the requested date is in the past
    if requested_date_obj < datetime.utcnow().date():
        flash("You cannot book a service for a date that has already passed.", "danger")
        return redirect(url_for("customer_dashboard"))

    # Fetch the service to get the amount
    service = Service.query.get(service_id)
    if not service:
        flash("Service not found.", "danger")
        return redirect(url_for("customer_dashboard"))

    amount = service.base_price  # Assuming the service has a field 'base_price'

    # Proceed with booking if the customer is not blocked and all data is available
    if service_id and professional_id and customer_id and amount:
        # Create the service request
        new_request = Service_Request(
            service_id=service_id,
            customer_id=customer_id,
            professional_id=professional_id,
            date_of_request=datetime.utcnow().date(),
            requested_date=requested_date_obj,
            requested_time=requested_time_obj,
            service_status="requested",
        )

        # Add and commit the new service request
        db.session.add(new_request)
        db.session.commit()  # Commit to get the new_request.id

        # Create the payment record without updating the wallet
        new_payment = Payment(
            service_request_id=new_request.id,
            customer_id=customer_id,
            professional_id=professional_id,
            amount=amount,
            payment_status="pending",  # Set as pending
            is_transferred=False,  # Initially, it's not transferred
            date_of_payment=datetime.utcnow(),
        )

        db.session.add(new_payment)
        db.session.commit()  # Commit the new payment record
        flash(
            "Service booked successfully! Awaiting professional's acceptance.",
            "success",
        )
        return redirect(url_for("customer_dashboard"))
    else:
        flash("Failed to book service. Please fill out all the fields.", "danger")
        return redirect(url_for("customer_dashboard"))


@app.route("/search_service", methods=["GET"])
def search_service():
    pin_code = request.args.get("pin_code")
    rating = request.args.get("rating")
    query = request.args.get("query")

    # Initialize the queries for services and professionals
    services_query = Service.query
    professionals_query = Service_Professional.query

    search_type = None

    # Filter by query (service name or description)
    if query:
        services_query = services_query.filter(
            Service.name.ilike(f"%{query}%") | Service.description.ilike(f"%{query}%")
        )
        search_type = "query"

    # Filter by pin code
    if pin_code:
        professionals_query = professionals_query.filter(
            Service_Professional.pin_code == pin_code,
            Service_Professional.verified_status == "approved",
        )
        search_type = "pin_code"

    # Filter by rating
    if rating is not None:
        rating_value = float(rating)  # Assuming the rating value is a number
        professionals_query = professionals_query.filter(
            (Service_Professional.average_rating >= rating)  # Check for average rating
            | (
                Service_Professional.id.in_(
                    db.session.query(Service_Request.professional_id).filter(
                        Service_Request.rating
                        >= rating  # Check past ratings if no average
                    )
                )
            )
        )
        search_type = "rating"

    # Execute the queries
    services = services_query.all()
    professionals = professionals_query.all()

    # Set the category message based on the search type
    if search_type == "query":
        category_message = f"Search results for '{query}'"
    elif search_type == "pin_code":
        category_message = f"Search results for pin code '{pin_code}'"
    elif search_type == "rating":
        category_message = f"Search results for rating '{rating}'"
    else:
        category_message = ""

    return render_template(
        "services_by_category.html",
        services=services,
        professionals=professionals,
        category=category_message,
        query=query,
    )


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


@app.route("/customer_dashboard/summary")
def customer_summary():
    customer_id = session.get("customer_id")

    # Ratings data
    ratings_data = (
        db.session.query(Service_Request.rating, func.count(Service_Request.rating))
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.rating.isnot(None),
        )
        .group_by(Service_Request.rating)
        .all()
    )

    # Service status data
    service_status_data = {
        "accepted": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "accepted",
        )
        .count(),
        "rejected": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "rejected",
        )
        .count(),
        "completed": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "closed",
        )
        .count(),
        "requested": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "requested",
        )
        .count(),  # Count for requested status
    }

    # Prepare data in a JSON-friendly structure
    ratings_chart_data = {
        "labels": [str(r[0]) for r in ratings_data],  # Ensure they are strings
        "values": [r[1] for r in ratings_data],
    }
    status_chart_data = {
        "labels": list(service_status_data.keys()),
        "values": list(service_status_data.values()),
    }

    return render_template(
        "customer_summary.html",
        ratings_data=ratings_chart_data,
        status_data=status_chart_data,
        customer=session["username"],
    )


@app.route("/customer_dashboard/summary/api")
def customer_summary_api():
    customer_id = session.get("customer_id")

    # Fetching ratings data
    ratings_data = (
        db.session.query(Service_Request.rating, func.count(Service_Request.rating))
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.rating.isnot(None),
        )
        .group_by(Service_Request.rating)
        .all()
    )

    # Preparing ratings chart data
    ratings_chart_data = {
        "labels": [str(r[0]) for r in ratings_data],  # Convert ratings to strings
        "values": [r[1] for r in ratings_data],
    }

    # Fetching service status data
    service_status_data = {
        "accepted": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "accepted",
        )
        .count(),
        "rejected": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "rejected",
        )
        .count(),
        "completed": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "closed",
        )
        .count(),
        "requested": db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "requested",
        )
        .count(),  # Count for requested status
    }

    # Preparing status chart data
    status_chart_data = {
        "labels": list(service_status_data.keys()),
        "values": list(service_status_data.values()),
    }

    return jsonify(
        {
            "ratings_data": ratings_chart_data,
            "status_data": status_chart_data,
        }
    )


@app.route("/customer_payments")
def customer_payments():
    customer_id = session.get("customer_id")

    if not customer_id:
        flash("User not logged in!", "danger")
        return redirect(url_for("login"))

    customer = Customer.query.filter_by(id=customer_id).first()

    if not customer:
        flash("Customer not found!", "danger")
        return redirect(url_for("customer_dashboard"))

    # Fetch the payments related to the customer and join with the Service_Professional table to get the professional name
    payments = (
        db.session.query(
            Payment,
            Service_Professional.name.label("professional_name"),
            ProfessionalService.custom_price,
            ProfessionalService.service_id,
        )
        .join(Service_Professional, Payment.professional_id == Service_Professional.id)
        .join(
            ProfessionalService,
            ProfessionalService.professional_id == Service_Professional.id,
        )
        .filter(Payment.customer_id == customer_id)
        .all()
    )

    # Get wallet balance, defaulting to 0 if wallet does not exist
    wallet = Wallet.query.filter_by(customer_id=customer_id).first()
    wallet_balance = wallet.balance if wallet else 0.0

    # Prepare payment details to pass to the template
    payment_details = []
    for row in payments:
        payment = row[0]  # Payment object
        professional_name = row[1]
        custom_price = row[2]
        service_id = row[3]

        # Always show the actual amount paid
        paid_amount = (
            payment.amount if payment.amount else 0
        )  # If payment exists, show the paid amount, else show 0.

        # Append the payment details to the list
        payment_details.append(
            {
                "payment": payment,
                "professional_name": professional_name,
                "paid_amount": paid_amount,  # This will now always show the actual amount paid.
                "service_id": service_id,
                "custom_price": custom_price,  # Optional for professional's reference.
            }
        )

    # Render the template with the updated payment details
    return render_template(
        "customer_payments.html",
        payments=payment_details,
        wallet_balance=wallet_balance,
        customer=customer,
    )


@app.route("/customer/profile", methods=["GET"])
def customer_profile():
    # Fetch the logged-in customer's details
    customer_id = session.get("customer_id")
    customer = Customer.query.filter_by(id=customer_id).first()

    if not customer:
        flash("Customer not found", "danger")
        return redirect(url_for("home"))

    return render_template("customer_profile.html", customer=customer)


@app.route("/customer/profile/update", methods=["POST"])
def update_customer_profile():
    customer_id = session.get("customer_id")
    customer = Customer.query.filter_by(id=customer_id).first()

    if not customer:
        flash("Customer not found", "danger")
        return redirect(url_for("customer_profile"))

    # Get the form data
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    address = request.form.get("address")
    pin_code = request.form.get("pin_code")
    phone_no = request.form.get("phone_no")
    gender = request.form.get("gender")  # Added gender field

    # Check if the new username already exists in the Customer table or Service Professional table
    existing_username_customer = Customer.query.filter(
        Customer.username == username, Customer.id != customer_id
    ).first()

    existing_username_professional = Service_Professional.query.filter(
        Service_Professional.username == username
    ).first()

    # Check if the new email already exists in the Customer table or Service Professional table
    existing_email_customer = Customer.query.filter(
        Customer.email == email, Customer.id != customer_id
    ).first()

    existing_email_professional = Service_Professional.query.filter(
        Service_Professional.email == email
    ).first()

    if existing_username_customer or existing_username_professional:
        flash("Username already exists. Please choose a different one.", "danger")
        return redirect(url_for("customer_profile"))

    if existing_email_customer or existing_email_professional:
        flash("Email address already exists. Please choose a different one.", "danger")
        return redirect(url_for("customer_profile"))

    # Handle profile picture upload
    if "profile_pic" in request.files:
        file = request.files["profile_pic"]
        if file:
            customer_pic_path = save_customer_pic(file)  # Save the customer pic
            customer.profile_pic = f"/static/customer_pic/{customer_pic_path}"  # Save the path in the database

    # Update the customer's information
    customer.name = name
    customer.username = username
    customer.email = email
    customer.address = address
    customer.pin_code = pin_code
    customer.phone_no = phone_no
    customer.gender = gender  # Update the gender

    # Commit changes to the database
    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for("customer_profile"))


@app.route("/rate_professional/<int:request_id>", methods=["POST"])
def rate_professional(request_id):
    service_request = Service_Request.query.get(request_id)
    customer_id = session["customer_id"]

    if service_request and service_request.customer_id == customer_id:
        service_request.rating = request.form.get("service_rating")
        service_request.remarks = request.form.get("service_remarks")
        db.session.commit()
        return redirect(url_for("customer_dashboard"))


@app.route("/cancel_service/<int:service_id>", methods=["POST"])
def cancel_service(service_id):
    service_request = Service_Request.query.get(service_id)

    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for("customer_dashboard"))

    # Check if the service status allows cancellation
    if service_request.service_status == "requested":
        # Update service request status
        service_request.service_status = "cancelled"

        # Fetch the related payment
        payment = Payment.query.filter_by(service_request_id=service_id).first()

        if payment:
            # Update payment status to "Cancelled"
            payment.payment_status = "Cancelled"

            # Calculate refund amount (custom price if available, else base price)
            professional_service = ProfessionalService.query.filter_by(
                professional_id=service_request.professional_id,
                service_id=service_request.service_id,
            ).first()

            refund_amount = (
                professional_service.custom_price
                if professional_service and professional_service.custom_price
                else payment.amount
            )

            # Update customer's wallet balance
            wallet = Wallet.query.filter_by(
                customer_id=service_request.customer_id
            ).first()
            if wallet:
                wallet.balance += refund_amount
            else:
                # Create wallet if it doesn't exist
                wallet = Wallet(
                    customer_id=service_request.customer_id, balance=refund_amount
                )
                db.session.add(wallet)

        db.session.commit()
        flash(
            "Service has been successfully cancelled and payment refunded.", "success"
        )
    else:
        flash("Service cannot be cancelled at this stage.", "warning")

    return redirect(url_for("customer_dashboard"))


@app.route("/close_service_professional", methods=["POST"])
def close_service_professional():
    data = request.json
    request_id = data.get("requestId")
    customer_rating = data.get("customerRating")
    customer_remarks = data.get("customerRemark")

    service_request = Service_Request.query.get(request_id)
    professional_id = session["professional_id"]

    if service_request and service_request.professional_id == professional_id:
        # Update the service status to 'closed'
        service_request.service_status = "closed"
        service_request.customer_rating = customer_rating  # Save the customer rating
        service_request.customer_remarks = customer_remarks  # Save the remarks
        service_request.date_of_completion = (
            datetime.utcnow()
        )  # Set the completion date

        # Commit the changes to the database
        db.session.commit()

        # Flash a success message and return the dashboard
        flash("Service request closed and rated successfully.", "success")
        return redirect(url_for("professional_dashboard"))

    return jsonify({"message": "An error occurred. Please try again."}), 400


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").strip()  # Remove any extra spaces
        phone = request.form.get("phone_no").strip()  # Remove extra spaces

        # Check if the phone number contains only digits
        if not phone.isdigit():
            flash("Phone number should contain only digits.", "danger")
            return redirect(url_for("forgot_password"))

        # Convert phone number to integer
        phone = int(phone)

        # Fetch user to verify email and phone number
        user = Customer.query.filter_by(email=email).first()
        user1 = Service_Professional.query.filter_by(email=email).first()

        if user and user.phone_no == phone:  # Compare phone numbers
            return redirect(url_for("reset_password", user_id=user.id))

        if user1 and user1.phone_no == phone:  # Compare phone numbers
            return redirect(url_for("reset_password", user_id=user1.id))

        flash("Invalid email or phone number.", "danger")
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


@app.route("/reset_password/<int:user_id>", methods=["GET", "POST"])
def reset_password(user_id):
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("reset_password", user_id=user_id))

        # Hash and update the new password
        user = Customer.query.get(user_id)
        if user:
            user.password = new_password
            db.session.commit()  # Assuming you have a session to commit the change
            flash("Password has been updated successfully!", "success")
            return redirect(url_for("user_login"))

        user1 = Service_Professional.query.get(user_id)
        if user1:
            user1.password = new_password
            db.session.commit()  # Assuming you have a session to commit the change
            flash("Password has been updated successfully!", "success")
            return redirect(url_for("user_login"))

    return render_template("reset_password.html", user_id=user_id)


# =============================================== Function Def =============================================================


def fetch_customer_ratings():
    ratings_count = {
        "1 Star": 0,
        "2 Stars": 0,
        "3 Stars": 0,
        "4 Stars": 0,
        "5 Stars": 0,
    }

    # Fetch service requests with ratings
    service_requests = Service_Request.query.with_entities(Service_Request.rating).all()

    for request in service_requests:
        rating = request.rating
        if rating is not None and 1 <= rating <= 5:
            ratings_count[f"{rating} Star" if rating == 1 else f"{rating} Stars"] += 1

    return {
        "labels": list(ratings_count.keys()),
        "data": list(ratings_count.values()),
    }


def fetch_service_request_summary():
    # Updated status categories with initial counts
    status_count = {
        "accepted": 0,
        "Closed": 0,  # Adding Closed
        "Rejected": 0,  # Adding Rejected
    }

    # Fetch the service_status values from the database
    service_requests = Service_Request.query.with_entities(
        Service_Request.service_status
    ).all()

    for request in service_requests:
        status = (
            request.service_status.strip().capitalize()
        )  # Clean and standardize the status
        if status in status_count:
            status_count[status] += 1
        # else:
        #     print(f"Unknown status encountered: {status}")  # Log for debugging

    return {
        "labels": list(status_count.keys()),
        "data": list(status_count.values()),
    }


def save_customer_pic(file):
    # Get the filename and ensure it's secure
    filename = secure_filename(file.filename)

    # Get the full path where the file will be saved
    upload_folder = current_app.config["CUSTOMER_PIC_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    # Ensure that the customer_pic directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the file
    file.save(file_path)

    return filename  # Return just the filename for storing in the database


def save_professional_pic(file):
    # Get the filename and ensure it's secure
    filename = secure_filename(file.filename)

    # Get the full path where the file will be saved
    upload_folder = current_app.config["PROFESSIONAL_PIC_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    # Ensure that the professional_pic directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the file
    file.save(file_path)

    return filename  # Return just the filename for storing in the database


def save_document(file):
    # Get the filename and ensure it's secure
    filename = secure_filename(file.filename)

    # Get the full path where the file will be saved
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    # Ensure that the uploads directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the file
    file.save(file_path)

    return filename  # Return just the filename for storing in the database


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


def save_service_picture(file):
    # Get the filename and ensure it's secure
    filename = secure_filename(file.filename)

    # Get the full path where the file will be saved
    upload_folder = current_app.config["SERVICE_PIC_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    # Ensure that the professional_pic directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the file
    file.save(file_path)

    return filename  # Return just the filename for storing in the database


def update_professional_rating(professional_id):
    # Count the number of completed service requests for the professional
    completed_requests_count = (
        db.session.query(Service_Request)
        .filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status == "closed",
            Service_Request.rating.isnot(
                None
            ),  # Only consider requests with customer ratings
        )
        .count()
    )

    # Calculate the average rating only if there are at least 7 completed service requests
    if completed_requests_count >= 7:
        average = (
            db.session.query(func.avg(Service_Request.rating))
            .filter(
                Service_Request.professional_id == professional_id,
                Service_Request.service_status == "closed",
                Service_Request.rating.isnot(
                    None
                ),  # Only consider requests with customer ratings
            )
            .scalar()
        )
        average = round(average, 1) if average is not None else 0.0
        # Update the professional's average rating in the database
        professional = Service_Professional.query.get(professional_id)
        if professional:
            professional.average_rating = average
            db.session.commit()

    else:
        # If less than 7 service requests, set the average rating to None
        professional = Service_Professional.query.get(professional_id)
        if professional:
            professional.average_rating = None
            db.session.commit()

    return professional.average_rating  # Return the updated average rating


def update_customer_rating(customer_id):
    # Count the number of completed service requests for the customer
    completed_requests_count = (
        db.session.query(Service_Request)
        .filter(
            Service_Request.customer_id == customer_id,
            Service_Request.service_status == "closed",
            Service_Request.customer_rating.isnot(
                None
            ),  # Only consider requests with professional ratings
        )
        .count()
    )

    # Calculate the average rating only if there are at least 7 completed service requests
    if completed_requests_count >= 7:
        average = (
            db.session.query(func.avg(Service_Request.customer_rating))
            .filter(
                Service_Request.customer_id == customer_id,
                Service_Request.service_status == "closed",
                Service_Request.customer_rating.isnot(
                    None
                ),  # Only consider requests with professional ratings
            )
            .scalar()
        )
        average = round(average, 1) if average is not None else 0.0
        # Update the customer's average rating in the database
        customer = Customer.query.get(customer_id)
        if customer:
            customer.average_rating = average
            db.session.commit()

    else:
        # If less than 7 service requests, set the average rating to None
        customer = Customer.query.get(customer_id)
        if customer:
            customer.average_rating = None
            db.session.commit()

    return customer.average_rating  # Return the updated average rating
