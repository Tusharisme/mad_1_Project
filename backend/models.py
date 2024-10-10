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
    phone_no = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=True)  # New column for gender (optional)
    profile_pic = db.Column(db.String, nullable=True)  # New column for profile picture (optional)
    role = db.Column(
        db.Integer, nullable=False, default=1
    )  # 0 for admin, 1 for customer
    average_rating = db.Column(db.Float, nullable=True)  # New column for average rating
    is_blocked = db.Column(
        db.Boolean, default=False
    )  # New column to track block status


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
    phone_no = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.String, nullable=False)
    verified_status = db.Column(db.String, nullable=True, default="Not verified yet")
    gender = db.Column(db.String, nullable=True)  # New column for gender (optional)
    profile_pic = db.Column(db.String, nullable=True)  # New column for profile picture (optional)
    average_rating = db.Column(db.Float, nullable=True)  # New column for average rating
    document = db.Column(db.String, nullable=True)  # Column to store document path
    block_status = db.Column(db.Boolean, default=False)  # Block/unblock status

    # Relationship with ProfessionalService (custom services per professional)
    custom_services = db.relationship(
        "ProfessionalService",
        back_populates="professional",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    base_price = db.Column(
        db.Integer, nullable=False
    )  # Changed 'price' to 'base_price'
    base_time_required = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=False)

    # Relationship with ProfessionalService (custom services per professional)
    # custom_services = db.relationship(
    #     "ProfessionalService", backref="service", lazy=True
    # )
    professional_services = db.relationship(
        "ProfessionalService", back_populates="service"
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
    custom_time_required = db.Column(
        db.String
    )  # New field for time required in minutes (or hours)
    # Optional: Add any additional fields to track custom services
    # additional_info = db.Column(db.String, nullable=True)

    # Use back_populates instead of backref, to avoid conflicts
    professional = db.relationship(
        "Service_Professional", back_populates="custom_services"
    )
    service = db.relationship("Service", back_populates="professional_services")


class Service_Request(db.Model):
    __tablename__ = "service_request"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    professional_id = db.Column(
        db.Integer, db.ForeignKey("service_professional.id"), nullable=False
    )

    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # date_of_request = db.Column(db.DateTime)  # Store only the date
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(
        db.String, nullable=False
    )  # e.g., 'requested', 'assigned', 'closed'
    remarks = db.Column(db.String, nullable=True)  # ratings given by customer
    rating = db.Column(db.Integer, nullable=True)  # Added this line for the rating
    customer_rating = db.Column(
        db.Integer, nullable=True
    )  # Rating given by professional
    customer_remarks = db.Column(
        db.String, nullable=True
    )  # Remarks from the professional
    # New fields for date and time
    requested_date = db.Column(db.Date)
    requested_time = db.Column(db.Time)

    service = db.relationship(
        "Service",
        backref=db.backref(
            "service_requests",
            lazy=True,
        ),
    )
    customer = db.relationship(
        "Customer", backref=db.backref("service_requests", lazy=True)
    )
    professional = db.relationship(
        "Service_Professional",
        backref=db.backref("service_requests", lazy=True, cascade="all, delete-orphan"),
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


#     # Relationship with ProfessionalService (custom services per professional)
#     custom_services = db.relationship(
#         "ProfessionalService", backref="professional", lazy=True
#     )


# class ProfessionalService(db.Model):
#     __tablename__ = "professional_service"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     professional_id = db.Column(
#         db.Integer, db.ForeignKey("service_professional.id"), nullable=False
#     )
#     service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
#     custom_price = db.Column(db.Float, nullable=True)
#     custom_description = db.Column(db.String, nullable=True)


#     # Optional: Add any additional fields to track custom services
#     additional_info = db.Column(db.String, nullable=True)
#     professional = db.relationship(
#         "Service_Professional", back_populates="custom_services"
#     )
#     service = db.relationship("Service", back_populates="professional_services")
