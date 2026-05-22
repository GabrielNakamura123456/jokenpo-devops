from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

# =====================
# LOAD ENV
# =====================

load_dotenv()

# =====================
# APP CONFIG
# =====================

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "connect_args": {
        "sslmode": "require"
    }
}

db = SQLAlchemy(app)

# =====================
# MODELS
# =====================

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    user_choice = db.Column(db.String(20))
    computer_choice = db.Column(db.String(20))
    result = db.Column(db.String(30))

# =====================
# ROUTES
# =====================

@app.route('/')
def index():
    return "API Jokenpo com PostgreSQL funcionando!"

# =====================
# CREATE PLAYER
# =====================

@app.route('/player', methods=['POST'])
def create_player():

    data = request.json

    player = Player(name=data['name'])

    db.session.add(player)
    db.session.commit()

    return jsonify({
        'message': 'Jogador criado!',
        'id': player.id
    })

# =====================
# PLAY GAME
# =====================

@app.route('/play', methods=['POST'])
def play_game():

    data = request.json

    player_id = data['player_id']
    user_choice = data['choice'].lower()

    if user_choice not in ['pedra', 'papel', 'tesoura']:
        return jsonify({
            'error': 'Escolha inválida'
        }), 400

    computer_choice = random.choice([
        'pedra',
        'papel',
        'tesoura'
    ])

    result = determine_winner(
        user_choice,
        computer_choice
    )

    match = Match(
        player_id=player_id,
        user_choice=user_choice,
        computer_choice=computer_choice,
        result=result
    )

    db.session.add(match)
    db.session.commit()

    return jsonify({
        'result': result,
        'computer_choice': computer_choice
    })

# =====================
# LIST MATCHES
# =====================

@app.route('/matches', methods=['GET'])
def list_matches():

    matches = Match.query.all()

    output = []

    for match in matches:

        output.append({
            'id': match.id,
            'player_id': match.player_id,
            'user_choice': match.user_choice,
            'computer_choice': match.computer_choice,
            'result': match.result
        })

    return jsonify(output)

# =====================
# GAME RULES
# =====================

def determine_winner(user_choice, computer_choice):

    if user_choice == computer_choice:
        return "Empate"

    elif (
        (user_choice == "pedra" and computer_choice == "tesoura") or
        (user_choice == "tesoura" and computer_choice == "papel") or
        (user_choice == "papel" and computer_choice == "pedra")
    ):
        return "Você"

    else:
        return "Computador"

# =====================
# START APP
# =====================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(
        host='0.0.0.0',
        port=80
    )