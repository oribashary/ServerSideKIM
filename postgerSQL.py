import sqlalchemy
from flask import Flask, request, jsonify, make_response

connection_string = "postgres://keepinminddb_user:yrOWdaHiZ0NSbKj5kQ5ARzUtXDiTjWg5@dpg-cf1but94reb5o41og2s0-a.frankfurt-postgres.render.com/keepinminddb"
connection = sqlalchemy.connect(connection_string)

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

    except sqlalchemy.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/scores", methods=["GET"])
def get_scores():
    try:
        cursor.execute("SELECT * FROM scores")
        scores = cursor.fetchall()

        return jsonify(scores)
    except sqlalchemy.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/scores/<int:account_id>", methods=["GET"])
def get_score(account_id):
    try:
        cursor.execute("SELECT score FROM scores WHERE account_id = %s", (account_id,))
        score = cursor.fetchone()
        if not score:
            return make_response("Error: Score not found", 404)
        return jsonify(score)
    except sqlalchemy.Error as e:
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
    except sqlalchemy.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/accounts", methods=["GET"])
def get_accounts():
    try:
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()

        return jsonify(accounts)
    except sqlalchemy.Error as e:
        return make_response("Error: {}".format(e), 500)

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    try:
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
        account = cursor.fetchone()
        if not account:
            return make_response("Error: Account not found", 404)
        return jsonify(account)
    except sqlalchemy.Error as e:
        return make_response("Error: {}".format(e), 500)
