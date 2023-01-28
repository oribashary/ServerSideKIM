import psycopg2
from flask import Flask, request, jsonify, make_response
import requests
import json

GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v1/userinfo"
POSTGRESQL_CONNECTION_STRING = "postgresql://keepinminddb_user:yrOWdaHiZ0NSbKj5kQ5ARzUtXDiTjWg5@dpg-cf1but94reb5o41og2s0-a.frankfurt-postgres.render.com:5432/keepinminddb"

connection = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
cursor = connection.cursor()

app = Flask(__name__)

class UserInfo:
    def __init__(self, name, email, given_name, family_name):
        self.name = name
        self.email = email
        self.given_name = given_name
        self.family_name = family_name

def get_response():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return 'Authorization header not found', 401

    token = auth_header.split()[1]
    session = requests.Session()
    res = session.get(GOOGLE_USERINFO_ENDPOINT, headers={'Authorization': f"Bearer {token}"})

    if res.status_code != 200:
        return 'Invalid token', 401

    user_info = json.loads(res.text)
    return UserInfo(user_info['name'], user_info['email'], user_info['given_name'], user_info['family_name'])

#accounts:
@app.route("/google_login", methods=["POST"])
def google_login():
    try:
        user_info = get_response()

        cursor.execute("SELECT * FROM accounts WHERE email = %s", (user_info.email,))
        account = cursor.fetchone()

        if account:
            return jsonify({"message": "Welcome back"})

        cursor.execute("INSERT INTO accounts (username, email, given_name, family_name) VALUES (%s, %s, %s, %s)", (user_info.name, user_info.email, user_info.given_name, user_info.family_name))
        connection.commit()

        return jsonify({"message": "Account created successfully"})

    except KeyError as e:
        return jsonify({"error": f"Missing required key in request data: {e}"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error obtaining access token: {e}"}), 500
    except psycopg2.Error as e:
        return jsonify({"error": f"Error inserting data into database: {e}"}), 500


#socres:
@app.route("/scores", methods=["POST"])
def add_score():
    try:
        user_info = get_response()

        data = request.get_json()
        score = data["score"]

        sql = "INSERT INTO scores (username, score) VALUES (%s, %s)"
        val = (user_info.name, score)
        cursor.execute(sql, val)
        connection.commit()

        return "Score added successfully"
        
    except KeyError:
        return make_response("Error: request data is missing required keys (username, score)", 400)

    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/scores", methods=["GET"])
def get_scores():
    try:
        user_info = get_response()

        cursor.execute("SELECT * FROM scores WHERE username = %s", (user_info.name,))
        score_list = cursor.fetchall()

        if not score_list:
            return make_response("Error: score_list not found", 404)

        scores = []
        for score in score_list:
            score_obj = {
                "id": score[0],
                "username": score[1],
                "score": score[2]
            }
            scores.append(score_obj)

        return jsonify({"scores": scores}), 200, {'Content-Type': 'application/json'}
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

#Google API photos
@app.route('/photos', methods=['GET'])
def photos():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return 'Authorization header not found', 401

    token = auth_header.split()[1]

    url = "https://photoslibrary.googleapis.com/v1/mediaItems:search"

    payload = {
    "filters": {
        "contentFilter": {
            "includedContentCategories": [
                "BIRTHDAYS",
                "ANIMALS",
                "SELFIES",
                "PETS"
            ]
        },
        "mediaTypeFilter": {
            "contentTypes": [
                "PHOTO"
                ]
            }
        }
    }

    session = requests.Session()
    response = session.request("POST", url, headers={'Authorization': f"Bearer {token}"}, data=payload)
    
    if response.status_code != 200:
        return 'Error connecting to Google Photos API', response.status_code

    response_json = response.json()
    
    if 'mediaItems' not in response_json:
        return 'Error: mediaItems not found in response', response.status_code

    links = []
    for item in response_json['mediaItems']:
        links.append(item['productUrl'])
    return links
