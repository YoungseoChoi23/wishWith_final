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
    
    def get_items(self, category=None):
    # 모든 아이템을 가져오는 경우
        if not category:
            items = self.db.child("item").get().val()
            return items if items else {}

        # 특정 카테고리의 아이템만 가져오는 경우
        all_items = self.db.child("item").get().val()
        if not all_items:
            return {}

        # 카테고리에 따라 필터링
        filtered_items = {}
        for key, item in all_items.items():
            if item.get("product_category") == category:
                filtered_items[key] = item

        return filtered_items
    
    def get_my_items(self, user_id=None):
    # 모든 아이템을 가져오는 경우
        items = self.db.child("item").get().val()
        if not items:
            return {}  # 데이터베이스에 아이템이 없는 경우 빈 딕셔너리 반환

        filtered_items = {}
        for key, item in items.items():
            # 카테고리와 사용자 ID에 따라 필터링
            if (not user_id or item.get("user_id") == user_id):
                filtered_items[key] = item

        return filtered_items


    
    def get_user_info(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            user_info = res.val()
            if user_info['id'] == user_id:
                return user_info
        return None
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value = ""

        print("###########", name)

        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()

        return target_value
    
    def insert_item(self, data):
    # DB에 저장할 item 정보 구성
        item_info = {
        "product_description": data['product_description'],
        "product_number": data['product_number'],
        "product_category": data['product_category'],
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "title": data['title'],
        "price": data['price'],
        "delivery": data['delivery'],
        "url": data['url'],
        "image_url": data['image_url'],
        "people_number": data['people_number'],
        "user_id": data['user_id']
    }

    # 데이터베이스에 item 저장
        self.db.child("item").push(item_info)
        print(item_info)
        return True
    
    def insert_product_for_user(self, user_id, name):
        users = self.db.child("user").get()
        for res in users.each():
            value = res.val()
            if value['id'] == user_id:
                self.db.child("user").child(res.key()).child("purchases").push(name)
                return True  # 사용자를 찾았을 때 해당 사용자의 키를 반환
        
        
        return False



