from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_socketio import SocketIO
from flask_socketio import Namespace, emit, join_room, disconnect
from flask_cors import CORS
import sys
import time
sys.path.append('../')
from database.tag import insert_tag, get_tags, delete_tag, exists
from database.user import add_new_user, load_mypage, update_data, delete_data
from database.chatroom import add_chatroom, check_chatroom, delete_chatroom
from auth.auth import signup, signin, verify, refresh_token
from auth.update import update_user
from auth.delete import delete_user

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/user", methods=["POST"])
def sign_up_user():
    given_json = request.json

    # Make token and id
    access_token, user_id = signup(
        email=given_json["email"],
        password=given_json["password"]
    )
    # provisional
    # access_token = "qawse"
    # user_id = "1010120"

    # Store to database
    add_new_user(
        user_id=user_id,
        email=given_json["email"],
        name=given_json["username"]
    )

    responsed_json = {
        "token": access_token
    }

    return _corsify_actual_response(jsonify(responsed_json)), 200


@app.route("/login", methods=["POST"])
def sign_in_user():
    given_json = request.json

    # Authentication
    access_token = signin(
        email=given_json["email"],
        password=given_json["password"]
    )
    # provisional
    # access_token = "qawse"
    # user_id = "1010120"

    responsed_json = {
        "token": access_token
    }

    return _corsify_actual_response(jsonify(responsed_json)), 200


@app.route("/user/load", methods=["GET"])
def load_user_page():

    access_token = request.headers.get("access_token")

    # Convert token to ID
    user_id = verify(access_token)
    if user_id == "":
        return _corsify_actual_response(jsonify({})), 401

    username, email = load_mypage(user_id)
    tags = get_tags(user_id)

    # provisional
    # username = "hoge"
    # email = "tmp@hoge.com"
    # tag = [{
    #         "id" : 0,
    #         "tag_name" : "test1"
    #     },
    #     {
    #         "id": 1,
    #         "tag_name": "test2"
    #     }
    # ]

    responsed_json = {
        "username": username,
        "email": email,
        "tag": tags
    }

    return _corsify_actual_response(jsonify(responsed_json)), 200


@app.route("/user/edit", methods=["POST"])
def edit_user_page():
    access_token = request.headers.get("access_token")
    # Convert token to ID
    user_id = verify(access_token)
    if user_id == "":
        return _corsify_actual_response(jsonify({})), 401

    given_json = request.json
    given_json["user_id"] = user_id

    # tags
    # New Tag
    for t_name in given_json["new_tag_names"]:
        insert_tag(user_id, t_name)
    # Delete Tag
    for t_name in given_json["delete_tag_names"]:
        if exists(user_id, t_name) == 0:
            return _corsify_actual_response(jsonify({})), 404
        delete_tag(user_id, t_name)

    # update Auth data
    # user = update_user(given_json["user_id"], given_json["email"], given_json["password"])
    # パスワード、メールはもう変更しない仕様に！
    # フロントからメール情報は送られてこなくなったので、データベースからロード（仮）
    _, email = load_mypage(user_id)

    # update Database
    update_data(given_json["user_id"], given_json["username"], email)
    # provisional
    # user_id = 1010120

    # "firebase_admin.update_user"でuidが変わる...??
    # リフレッシュすればいける？
    # new_token = refresh_token(given_json["token"])

    responsed_json = {
        "token": access_token
    }

    return _corsify_actual_response(jsonify(responsed_json)), 200

def transform_tags_dict(tags):
    """
    tag = [ {"id": 0,
            "tag_name": "test1"},
            {"id": 1,
            "tag_name": "test2"}]
    ->
    tag = {"ids" : [0, 1],
           "names" : ["test1", "test2"]}
    """
    transformed = {"ids":[], "tag_name":[]}

    for t in tags:
        transformed["ids"].append(t["id"])
        transformed["tag_name"].append(t["tag_name"])

    return transformed


@app.route("/user/delete", methods=["POST"])
def delete_account():
    access_token = request.headers.get("access_token")
    # Convert token to ID
    user_id = verify(access_token)
    if user_id == "":
        return _corsify_actual_response(jsonify({})), 401

    given_json = request.json
    given_json["user_id"] = user_id

    # delete Auth data
    delete_user(given_json["user_id"])
    # delete Database
    delete_data(given_json["user_id"])

    responsed_json = {

    }
    return _corsify_actual_response(jsonify(responsed_json)), 200

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/tag", methods=["POST"])
def insert_db_tag():
    access_token = request.headers.get("access_token")
    given_json = request.json
    tag_name = given_json['tag_name']
    user_id = verify(access_token)
    if user_id == '':
        return _corsify_actual_response(jsonify({})), 401
    exist_flag = exists(user_id, tag_name)
    if exist_flag == 1:
        return _corsify_actual_response(jsonify({})), 400
    insert_tag(user_id, tag_name)
    return _corsify_actual_response(jsonify({})), 204

@app.route("/tags", methods=["GET"])
def get_db_tags():
    access_token = request.headers.get("access_token")
    user_id = verify(access_token)
    if user_id == '':
        return _corsify_actual_response(jsonify({})), 401
    tags = get_tags(user_id)
    return _corsify_actual_response(jsonify({ 'tags': tags })), 200

@app.route("/tag/delete", methods=["POST"])
def delete_db_tag():
    access_token = request.headers.get("access_token")
    given_json = request.json
    tag_name = given_json['tag_name']
    user_id = verify(access_token)
    if user_id == '':
        return _corsify_actual_response(jsonify({})), 401
    exist_flag = exists(user_id, tag_name)
    if exist_flag == 0:
        return _corsify_actual_response(jsonify({})), 404
    delete_tag(user_id, tag_name)
    return _corsify_actual_response(jsonify({})), 204
      
def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/chatrooms/<chatroom_id>", methods=["GET"])
def get_chatroom_users(chatroom_id):
    access_token = request.headers.get("access_token")
    user_id = verify(access_token)
    if user_id == '':
        return _corsify_actual_response(jsonify({})), 401
    users = check_chatroom(chatroom_id)
    if users != 4:
        return _corsify_actual_response(jsonify({})), 205
    return _corsify_actual_response(jsonify({})), 200

@app.route("/chatrooms", methods=["POST"])
def join_chatroom():
    access_token = request.headers.get("access_token")
    given_json = request.json
    tag_name = given_json['tag_name']
    user_id = verify(access_token)
    if user_id == '':
        return _corsify_actual_response(jsonify({})), 401
    chatroom_id = add_chatroom(user_id, tag_name)
    return _corsify_actual_response(jsonify({ 'chatroom_id': chatroom_id })), 200

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

class MyNamespace(Namespace):
    def on_ping_ping(self, data):
        print("ping")
        time.sleep(3)
        emit('pong_pong')

    def on_connect_req(self, data): # connect
        print("connect_req")
        access_token = data['access_token']
        chatroom_id = data['chatroom_id']
        print("chatroom_id: ", chatroom_id)
        if verify(access_token) != "":
            #join_room(chatroom_id)
            emit('connect_res', {'status': 'ok'})
        else:
            emit('connect_res', {'status': 'incorrect access token'})

    def on_send_message_req(self, data): # send message
        print("send_message_req")
        access_token = data['access_token']
        chatroom_id = data['chatroom_id']
        content = data['content']
        print("chatroom_id: ", chatroom_id)
        print("content: ", content)
        user_id = verify(access_token)
        if user_id != "":
            username, _ = load_mypage(user_id)
            result = {'username': username, 'content': content, 'access_token': access_token}
            emit('send_message_res', result, room_id=chatroom_id)
        else:
            emit('send_message_res', {'status': 'incorrect access token'})

    def on_disconnect_req(self, data): # disconnect
        print("disconnect")
        access_token = data['access_token']
        chatroom_id = data['chatroom_id']
        user_id = verify(access_token)
        if user_id != "":
            delete_chatroom(chatroom_id)

socketio.on_namespace(MyNamespace('/chat'))

if __name__ == '__main__':
    socketio.run(app)