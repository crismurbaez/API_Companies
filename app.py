from flask import Flask, request, jsonify, Response, abort
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

if not MONGO_URI_ENV:
    raise ValueError("No MONGO_URI_ENV found in environment variables")
app.config["MONGO_URI"] = MONGO_URI_ENV

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
                    "code": "Integer numeric code",
                    "name": "String name",
                    "website": "String website",
                    "email": "String email",
                    "te": "String te",
                    "link_origin": "String link with origin",
                    "country": "String pais",
                    "details": "String details",
                },
            },
            {
                "route": "/error",
                "method": "GET",
                "result": "List all errors",
            },
            {"route": "/error", "method": "POST", "result": "New error", "body": "any"},
        ],
    }

    # routes CRUD companies


@app.route("/companies", methods=["GET"])
def get_companies():
    result = mongo.db.companies.find().sort("code", 1)
    companies = []

    if result is None:
        abort(404, description="No companies were found in the database")
    
    for doc in result:
        doc["_id"] = str(doc["_id"])
        companies.append(doc)
        
    return jsonify({
        "message": "Listing all companies successfully",
        "services": companies}), 200

@app.route("/company/<int:code>", methods=["GET"])
def get_company(code):
    result = mongo.db.companies.find_one({"code": code})
    if result is None:
        abort(404, description=f"The company with code {code} does not exist")

    # Convertimos el ID a una cadena de texto normal
    result["_id"] = str(result["_id"])

    # Devolvemos el objeto
    return jsonify({
            "message": "Service found successfully",
            "company": result}), 200

@app.route("/company/<int:code>", methods=["DELETE"])
def company_delete(code):
    result = mongo.db.companies.delete_one({"code": code})
    if result is None:
        abort(404, description=f"The company with code {code} does not exist")
    
    if result.deleted_count == 1:
        response_ok = jsonify(
            {
                "message": "Company was deleted successfully",
                "code": code,
            }
        )
        response_ok.status_code = 200
        return response_ok

@app.route("/company/<int:code>", methods=["PUT"])
def update_company(code):
    data = request.json
    name = data.get("name")
    website = data.get("website")
    email = data.get("email")
    te = data.get("te")
    link_origin = data.get("link_origin")
    country = data.get("country")
    details = data.get("details")

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
        if result is None:
            abort(404, description=f"The company with code {code} does not exist")

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
        
        return jsonify(response_message), 200


@app.route("/company", methods=["POST"])
def create_company():
    data = request.json
    code = int(data.get("code"))
    name = data.get("name")
    website = data.get("website")
    email = data.get("email")
    te = data.get("te")
    link_origin = data.get("link_origin")
    country = data.get("country")
    details = data.get("details")
    # Consulto si ya existe una company con ese code
    result_get = mongo.db.companies.find_one({"code": code})

    if result_get is not None:
        abort(400, description=f"The company with code {code} already exists")

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
        response_message = jsonify({
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
        })
        response_message.status_code = 200
        return response_message

    else:
        abort(400, description="Invalid Data: name and email are required")


# guarda los errores en los envíos de emails
@app.route("/error", methods=["POST"])
def create_error():
    error = request.json
    # print(error)
    result = mongo.db.error.insert_one(error)
    response = json_util.dumps(result)
    response_json = Response(response, mimetype="application/json").json
    response_message = jsonify(
        {
            "message": response_json,
        }
    )
    return response_message


@app.route("/error", methods=["GET"])
def get_error():
    result = mongo.db.error.find()
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


# cuando ocurre un error es manejado con estas funciones
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)

def error_handler(error):
    if error.code == 400:
        response = jsonify(
            {
                "message": "Error creating resource in " + str(error.description) + " " + str(error.code),
                "status": 400,
            }
        )
        response.status_code = 400
        return response

    elif error.code == 404:
        response = jsonify(
            {
                "message": "Resource not found " + str(error.description),
                "status": 404,
            }
        )
        response.status_code = 404
        return response

    elif error.code == 500:
        response = jsonify(
            {
                "message": "Internal server error " + str(error.description),
                "status": 500,
            }
        )
        response.status_code = 500
        return response

if __name__ == "__main__":
    app.run()
