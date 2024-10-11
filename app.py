from flask import Flask
from backend.models import *  # Importing the db instance from models

# from backend.api_controller import api  # Importing the api controller (if necessary)

app = None  # initially None


def init_app():
    service_app = Flask(__name__)  # Flask app initialization
    service_app.debug = True  # Enable debug mode
    service_app.secret_key = "mynameistushar"
    service_app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///service.sqlite3"  # Database config
    )
    service_app.config["UPLOAD_FOLDER"] = "static/uploads/"  # File upload folder
    service_app.config["CUSTOMER_PIC_FOLDER"] = (
        "static/customer_pic/"  # File upload folder for customer pics
    )
    service_app.config["PROFESSIONAL_PIC_FOLDER"] = (
        "static/professional_pic/"  # File upload folder for customer pics
    )
    service_app.config["SERVICE_PIC_FOLDER"] = (
        "static/service_pics/"  # File upload folder for service pics
    )

    # Ensure the upload folder exists
    import os

    if not os.path.exists(service_app.config["UPLOAD_FOLDER"]):
        os.makedirs(service_app.config["UPLOAD_FOLDER"])
    if not os.path.exists(service_app.config["CUSTOMER_PIC_FOLDER"]):
        os.makedirs(service_app.config["CUSTOMER_PIC_FOLDER"])
    if not os.path.exists(service_app.config["PROFESSIONAL_PIC_FOLDER"]):
        os.makedirs(service_app.config["PROFESSIONAL_PIC_FOLDER"])
    # Ensure the service pics folder exists
    if not os.path.exists(service_app.config["SERVICE_PIC_FOLDER"]):
        os.makedirs(service_app.config["SERVICE_PIC_FOLDER"])

    service_app.app_context().push()  # Push the app context for use in other modules
    db.init_app(service_app)  # Initialize the db object
    # api.init_app(service_app)  # Initialize API if needed

    print("Service application started....")
    return service_app


app = init_app()

# Import routes from controller after initializing app
from backend.controller import *  # Importing all the routes from controller.py

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables
    app.run()  # Run the application
