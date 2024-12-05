from flask_restx import Namespace, Resource, fields
from flask import request
from .taxonomy_service import Taxonomy
from .auth_service import Auth


namespace_taxonomie = Namespace("taxonomie", description="Taxonnomie operations")


taxonomie_model_add = namespace_taxonomie.model(
    "Taxonomie Add",
    {
        "domain": fields.String(required=True, description="Domain of the taxonomy"),
        "description": fields.String(
            required=True, description="Description of the taxonomy"
        ),
    },
)


taxonomie_model_response = namespace_taxonomie.model(
    "Taxonomie Full",
    {
        "id": fields.Integer(
            required=True, description="The unique identifier of the taxonomy"
        ),
        "user_id": fields.Integer(
            required=True, description="The ID of the user who created this taxonomy"
        ),
        "domain": fields.String(
            required=True, description="The domain of the taxonomy"
        ),
        "description": fields.String(
            required=True, description="A description of the taxonomy"
        ),
        "data": fields.Raw(description="Additional data in JSON format"),
        "created_at": fields.String(
            description="The timestamp when the taxonomy was created"
        ),
        "last_update": fields.String(
            description="The timestamp of the last update to the taxonomy"
        ),
    },
)


taxonomie_delete_model = namespace_taxonomie.model(
    "Taxonomie Delete",
    {
        "id": fields.Integer(
            required=True, description="The unique identifier of the taxonomy"
        ),
        "password": fields.String(required=True, description="A password"),
    },
)


sub_subcategory_data_model = namespace_taxonomie.model(
    "SubSubCategory",
    {"name": fields.String(required=True, description="Name of the sub-subcategory")},
)


subcategory_data_model = namespace_taxonomie.model(
    "SubCategory",
    {
        "name": fields.String(required=True, description="Name of the subcategory"),
        "sub_subcategories": fields.List(
            fields.Nested(sub_subcategory_data_model),
            description="Optional list of sub-subcategories",
        ),
    },
)


category_data_model = namespace_taxonomie.model(
    "Category",
    {
        "name": fields.String(required=True, description="Name of the category"),
        "subcategories": fields.List(
            fields.Nested(subcategory_data_model),
            description="Optional list of subcategories",
        ),
    },
)


taxonomy_data_model_full = namespace_taxonomie.model(
    "Taxonomy Generate",
    {
        "api_key": fields.String(required=True, description="Api-Key for gpt-4o-mini"),
        "id": fields.String(
            required=True, description="The unique identifier of the taxonomy"
        ),
        "categories": fields.List(
            fields.Nested(category_data_model),
            description="Optional list of categories",
        ),
    },
)


@namespace_taxonomie.route("/add")
class AddTaxonomie(Resource):
    @namespace_taxonomie.doc(security="jasonWebToken")
    @namespace_taxonomie.expect(taxonomie_model_add, validate=True)
    @namespace_taxonomie.response(201, "Taxonomie successfully added")
    @namespace_taxonomie.response(409, "Taxonomie could not be added")
    @namespace_taxonomie.response(403, "Access Denied")
    @namespace_taxonomie.response(400, "BAD REQUEST")
    @Auth.token_required
    def post(self, current_user):
        """
        Add a new taxonomy.

        This method allows the user to add a new taxonomy by providing a domain
        and a description. It associates the taxonomy with the currently authenticated user.
        """
        data = request.get_json()
        domain = data["domain"]
        desciption = data["description"]
        if Taxonomy.add_taxonomy(
            domain=domain, description=desciption, current_user=current_user
        ):
            return f"{domain} successfully added", 201
        else:
            return f"{domain} could not be added", 400


@namespace_taxonomie.route("/delete")
class DeleteTaxonomie(Resource):
    @namespace_taxonomie.doc(security="jasonWebToken")
    @namespace_taxonomie.expect(taxonomie_delete_model, validate=True)
    @namespace_taxonomie.response(200, "Taxonomy successfully deleted")
    @namespace_taxonomie.response(404, "Taxonomy not found or wrong password")
    @namespace_taxonomie.response(403, "Access Denied")
    @namespace_taxonomie.response(400, "BAD REQUEST")
    @Auth.token_required
    def delete(self, current_user):
        """
        Delete a taxonomy.

        This method deletes a specified taxonomy after verifying the user's identity with a password.
        """
        data = request.get_json()
        id = data["id"]
        password = data["password"]
        if Taxonomy.delete_taxonomie(id=id, username=current_user, password=password):
            return "Taxonomy successfully deleted", 200
        else:
            return "Taxonomy not found or wrong password", 404


@namespace_taxonomie.route("/save")
class SaveTaxonomie(Resource):
    @namespace_taxonomie.doc(security="jasonWebToken")
    @namespace_taxonomie.response(201, "Taxonomy successfully saved.")
    @namespace_taxonomie.expect(taxonomy_data_model_full, validate=True)
    @namespace_taxonomie.response(404, "Taxonomy not found")
    @namespace_taxonomie.response(403, "Access Denied")
    @namespace_taxonomie.response(400, "BAD REQUEST")
    @Auth.token_required
    def put(self, current_user):
        """
        Save or update a taxonomy.

        This method saves or updates the given taxonomy data if it belongs to the specified user.
        """
        data = request.get_json()
        if Taxonomy.save_taxonomie(data=data, username=current_user):
            return "Taxonomy successfully saved", 201
        else:
            return "Taxonomy not found", 404


@namespace_taxonomie.route("/get")
class GetTaxonomie(Resource):
    @namespace_taxonomie.doc(security="jasonWebToken")
    @namespace_taxonomie.param("taxonomie_id", "The taxonomy identifier")
    @namespace_taxonomie.response(200, "Success", taxonomie_model_response)
    @namespace_taxonomie.response(404, "Taxonomy not found")
    @namespace_taxonomie.response(403, "Access Denied")
    @namespace_taxonomie.response(400, "BAD REQUEST")
    @Auth.token_required
    def get(self, current_user):
        """
        Retrieve a taxonomy.

        This method retrieves a taxonomy by its ID or all taxonomies for the authenticated user
        if no ID is provided.
        """
        taxonomie_id = request.args.get("taxonomie_id")
        if taxonomie_id:
            try:
                taxonomie_id = int(taxonomie_id)
            except ValueError:
                return {
                    "errors": {"refresh_token": "'taxonomie_id' must be an integer"},
                    "message": "Input payload validation failed",
                }, 400
            response = Taxonomy.get_taxonomy(
                id=int(taxonomie_id), username=current_user
            )
            if response == None:
                return "Taxonomie not found.", 404
            else:
                return response, 200
        else:
            return Taxonomy.get_taxonomy(id=0, username=current_user)


@namespace_taxonomie.route("/generate")
class GenerateTaxonomie(Resource):
    @namespace_taxonomie.doc(security="jasonWebToken")
    @namespace_taxonomie.expect(taxonomy_data_model_full, validate=True)
    @namespace_taxonomie.response(200, "Success", taxonomy_data_model_full)
    @namespace_taxonomie.response(404, "Taxonomy not found or wrong API Key")
    @namespace_taxonomie.response(403, "Access Denied")
    @namespace_taxonomie.response(400, "BAD REQUEST")
    @Auth.token_required
    def post(self, current_user):
        """
        Generate a taxonomy.

        This method generates categories for a taxonomy using data provided by the user and GPT.
        """
        data = request.get_json()
        response = Taxonomy.generate_taxonomie(data=data, username=current_user)
        if response:
            return response, 200
        else:
            return "Taxonomy not found or wrong API Key", 404
