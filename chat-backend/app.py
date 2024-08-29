from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from googletrans import Translator
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# Initialize Google Translator
# translator = Translator()

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    preferred_language = db.Column(db.String(50), nullable=False)

# Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# User Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    preferred_language = data.get('preferred_language')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, preferred_language=preferred_language)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# User Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'preferred_language': user.preferred_language})

# Real-time messaging with SocketIO
@socketio.on('message')
@jwt_required()
def handle_message(data):
    user_id = get_jwt_identity()
    recipient_id = data.get('recipient_id')
    message_text = data.get('message_text')

    sender = User.query.get(user_id)
    recipient = User.query.get(recipient_id)

    if not recipient:
        emit('error', {'error': 'Recipient not found'})
        return

    # Translate message if the recipient's preferred language is different
    # if sender.preferred_language != recipient.preferred_language:
    #     translated_message = translator.translate(message_text, dest=recipient.preferred_language).text
    # else:
    #     translated_message = message_text
    translated_message = message_text

    # Store message in the database
    new_message = Message(sender_id=sender.id, recipient_id=recipient.id, message_text=message_text)
    db.session.add(new_message)
    db.session.commit()

    # Emit the translated message to the recipient
    emit('new_message', {'message': translated_message, 'sender': sender.username}, room=recipient_id)

# WebSocket connection handler
@socketio.on('connect')
def handle_connect():
    print("User connected")

# WebSocket disconnect handler
@socketio.on('disconnect')
def handle_disconnect():
    print("User disconnected")

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)