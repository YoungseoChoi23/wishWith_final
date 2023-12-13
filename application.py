from flask import Flask, render_template , url_for, request, redirect , flash, session, jsonify
import hashlib
from bs4 import BeautifulSoup
import requests
from database import DBhandler


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
    id_=request.form['id']
    pw=request.form['password']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('index'))
    else:
        flash("존재하지 않는 정보입니다! 다시 로그인을 시도해주세요.")
        return redirect(url_for('login'))
    
@app.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('index'))



# 크롤링 코드
@app.route('/crawl-url', methods=['POST'])
def crawl_url():
    data = request.json
    url = data['url']
    print(url)
    # URL에서 HTML을 가져온 후 BeautifulSoup로 파싱
    response = requests.get(url)
    print(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)

    # 이미지 링크 추출
    image_link = soup.find('img', class_='prod-image__detail')['src']
    print(image_link)
    # 제품명 추출
    title = soup.find('h2', class_='prod-buy-header__title').get_text(strip=True)

    # 가격 정보 추출
    sale_price_div = soup.select_one('.prod-sale-price')
    sale_total_price = sale_price_div.select_one('strong').get_text(strip=True)
    sale_unit_price = sale_price_div.select_one('.unit-price').get_text(strip=True)

    coupon_price_div = soup.select_one('.prod-coupon-price')
    coupon_total_price = coupon_price_div.select_one('strong').get_text(strip=True)
    coupon_unit_price = coupon_price_div.select_one('.unit-price').get_text(strip=True)

    delivery_info = soup.select_one('.prod-shipping-fee-message em').get_text(strip=True)
    arrival_info = soup.select_one('.prod-pdd em').get_text(strip=True)

    # 추출된 정보를 JSON 형태로 반환
    return jsonify({
        'image_link': image_link,
        'title': title,
        'price_info': sale_total_price,
        'per_price_info': sale_unit_price,
        'unit_price_info': coupon_total_price,
        'per_unit_price_info': coupon_unit_price,
        'delivery_info': delivery_info,
        'arrival_info': arrival_info
    })

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)