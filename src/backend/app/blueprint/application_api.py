import hmac
import secrets
import time
import uuid

from flask import Blueprint, request
from webargs import fields, validate
from webargs.flaskparser import parser

from model.Group import Group
from model.User import User
from model.GroupApplication import GroupApplication
from model.GroupComment import GroupComment
from shared import get_logger, db
from utility import MyValidator
from utility.ApiException import *
from utility.Auth import Auth
from utility.MyResponse import MyResponse

logger = get_logger(__name__)
application_api = Blueprint("application_api", __name__)


# webargs parser error handler
@parser.error_handler
def handle_error(error, req, schema, *, error_status_code, error_headers):
    raise ApiInvalidInputException(error.messages)


@application_api.route("/group/<group_uuid>/application", methods=["POST"])
def create_application(group_uuid):
    """Create an application to join the group
    ---
    tags:
      - application

    description: |
      ## Constrains
      * operator must not have possessed group or joined group
      * operator can have only one application for a group
      * application can only be created if system state is GROUPING
      * application can only be created if the group application_enabled=true
      * application can only be created if the group member count < system max member per group settings
    
    parameters:
      - name: group_uuid
        in: path
        required: true
        description: group uuid
        schema:
          type: string
          example: 16fc2db7-cac0-46c2-a0e3-2da6cec54abb

    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              comment:
                type: string
                description: application comment
                example: FBI OPEN DA DOOR!
                max: 4096

    responses:
      '200':
        description: query success
        content:
          application/json:
            schema:
              type: object
    """
    pass  # TODO


@application_api.route("/group/<group_uuid>/application", methods=["GET"])
def get_group_application_list(group_uuid):
    """Get list of group applications
    ---
    tags:
      - application

    description: |
      ## Constrains
      * operator must be group owner
      
    parameters:
      - name: group_uuid
        in: path
        required: true
        description: group uuid
        schema:
          type: string
          example: 16fc2db7-cac0-46c2-a0e3-2da6cec54abb

    responses:
      200:
        description: query success
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  uuid:
                    type: string
                    description: group application uuid
                    example: b86a6406-14ca-4459-80ea-c0190fc43bd3
                  applicant:
                    type: object
                    description: the user who created the group
                    properties:
                      uuid:
                        type: string
                        description: user uuid
                        example: b86a6406-14ca-4459-80ea-c0190fc43bd3
                      alias:
                        type: string
                        example: Ming Li
                      email:
                        type: string
                        example: Ming.Li@example.com
                  comment:
                    type: string
                    description: group application comment
                    example: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque a ultricies diam. Donec ultrices tortor non lobortis mattis. Mauris euismod tellus ipsum, et porta mi scelerisque ac.
                  creation_time:
                    type: integer
                    description: group creation time, unix timestamp
                    example: 1617189103
    """
    # TODO complete Leo
    args_query = parser.parse({
        "group_uuid": fields.Str(required=True, validate=MyValidator.Uuid())
    }, request, location="path")
    group_uuid: str = args_query["group_uuid"]
    group=Group.query.filter_by(uuid=uuid.UUID(group_uuid).bytes).first()
    if group is None:
        raise ApiResourceNotFoundException("No such group!")
    token_info = Auth.get_payload(request)
    uuid_in_token = token_info['uuid']
    if uuid_in_token!=str(uuid.UUID(bytes=group.owner_uuid)):
        raise ApiPermissionException("You are not the owner of this group!")
    application_list= GroupApplication.query.filter_by(group_uuid=uuid.UUID(group_uuid).bytes).all()
    response_list=[]
    for application in application_list:
        applicant = application.applicant
        response_list.append({"applicant":{"alias":applicant.alias, "email":applicant.email, "uuid":str(uuid.UUID(bytes=applicant.uuid))},
                              "comment":application.comment,"creation_time":application.creation_time,
                              "uuid":str(uuid.UUID(bytes=application.uuid))})
    return MyResponse(data=response_list, msg='query success').build()





@application_api.route("/user/<user_uuid>/application", methods=["GET"])
def get_user_application_list(user_uuid):
    """Get list of user's applications
    ---
    tags:
      - application

    description: |
       ## Constrains
      * operator must be himself
    parameters:
      - name: user_uuid
        in: path
        required: true
        description: user uuid
        schema:
          type: string
          example: 16fc2db7-cac0-46c2-a0e3-2da6cec54abb

    responses:
      200:
        description: query success
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  uuid:
                    type: string
                    description: application uuid
                    example: b86a6406-14ca-4459-80ea-c0190fc43bd3
                  group:
                    type: object
                    description: the user who created the group
                    properties:
                      uuid:
                        type: string
                        description: group uuid
                        example: b86a6406-14ca-4459-80ea-c0190fc43bd3
                      name:
                        type: string
                        example: Jaxzefalk
                      description:
                        type: string
                        example: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque a ultricies diam. Donec ultrices tortor non lobortis mattis. Mauris euismod tellus ipsum, et porta mi scelerisque ac.
                  comment:
                    type: string
                    description: group application comment
                    example: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque a ultricies diam. Donec ultrices tortor non lobortis mattis. Mauris euismod tellus ipsum, et porta mi scelerisque ac.
                  creation_time:
                    type: integer
                    description: group creation time, unix timestamp
                    example: 1617189103
    """
    # TODO complete Leo
    args_query = parser.parse({
        "user_uuid": fields.Str(required=True, validate=MyValidator.Uuid())
    }, request, location="path")
    user_uuid: str = args_query["user_uuid"]
    user=User.query.filter_by(uuid=uuid.UUID(user_uuid).bytes).first()
    if user is None:
        raise ApiResourceNotFoundException("No such user!")
    token_info = Auth.get_payload(request)
    uuid_in_token = token_info['uuid']
    if uuid_in_token != user_uuid:
        raise ApiPermissionException("You cannot view others' application!")
    application_list = GroupApplication.query.filter_by(applicant_uuid=uuid.UUID(user_uuid).bytes).all()
    response_list = []
    for application in application_list:
        applicant = application.applicant
        response_list.append({"applicant": {"alias": applicant.alias, "email": applicant.email,
                                            "uuid": str(uuid.UUID(bytes=applicant.uuid))},
                              "comment": application.comment, "creation_time": application.creation_time,
                              "uuid": str(uuid.UUID(bytes=application.uuid))})
    return MyResponse(data=response_list, msg='query success').build()



@application_api.route("/application/accepted", methods=["POST"])
def accept_application():
    """Accept the application
    ---
    tags:
      - application

    description: |
      ## Constrains
      * operator must be the group owner
      * application removed after the operation

    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              uuid:
                type: string
                description: application uuid
                example: 16fc2db7-cac0-46c2-a0e3-2da6cec54abb

    responses:
      '200':
        description: query success
        content:
          application/json:
            schema:
              type: object
    """
    pass  # TODO


@application_api.route("/application/rejected", methods=["POST"])
def reject_application():
    """Reject the application
    ---
    tags:
      - application

    description: |
      ## Constrains
      * operator must be the group owner
      * application removed after the operation

    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              uuid:
                type: string
                description: application uuid
                example: 16fc2db7-cac0-46c2-a0e3-2da6cec54abb

    responses:
      '200':
        description: query success
        content:
          application/json:
            schema:
              type: object
    """
    pass  # TODO