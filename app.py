import psycopg2
from flask import Flask, request, jsonify, make_response
from google.oauth2.credentials import Credentials

connection_string = "postgresql://keepinminddb_user:yrOWdaHiZ0NSbKj5kQ5ARzUtXDiTjWg5@dpg-cf1but94reb5o41og2s0-a.frankfurt-postgres.render.com:5432/keepinminddb"

connection = psycopg2.connect(connection_string)

cursor = connection.cursor()

app = Flask(__name__)

#socres:
@app.route("/scores", methods=["POST"])
def add_score():
    try:
        data = request.get_json()
        username = data["username"]
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

@app.route("/scores", methods=["GET"])
def get_scores():
    try:
        cursor.execute("SELECT * FROM scores")
        scores_list = cursor.fetchall()
        scores = []
        for score in scores_list:
            scores.append({
                "id": score[0],
                "username": score[1],
                "score": score[2]
            })
        return jsonify({"scores": scores}), 200, {'Content-Type': 'application/json'}
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/scores/<int:score_id>", methods=["GET"])
def get_score(score_id):
    try:
        cursor.execute("SELECT * FROM scores WHERE id = %s", (score_id,))
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
@app.route("/accounts", methods=["POST"])
def add_account():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]

        sql = "INSERT INTO accounts (username, password) VALUES (%s, %s)"
        val = (username, password)
        cursor.execute(sql, val)
        connection.commit()

        return "Account added successfully"
    except KeyError:
        return make_response("Error: request data is missing required keys (username, password)", 400)
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/accounts", methods=["GET"])
def get_accounts():
    try:
        cursor.execute("SELECT * FROM accounts")
        accounts_list = cursor.fetchall()
        accounts = []
        for account in accounts_list:
            accounts.append({
                "id": account[0],
                "username": account[1],
            })
        return jsonify({"accounts": accounts}), 200, {'Content-Type': 'application/json'}
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    try:
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
        account_list = cursor.fetchone()
        account = {
                "id": account_list[0],
                "username": account_list[1],
        }
        if not account:
            return make_response("Error: Account not found", 404)
        return jsonify({"account": account}), 200, {'Content-Type': 'application/json'}
    except psycopg2.Error as e:
        return make_response("Error: {}".format(e), 500)


@app.route('/email', methods=['POST'])
def email():
    access_token = request.json.get('access_token')
    creds = Credentials.from_authorized_user_info(info=access_token)
    email = creds.id_token["email"]
    return jsonify(email=email)
