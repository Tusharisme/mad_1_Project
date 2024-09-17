# from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.String, nullable=False)
    role = db.Column(
        db.Integer, nullable=False, default=1
    )  # 0 for admin, 1 for customer


class Service_Professional(db.Model):
    __tablename__ = "service_professional"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    service_type = db.Column(
        db.String, nullable=False
    )  # nullable true done for some reason
    experience = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.String, nullable=False)
    verified_status = db.Column(db.String, nullable=True)
    document = db.Column(db.String, nullable=True)  # Column to store document path

    # Relationship with ProfessionalService (custom services per professional)
    custom_services = db.relationship(
        "ProfessionalService", backref="professional", lazy=True
    )


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    base_price = db.Column(
        db.Integer, nullable=False
    )  # Changed 'price' to 'base_price'
    time_required = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=False)

    # Relationship with ProfessionalService (custom services per professional)
    custom_services = db.relationship(
        "ProfessionalService", backref="service", lazy=True
    )


class ProfessionalService(db.Model):
    __tablename__ = "professional_service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    professional_id = db.Column(
        db.Integer, db.ForeignKey("service_professional.id"), nullable=False
    )
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    custom_price = db.Column(db.Float, nullable=True)
    custom_description = db.Column(db.String, nullable=True)

    # Optional: Add any additional fields to track custom services
    additional_info = db.Column(db.String, nullable=True)


class Service_Request(db.Model):
    __tablename__ = "service_request"
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


# old model kept for refernece

# Junction table for the many-to-many relationship between professionals and services
# professional_service_association = db.Table(
#     "professional_service_association",
#     db.Column("professional_id", db.Integer, db.ForeignKey("service_professional.id")),
#     db.Column("service_id", db.Integer, db.ForeignKey("service.id")),
# )


# class Customer(db.Model):
#     __tablename__ = "customer"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     name = db.Column(db.String, nullable=False)
#     email = db.Column(db.String, unique=True, nullable=False)  # Added unique constraint
#     address = db.Column(db.String, nullable=False)
#     pin_code = db.Column(db.String, nullable=False)
#     role = db.Column(
#         db.Integer, nullable=False, default=1
#     )  # 0 for role and 1 for customer


# class Service_Professional(db.Model):
#     __tablename__ = "service_professional"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     name = db.Column(db.String, nullable=False)
#     service_type = db.Column(
#         db.String, nullable=False
#     )  # nullable true done for some reason
#     experience = db.Column(db.Integer, nullable=False)
#     email = db.Column(db.String, unique=True, nullable=False)
#     address = db.Column(db.String, nullable=False)
#     pin_code = db.Column(db.String, nullable=False)
#     verified_status = db.Column(db.String, nullable=True)
#     document = db.Column(db.String, nullable=True)  # Column to store document path

#     # Many-to-many relationship with services
#     services = db.relationship(
#         "Service",
#         secondary=professional_service_association,
#         backref=db.backref("professionals", lazy=True),
#     )


# class Service(db.Model):
#     __tablename__ = "service"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String, nullable=False)
#     price = db.Column(db.Integer, nullable=False)
#     time_required = db.Column(db.Integer, nullable=True)  # True for now
#     description = db.Column(db.String, nullable=False)


# class Service_Request(db.Model):
#     __tablename__ = "service_request"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
#     customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
#     professional_id = db.Column(
#         db.Integer, db.ForeignKey("service_professional.id"), nullable=False
#     )

#     date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     date_of_completion = db.Column(db.DateTime)
#     service_status = db.Column(
#         db.String, nullable=False
#     )  # e.g., 'requested', 'assigned', 'closed'
#     remarks = db.Column(db.String)

#     service = db.relationship(
#         "Service", backref=db.backref("service_requests", lazy=True)
#     )
#     customer = db.relationship(
#         "Customer", backref=db.backref("service_requests", lazy=True)
#     )
#     professional = db.relationship(
#         "Service_Professional", backref=db.backref("service_requests", lazy=True)
#     )
