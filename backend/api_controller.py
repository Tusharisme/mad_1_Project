# from flask_restful import Api, Resource, reqparse
# from .models import *

# api = Api()


# class ServiceResource(Resource):
#     def get(self, service_id=None):
#         if service_id:
#             service = Service.query.get(service_id)
#             if not service:
#                 return {"message": "Service not found"}, 404
#             return {
#                 "id": service.id,
#                 "name": service.name,
#                 "base_price": service.base_price,
#                 "description": service.description,
#             }
#         else:
#             services = Service.query.all()
#             return [
#                 {
#                     "id": s.id,
#                     "name": s.name,
#                     "base_price": s.base_price,
#                     "description": s.description,
#                 }
#                 for s in services
#             ], 200

#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument("name", required=True)
#         parser.add_argument("base_price", required=True, type=float)
#         parser.add_argument("description", required=False)
#         args = parser.parse_args()

#         new_service = Service(
#             name=args["name"],
#             base_price=args["base_price"],
#             description=args["description"],
#         )
#         db.session.add(new_service)
#         db.session.commit()
#         return {"message": "Service created successfully"}, 201

#     def put(self, service_id):
#         service = Service.query.get(service_id)
#         if not service:
#             return {"message": "Service not found"}, 404

#         parser = reqparse.RequestParser()
#         parser.add_argument("name", required=False)
#         parser.add_argument("base_price", required=False, type=float)
#         parser.add_argument("description", required=False)
#         args = parser.parse_args()

#         if args["name"]:
#             service.name = args["name"]
#         if args["base_price"]:
#             service.base_price = args["base_price"]
#         if args["description"]:
#             service.description = args["description"]

#         db.session.commit()
#         return {"message": "Service updated successfully"}, 200

#     def delete(self, service_id):
#         service = Service.query.get(service_id)
#         if not service:
#             return {"message": "Service not found"}, 404
#         db.session.delete(service)
#         db.session.commit()
#         return {"message": "Service deleted successfully"}, 200


# class ProfessionalResource(Resource):
#     def get(self, professional_id=None):
#         if professional_id:
#             professional = Service_Professional.query.get(professional_id)
#             if not professional:
#                 return {"message": "Professional not found"}, 404
#             return {
#                 "id": professional.id,
#                 "name": professional.name,
#                 "experience": professional.experience,
#                 "service_type": professional.service_type,
#                 "address": professional.address,
#                 "pin_code": professional.pin_code,
#                 "verified_status": professional.verified_status,
#             }
#         else:
#             professionals = Service_Professional.query.all()
#             return [
#                 {
#                     "id": p.id,
#                     "name": p.name,
#                     "experience": p.experience,
#                     "service_type": p.service_type,
#                 }
#                 for p in professionals
#             ], 200

#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument("name", required=True)
#         parser.add_argument("experience", required=True, type=int)
#         parser.add_argument("service_type", required=True)
#         parser.add_argument("address", required=True)
#         parser.add_argument("pin_code", required=True)
#         parser.add_argument("verified_status", required=False, type=bool)
#         args = parser.parse_args()

#         new_professional = Service_Professional(
#             name=args["name"],
#             experience=args["experience"],
#             service_type=args["service_type"],
#             address=args["address"],
#             pin_code=args["pin_code"],
#             verified_status=args.get("verified_status", False),
#         )
#         db.session.add(new_professional)
#         db.session.commit()
#         return {"message": "Professional created successfully"}, 201

#     def put(self, professional_id):
#         professional = Service_Professional.query.get(professional_id)
#         if not professional:
#             return {"message": "Professional not found"}, 404

#         parser = reqparse.RequestParser()
#         parser.add_argument("name", required=False)
#         parser.add_argument("experience", required=False, type=int)
#         parser.add_argument("service_type", required=False)
#         parser.add_argument("address", required=False)
#         parser.add_argument("pin_code", required=False)
#         parser.add_argument("verified_status", required=False, type=bool)
#         args = parser.parse_args()

#         if args["name"]:
#             professional.name = args["name"]
#         if args["experience"]:
#             professional.experience = args["experience"]
#         if args["service_type"]:
#             professional.service_type = args["service_type"]
#         if args["address"]:
#             professional.address = args["address"]
#         if args["pin_code"]:
#             professional.pin_code = args["pin_code"]
#         if args["verified_status"] is not None:
#             professional.verified_status = args["verified_status"]

#         db.session.commit()
#         return {"message": "Professional updated successfully"}, 200

#     def delete(self, professional_id):
#         professional = Service_Professional.query.get(professional_id)
#         if not professional:
#             return {"message": "Professional not found"}, 404
#         db.session.delete(professional)
#         db.session.commit()
#         return {"message": "Professional deleted successfully"}, 200


# from flask_restful import Api

# # from backend.resources import ServiceResource, ProfessionalResource

# # api = Api(app)
# api.add_resource(ServiceResource, "/api/services", "/api/services/<int:service_id>")
# api.add_resource(
#     ProfessionalResource,
#     "/api/professionals",
#     "/api/professionals/<int:professional_id>",
# )
