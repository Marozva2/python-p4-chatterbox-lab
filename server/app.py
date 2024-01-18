from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    message_list = [{"id": msg.id, "body": msg.body, "username": msg.username, "created_at": msg.created_at} for msg in messages]
    response = make_response(jsonify(message_list), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.get(id)
    if message:
        message_data = {"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at}
        return jsonify(message_data)
    return jsonify({"message": "Message not found"}), 404

# POST new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    new_message = Message(body=data.get('body'), username=data.get('username'))
    db.session.add(new_message)
    db.session.commit()
    response_data = {"id": new_message.id, "body": new_message.body, "username": new_message.username, "created_at": new_message.created_at}
    response = make_response(jsonify(response_data), 201)
    response.headers['Content-Type'] = 'application/json'
    return response

# PATCH message by ID
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if message:
        data = request.get_json()
        message.body = data.get('body', message.body)
        db.session.commit()
        updated_data = {"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at}
        response = make_response(jsonify(updated_data), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    return make_response(jsonify({"message": "Message not found"}), 404)


# DELETE message by ID
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({"message": "Message deleted successfully"}), 200)
    return make_response(jsonify({"message": "Message not found"}), 404)


if __name__ == '__main__':
    app.run(port=5555)
