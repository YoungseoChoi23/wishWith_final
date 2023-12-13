from flask import Flask, render_template , url_for, request, redirect , flash, session, jsonify
import hashlib
from bs4 import BeautifulSoup
import requests
from database import DBhandler
import re



app = Flask(__name__)
app.config["SECRET_KEY"]="helloosp"
DB = DBhandler()

@app.route("/product-add") 
def productAdd():
    return render_template('product_add.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/header")
def headerBefore():
    return render_template('layout/header.html')
@app.route("/header-only")
def headerAfter():
    return render_template('layout/header_only.html')
@app.route("/footer")
def footerEnter():
    return render_template('layout/footer.html')

@app.route("/signup1")
def signup1():
    return render_template('signup1.html')

@app.route("/signup3")
def signup3():
    return render_template('signup3.html')

@app.route("/signup2", methods=["GET", "POST"])
def signup2():
    if request.method == "POST":
        return redirect(url_for('signup1'))
    return render_template('signup2.html')

@app.route("/signup1_post", methods=['POST'])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    
    if DB.insert_user(data, pw_hash):
        return 'signup3' 
    else:
        return jsonify({'error': '이미 존재하는 아이디입니다!'}), 400
    
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route("/login_confirm", methods=['POST'])
def login_user():
    print("실행됨")
    id_=request.form['id']
    pw=request.form['password']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('index'))
    else:
        flash("존재하지 않는 정보입니다! 다시 로그인을 시도해주세요.")
        return redirect(url_for('index'))
    
@app.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('index'))



# 크롤링 코드
@app.route("/process-url", methods=['POST'])
def process_url():
    data = request.get_json()
    url = data['url']
    
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h3', class_='_22kNQuEXmb _copyable').text
    price = soup.find('span', class_='_1LY7DqCnwR').text
    delivery = soup.find('span', class_='bd_3uare').text

    img_element = soup.find('img', class_='_2RYeHZAP_4')

    image_url = None
    
    if img_element:
    # src 속성 추출
        image_url = img_element['src']
        print("Extracted Image URL:", image_url)
    else:
        print("Image tag with specified class not found.")

    return {
        'title': title,
        'price': price,
        'delivery': delivery,
        'image_url': image_url,
        'url' : url
    }

@app.route("/add-product-post", methods=["POST"])
def registerproduct():

    hidden_title = request.form.get("hidden-title")
    hidden_price = request.form.get("hidden-price")
    hidden_delivery = request.form.get("hidden-delivery")
    hidden_url = request.form.get("hidden-url")
    hidden_image_url = request.form.get("hidden-image-url")
    user_id = session.get('id', 'default-user-id')
    data = {
        "product_description": request.form.get("product-description"),
        "product_number": request.form.get("product-number"),
        "product_category": request.form.get("product-category"),
        "start_date": request.form.get("start-date"),
        "end_date": request.form.get("end-date"),
        "people_number": request.form.get("people-number"),
        "title": hidden_title,
        "price": hidden_price,
        "delivery": hidden_delivery,
        "url": hidden_url,
        "image_url": hidden_image_url,
        "user_id": user_id
    }
    print(data)
    DB.insert_item(data)
    return redirect(url_for('mypage'))

@app.route("/products-list")
def view_list():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", None)
    per_page = 6  # 페이지 당 표시할 아이템 수
    per_row = 3  # 행 당 표시할 아이템 수
    
    data = DB.get_items(category=category)  # 카테고리에 따라 아이템 가져오기
    print(data)
    
    # 페이지네이션 로직
    item_counts = len(data)
    data = dict(list(data.items())[page * per_page:(page + 1) * per_page])
    row_data = [list(data.items())[i * per_row:(i + 1) * per_row] for i in range((len(data) + per_row - 1) // per_row)]

    return render_template("product_list.html", row_data=row_data, limit=per_page, page=page, page_count=int((item_counts + per_page - 1) / per_page), total=item_counts)



@app.route('/mypage')
def mypage():
    user_id = session['id']
    user_info = DB.get_user_info(user_id)
    print(user_info)
    return render_template('mypage.html', user_info=user_info)

@app.route('/my-reviews')
def my_reviews():
    if 'id' not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for('index'))

    user_id = session['id']
    user_reviews = DB.get_user_reviews(user_id)
    return render_template('my_review.html', reviews=user_reviews)


@app.route("/parti-product") 
def partiProduct():
    return render_template("parti_product.html")

@app.route("/written-review")
def writtenReview():
    return render_template("written_review.html")

@app.route("/review-add") 
def reviewAdd():
    return render_template('review_add.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)