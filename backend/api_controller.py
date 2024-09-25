from flask_restful import Api, Resource, reqparse
from .models import *

api = Api()


# # Define the parser for incoming JSON data
# parser = reqparse.RequestParser()
# parser.add_argument(
#     "service_id", type=int, required=True, help="Service ID cannot be blank"
# )
# parser.add_argument(
#     "customer_id", type=int, required=True, help="Customer ID cannot be blank"
# )
# parser.add_argument(
#     "professional_id", type=int, required=True, help="Professional ID cannot be blank"
# )


# class ServiceRequestResource(Resource):
#     def get(self, request_id):
#         service_request = Service_Request.query.get(request_id)
#         if service_request:
#             return {
#                 "id": service_request.id,
#                 "service_id": service_request.service_id,
#                 "customer_id": service_request.customer_id,
#                 "professional_id": service_request.professional_id,
#                 "status": service_request.service_status,
#             }, 200
#         return {"message": "Service request not found"}, 404

#     def post(self):
#         args = parser.parse_args()
#         new_request = Service_Request(
#             service_id=args["service_id"],
#             customer_id=args["customer_id"],
#             professional_id=args["professional_id"],
#         )
#         db.session.add(new_request)
#         db.session.commit()
#         return {"message": "Service request created successfully"}, 201

#     def delete(self, request_id):
#         service_request = Service_Request.query.get(request_id)
#         if service_request:
#             db.session.delete(service_request)
#             db.session.commit()
#             return {"message": "Service request deleted"}, 200
#         return {"message": "Service request not found"}, 404


# api.add_resource(
#     ServiceRequestResource,
#     "/api/service_request/<int:request_id>",
#     "/api/service_request",
# )
