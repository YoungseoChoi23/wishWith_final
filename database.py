import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
            firebase = pyrebase.initialize_app(config)
            self.db = firebase.database()
            self.storage = firebase.storage()

    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "name": data['name']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False
        
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        print("users###", users.val())
        if str(users.val()) == "None":  # first registration
            return True
        else:
            for res in users.each():
                value = res.val()
                if value['id'] == id_string:
                    return False
            return True
        
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    def get_user_info(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            user_info = res.val()
            if user_info['id'] == user_id:
                return user_info
        return None