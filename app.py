from flask import Flask, jsonify, request
from utils import generateUserId
from flask_mysqldb import MySQL
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
import mysql.connector

app = Flask(__name__)

app.config['secret_key'] = 'a_secret_key'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="sHj@6378#jw",
  database = 'crickbuzz'
)

cursor = mydb.cursor()

cursor.execute(
    'create table if not exists ADMIN ( \
        userId varchar(255) PRIMARY KEY,\
        name varchar(255) UNIQUE, \
        password varchar(255), \
        email varchar(255) \
    )'
)

cursor.execute(
    'create table if not exists MATCH ( \
        matchId INT AUTO_INCREMENT PRIMARY KEY,\
        team1 varchar(255), \
        team2 varchar(255), \
        date varchar(255),\
        venue varchar(255), \
        status varchar(255) \
    )'
)

cursor.execute(
    'create table if not exists SQUAD ( \
        playerId int PRIMARY KEY,\
        Team varchar(255), \
        name varchar(255), \
        role varchar(255)\
        matchesPlayed int, \
        runs int, \
        average float, \
        strikerate float \
    )'
)


@app.route('/api/admin/signup', methods=['POST'])
def signUp():
    try:
        name = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if(name == None or password == None or email == None or name == '' or password == '' or email == ''):
            return jsonify({
                'status': 'account not created',
                'msg': 'some parameters are missing'
            }), 
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashPassword = bcrypt.hashpw(bytes, salt)
        hashPassword = str(hashPassword)
        print(str(hashPassword), type(hashPassword))
        userId = str(generateUserId())
        print(type(userId), len(userId))

        cursor.execute("INSERT INTO ADMIN values(%s, %s, %s, %s)", (userId, name, hashPassword, email))
        mydb.commit()
        return jsonify({
            "status": "account created",
            "status_code": 200,
            "user_id": userId
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "error": e
        }), 500
    
@app.route("/api/admin/login", methods=["POST"])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashPassword = bcrypt.hashpw(bytes, salt)

        cursor.execute('SELECT userId, password FROM ADMIN WHERE name = %s', (username,))
        account = cursor.fetchone()
        if account:
            if not bcrypt.checkpw(account['password'], hashPassword):
                return jsonify({
                    "status": "Incorrect username/password provided. Please retry",
                    "status_code": 401
                }), 401
            token = jwt.encode({
                'id': account['userId'],
                'exp': datetime.utcnow() + timedelta(minutes = 5)
            }, app.config['SECRET_KEY'])
            return jsonify({
                "status": "Login successful",
                "status_code": 200,
                "user_id": account['userId'],
                "token": token.decode('utf-8')
            }), 200
        else:
            return jsonify({
                    "status": "Incorrect username/password provided. Please retry",
                    "status_code": 401
                }), 401

    except Exception as e:
        print(e)
        return jsonify({
            "status": "Internal server error",
            "status_code": 500
        }), 500
    
@app.route('/api/matches', methods=['GET'])
def getMatches():
    try:
        cursor.execute("SELECT * FROM MATCH")
        matches = cursor.fetchall()
        return jsonify({
            "matches": matches,
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "Internal server error",
            "status_code": 500
        }), 500
    
@app.route('/api/matches/<match_id>', methods=['POST'])
def getMatchDetails(match_id):
    try:
        cursor.execute("SELECT * FROM MATCH WHERE matchId = %s", (match_id, ))
        match = cursor.fetchone()
        cursor.execute("SELECT * FROM SQUAD WHERE Team = %s", (match['team1'], ))
        team1 = cursor.fetchall()
        cursor.execute("SELECT * FROM SQUAD WHERE Team = %s", (match['team2'], ))
        team2 = cursor.fetchall()
        
        return jsonify({
            "match_id": match_id,
            "team_1": match['team1'],
            "team_2": match['team2'],
            "date": match['date'],
            "venue": match['venue'],
            "status": match['status'],
            "squads": {
                "team_1": team1,
                "team_2": team2
            }
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "Internal server error",
            "status_code": 500
        }), 500
    
@app.route('/api/players/<player_id>/stats', methods=['GET'])
def getPlayerStats(player_id):
    try:
        cursor.execute("SELECT name, matchesPlayed, runs, average, strikerate from SQUAD where playerId = %s", (player_id, ))
        player = cursor.fetchone();
    
        return jsonify({
            "player_id": player_id,
            "name": player['name'],
            "matches_played": player['matchesPlayed'],
            "runs": player['runs'],
            "average": player['average'],
            "strike_rate": player['strikerate']
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "Internal server error",
            "status_code": 500
        }), 500