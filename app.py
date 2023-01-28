import psycopg2
from flask import Flask, request, jsonify, make_response
import requests

connection_string = "postgresql://keepinminddb_user:yrOWdaHiZ0NSbKj5kQ5ARzUtXDiTjWg5@dpg-cf1but94reb5o41og2s0-a.frankfurt-postgres.render.com:5432/keepinminddb"
connection = psycopg2.connect(connection_string)
cursor = connection.cursor()

app = Flask(__name__)

#socres:
@app.route("/scores", methods=["POST"])
def add_score():
    try:
        headers = {
        'Authorization': request.headers.get('Authorization')
        }
        
        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
        user_info = response.json()
        username = user_info['name']

        data = request.get_json()
        score = data["score"]

        sql = "INSERT INTO scores (username, score) VALUES (%s, %s)"
        val = (username, score)
        cursor.execute(sql, val)
        connection.commit()

        return "Score added successfully"
        
    except KeyError:
        return make_response("Error: request data is missing required keys (username, score)", 400)

    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/scores/<int:score_id>", methods=["GET"])
def get_score():
    try:
        headers = {
        'Authorization': request.headers.get('Authorization')
        }
        
        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
        user_info = response.json()
        username = user_info['name']

        cursor.execute("SELECT * FROM scores WHERE username = %s", (username))

        score_list = cursor.fetchone()
        score = {
                "id": score_list[0],
                "username": score_list[1],
                "score": score_list[2]
        }

        if not score:
            return make_response("Error: Score not found", 404)
        return jsonify({"score": score}), 200, {'Content-Type': 'application/json'}
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

#accounts:
@app.route("/google_login", methods=["POST"])
def google_login():
    try:
        headers = {
        'Authorization': request.headers.get('Authorization')
        }

        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
        user_info = response.json()

        username = user_info['name']
        email = user_info['email']
        given_name = user_info['given_name']
        family_name = user_info['family_name']

        sql = ("INSERT INTO accounts (username, email, given_name, family_name) VALUES (%s, %s, %s, %s)")
        val = (username, email, given_name, family_name)

        cursor.execute(sql,val)
        connection.commit()

        return jsonify({"message": "Account created successfully"})
    except KeyError as e:
        return jsonify({"error": f"Missing required key in request data: {e}"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error obtaining access token: {e}"}), 500
    except psycopg2.Error as e:
        return jsonify({"error": f"Error inserting data into database: {e}"}), 500

#Google API photos
@app.route('/photos', methods=['GET'])
def photos():
    url = "https://photoslibrary.googleapis.com/v1/mediaItems"

    headers = {
        'Authorization': request.headers.get('Authorization')
    }

    response = requests.request("GET", url, headers=headers)
    return  jsonify(response.json())
