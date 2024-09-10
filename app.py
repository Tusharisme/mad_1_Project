from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

db = SQLAlchemy(app)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)


class Service_Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    service_type = db.Column(db.String, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    verified_status = db.Column(db.String, nullable=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)


class Service_Request(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    professional_id = db.Column(
        db.Integer, db.ForeignKey("service_professional.id"), nullable=False
    )

    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(
        db.String, nullable=False
    )  # e.g., 'requested', 'assigned', 'closed'
    remarks = db.Column(db.String)

    service = db.relationship(
        "Service", backref=db.backref("service_requests", lazy=True)
    )
    customer = db.relationship(
        "Customer", backref=db.backref("service_requests", lazy=True)
    )
    professional = db.relationship(
        "Service_Professional", backref=db.backref("service_requests", lazy=True)
    )


# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
