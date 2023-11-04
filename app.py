from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI_ENV = os.getenv("MONGO_URI_ENV")

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = str(MONGO_URI_ENV)
mongo = PyMongo(app)


# Hacer las rutas para CRUD a la base de datos
@app.route("/", methods=["GET"])
def index():
    return {
        "message": "API list of companies",
        "Routes": [
            {
                "route": "/companies",
                "method": "GET",
                "result": "List all companies",
            },
            {
                "route": "/company/<code>",
                "method": "GET",
                "result": "See company by code",
            },
            {
                "route": "/company/<code>",
                "method": "DELETE",
                "result": "Delete company by code",
            },
            {
                "route": "/company/<code>",
                "method": "PUT",
                "result": "Update company by code",
            },
            {
                "route": "/company",
                "method": "POST",
                "result": "New company",
                "format_body": {
                    "code": "String codigo",
                    "name": "String name",
                    "website": "String website",
                    "email": "String email",
                    "te": "String te",
                    "link_origin": "String link with origin",
                    "country": "String pais",
                    "details": "String details",
                },
            },
        ],
    }

    # routes CRUD companies


@app.route("/companies", methods=["GET"])
def get_companies():
    result = mongo.db.companies.find()
    response = json_util.dumps(result)
    response_json = Response(response, mimetype="application/json").json
    response_message = jsonify(
        {
            "message": "Listing all companies successfully",
            "services": response_json,
        }
    )
    response_message.status_code = 200
    return response_message


@app.route("/company/<code>", methods=["GET"])
def get_company(code):
    result = mongo.db.companies.find_one({"code": code})
    if result is not None:
        response = json_util.dumps(result)
        response_json = Response(response, mimetype="application/json").json
        response_ok = jsonify(
            {
                "message": "Service found successfully",
                "_id": response_json["_id"],
                "code": response_json["code"],
                "name": response_json["name"],
                "website": response_json["website"],
                "email": response_json["email"],
                "te": response_json["te"],
                "link_origin": response_json["link_origin"],
                "country": response_json["country"],
                "details": response_json["details"],
            }
        )
        response_ok.status_code = 200
        return response_ok
    else:
        return not_found()


@app.route("/company/<code>", methods=["DELETE"])
def company_delete(code):
    result = mongo.db.companies.delete_one({"code": code})
    if result.deleted_count == 1:
        return {
            "message": "Company was deleted successfully",
            "code": code,
        }
    else:
        return not_found()


@app.route("/company/<code>", methods=["PUT"])
def update_company(code):
    name, website, email, te, link_origin, country, details = request.json.values()
    if name and email:
        result = mongo.db.companies.find_one_and_update(
            {"code": code},
            {
                "$set": {
                    "name": name,
                    "website": website,
                    "email": email,
                    "te": te,
                    "link_origin": link_origin,
                    "country": country,
                    "details": details,
                }
            },
        )
        if result is not None:
            response = json_util.dumps(result)
            response_json = Response(response, mimetype="application/json").json
            response_message = {
                "message": "service updated successfully",
                "_id": response_json["_id"],
                "code": response_json["code"],
                "service_new": {
                    "name": name,
                    "website": website,
                    "email": email,
                    "te": te,
                    "link_origin": link_origin,
                    "country": country,
                    "details": details,
                },
                "service_old": {
                    "name": response_json["name"],
                    "website": response_json["website"],
                    "email": response_json["email"],
                    "te": response_json["te"],
                    "link_origin": response_json["link_origin"],
                    "country": response_json["country"],
                    "details": response_json["details"],
                },
            }
            return response_message
        else:
            return not_found()


@app.route("/company", methods=["POST"])
def create_company():
    (
        code,
        name,
        website,
        email,
        te,
        link_origin,
        country,
        details,
    ) = request.json.values()
    # Consulto si ya existe una company con ese code
    result_get = get_company(code)
    if result_get.status_code != 404:
        error = error_create("This company " + code + " already exists")
        error_response = error.json
        return error_response

    # Si la company con ese code no existe se crea el company
    if code and name and email:
        result = mongo.db.companies.insert_one(
            {
                "code": code,
                "name": name,
                "website": website,
                "email": email,
                "te": te,
                "link_origin": link_origin,
                "country": country,
                "details": details,
            }
        )
        return {
            "message": "Created company successfully",
            "_id": str(result.inserted_id),
            "code": code,
            "name": name,
            "website": website,
            "email": email,
            "te": te,
            "link_origin": link_origin,
            "country": country,
            "details": details,
        }
    else:
        return error_create("Invalid Data")


# cuando ocurre un error va a ser manejado con estas funciones
@app.errorhandler(404)
def not_found(error=404):
    response = jsonify(
        {
            "message": "Resource not found " + str(error),
            "status": 404,
        }
    )
    response.status_code = 404
    return response


@app.errorhandler(400)
def error_create(message, error=400):
    response = jsonify(
        {
            "message": "Error creating resource in " + str(message) + " " + str(error),
            "status": 400,
        }
    )
    response.status_code = 400
    return response


@app.errorhandler(500)
def error_create(error=500):
    response = jsonify(
        {
            "message": "Internal server error " + str(error),
            "status": 500,
        }
    )
    response.status_code = error
    return response


if __name__ == "__main__":
    app.run()
