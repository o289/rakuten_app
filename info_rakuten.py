import os, requests
# 
from flask import Flask, render_template, request

# 環境変数を使用する際に必須
from dotenv import load_dotenv
from time import sleep as sl
from bs4 import BeautifulSoup

app = Flask(__name__)

# HTML
root_html = 'index.html'
product_html = 'product.html'
game_html = 'game.html'
book_html = 'book.html'
golf_html = 'golf.html'
hotel_html = 'hotel.html'
result_html = 'result.html'

# class

#環境変数 
load_dotenv()

app_id = os.environ['RAKUTEN_APPLICATION_ID']
affiliate_id = os.environ['RAKUTEN_AFFILIATE_ID']

# 検索に関するHTML
@app.route('/')
def root():
    return render_template(root_html)

# 商品検索画面
@app.route('/product', methods=['get'])
def product():
    return render_template(product_html)

# ゲーム検索画面
@app.route('/game', methods=['get'])
def game():
    return render_template(game_html)

# 書籍検索画面
@app.route('/book', methods=['get'])
def book():
    return render_template(book_html)

# ゴルフ検索画面
@app.route('/golf', methods=['get'])
def golf():
    return render_template(golf_html)

# ホテル検索画面
@app.route('/hotel', methods=['get'])
def hotel():
    return render_template(hotel_html)



# カラムを作成する This is creating columns of search result.
def create_columns(title: str, body, sentence_type: int):
    # 普通
    if sentence_type == 0:
        columns = f"<tr><th>{title}</th><td>{body}</td></tr>"
    
    # まあまあ長い文章
    elif sentence_type == 1:
        columns = f"<tr><th>{title}</th><td class='text-left'>{body}</td></tr>"
    
    # 長い文章
    elif sentence_type == 2:
        columns = f"<tr><th>{title}</th><td class='text-left text-container'><p class='long-sentence'>{body}</p></td></tr>"
    
    # 得点
    elif sentence_type == 3:
        columns = f"<tr><th>{title}</th><td>{body}点</td></tr>"
    
    # 件数
    elif sentence_type == 4:
        columns = f"<tr><th>{title}</th><td>{body}件</td></tr>"
    
    # 価格
    elif sentence_type == 5:
        columns = f"<tr><th>{title}</th><td>{body}円</td></tr>"

    else:
        raise ValueError('You must set 0 ~ 5 in sentence_type.')
    return columns


# レビュー点数の星5化
def star(obj):
    if obj is None:
        value = 'なし'
    else:
        obj = str(obj)

        # カンマが含まれていたら、小数点なので四捨五入する
        if '.' in obj:
            obj = float(obj)
            obj = round(obj)
        else:
            obj = int(obj)
        # 点数で星の数を分ける
        if obj == 5:
            value = '★★★★★'
        
        elif obj >= 4:
            value = '★★★★☆'
        
        elif obj >= 3:
            value = '★★★☆☆'
        
        elif obj >= 2:
            value = '★★☆☆☆' 
        
        elif obj >= 1:
            value = '★☆☆☆☆'
        
        elif obj == 0:
            value = '評価なし'
        
        else:
            raise ValueError('This value was nothing.')
        
    return value


# 商品検索
@app.route('/search_product', methods=['post'])
def product_search():
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'
    rf = request.form
    
    # 検索パラメーター  
    keyword = rf['product']
    want_product_length_search = int(rf['want_product'])
    max_price_search = int(rf['max_price'])
    min_price_search = int(rf['min_price'])
    product_sort = rf['product_sort']
    postage_sort = int(rf['postage'])
    purchase_type = int(rf['purchase_type'])
    if purchase_type >= 3:
        raise ValueError('Over 3 is Invalid value.')

    # 表示する情報（チェックボックス）
    get_code = rf.get('get_code', '0')
    get_tax = rf.get('get_tax', '0')
    get_shop = rf.get('get_shop', '0')
    get_shop_code = rf.get('get_shop_code', '0')
    get_caption = rf.get('get_caption', '0')
    get_postage = rf.get('get_postage', '0')
    get_asuraku = rf.get('get_asuraku', '0')
    get_overseas = rf.get('get_overseas', '0')
    get_credit_card = rf.get('get_credit_card', '0')
    get_review_count = rf.get('get_review_count', '0')
    get_review_average = rf.get('get_review_average', '0')
    get_gift_flag = rf.get('get_gift_flag', '0')
    
    # 楽天APIにリクエストするためのパラメーター
    
    params = {
        "applicationId": app_id, 
        "affiliateId": affiliate_id,
        "hits": want_product_length_search,
        "keyword": keyword,
        "page": 1,
        "maxPrice": max_price_search,
        "minPrice": min_price_search,
        "sort": product_sort,
        "imageFlag": 1,
        "postageFlag": postage_sort,
        "purchaseType": purchase_type
        
    }


    # レスポンス
    response = requests.get(url, params=params) 
    res = response.json()
    res_code = response.status_code
    
    print(res_code)

    items = res['Items']

    if not items:
        result = "<h2>商品がありません</h2>"
    else:
        result = "<div class='grid-container'>"
        count = 1
        for i in items:
            item = i['Item']

            # 商品URL
            url = item['itemUrl']
            
            product_num = f'商品No.{count}'
            
            result += f"<table class='tb01'><h2>{product_num}</h2>"
            # 商品名 
            name = item['itemName']
            result += create_columns(title='商品名', body=name, sentence_type=1)
            

            # 価格
            price = item['itemPrice']
            result += create_columns(title='価格', body=price, sentence_type=5)
            
            # 税
            if get_tax == '1':
                # There is a if tax.
                tax_flag = item['taxFlag']
                if tax_flag == 0:
                    tax = "税込価格"
                elif tax_flag == 1:
                    tax = "税別価格"
                else: 
                    raise ValueError('Invalid value.')
                result += create_columns(title='税', body=tax, sentence_type=0)
                
            # レビュー数
            if get_review_count == '1':
                review_count = item['reviewCount']
                result += create_columns(title='レビュー数', body=f'{review_count}件',sentence_type=0)

            # レビュー平均点数
            if get_review_average == '1':
                review_average = item['reviewAverage']
                result += create_columns(title='レビュー平均', body=f'{review_average}点', sentence_type=0)

            # 商品コード
            if get_code == '1':
                code = item['itemCode']
                result += create_columns(title='商品コード', body=code, sentence_type=0)
            
            # 販売店
            if get_shop == '1':
                shop = item['shopName']
                result += create_columns(title='販売店', body=shop, sentence_type=0)

            # 販売店コード
            if get_shop_code == '1':
                shop_code = item['shopCode']
                result += create_columns(title='販売店コード', body=shop_code, sentence_type=0)

            # 送料
            if get_postage == '1':
                # There is a if postage.
                postage_flag = item['postageFlag']
                if postage_flag == 0:
                    postage = "送料込/送料無料"
                elif postage_flag == 1:
                    postage = "送料別"
                else: 
                    raise ValueError('Invalid value.')
                result += create_columns(title='送料', body=postage, sentence_type=0)
                
            # 翌日配送
            if get_asuraku == '1':
                # There is a if asuraku.
                asuraku_flag = item['asurakuFlag']
                if asuraku_flag == 0:
                    asuraku = '不可'
                    result += create_columns(title='翌日配送', body=asuraku, sentence_type=0)

                elif asuraku_flag == 1:
                    asuraku = '可'
                    asuraku_area = item['asurakuArea']
                    asuraku_closing_time = item['asurakuClosingTime']
                    asuraku_area = asuraku_area.replace('/', '|')
                    
                    result += create_columns(title='翌日配送', body=asuraku, sentence_type=0)
                    result += create_columns(title='翌日配送可能地域', body=asuraku_area, sentence_type=1)
                    result += create_columns(title='翌日配送締切日', body=asuraku_closing_time, sentence_type=0)
                    
                else:
                    raise ValueError('Invalid value.')

            # 海外配送
            if get_overseas == '1':
                ship_overseas_flag = item['shipOverseasFlag']
                if ship_overseas_flag == 0:
                    ship_overseas = '不可'
                    result += create_columns(title='海外配送', body=ship_overseas, sentence_type=0)
                    
                elif ship_overseas_flag == 1:
                    ship_overseas = '可'
                    ship_overseas_area = item['shipOverseasArea']
                    ship_overseas_area = ship_overseas_area.replace('/', '|')
                    
                    result += create_columns(title='海外配送', body=ship_overseas, sentence_type=0)
                    result += create_columns(title='海外配送可能地域', body=ship_overseas_area, sentence_type=1)

                else:
                    raise ValueError('Invalid value.')

            # クレジットカード
            if get_credit_card == '1':
                credit_card_flag = item['creditCardFlag']
                if credit_card_flag == 0:
                    credit_card = '不可'
                elif credit_card_flag == 1:
                    credit_card = '可'
                else:
                    raise ValueError('Invalid value.')

                result += create_columns(title='カード', body=credit_card, sentence_type=0)
            
            # ギフト包装
            if get_gift_flag == '1':
                gift_flag = item['giftFlag']
                if gift_flag == 0:
                    gift = '不可'
                elif gift_flag == 1:
                    gift = '可'
                else:
                    raise ValueError('Invalid value.')

                result += create_columns(title='ギフト包装', body=gift, sentence_type=0)
            
            # 商品説明
            if get_caption == '1':
                caption = item['itemCaption']
                result += create_columns(title='商品説明', body=caption, sentence_type=2)
            
            result += "</table></div>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>商品はこちら</a>"
            count += 1

        result += "<form action='/product' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
        soup = BeautifulSoup(result, 'html.parser')
        result = soup.prettify()
        sl(1)
    
    return render_template(result_html, result=result)
    
# ゲームの検索
@app.route('/search_game', methods=['post'])
def game_search():
    url = 'https://app.rakuten.co.jp/services/api/BooksGame/Search/20170404'
    

    rf = request.form
    # 入力パラメーター
    game_search = rf['game']
    want_game_length_search = int(rf['want_game'])
    availability_game_search = int(rf['availability_game'])
    game_sort = rf['game_sort']
    
    # 欲しい情報
    get_item_caption = rf.get('get_item_caption', '0')
    get_hardware = rf.get('get_hardware', '0')
    get_jan_code = rf.get('get_jan_code', '0')
    get_sales_date = rf.get('get_sales_date', '0')
    get_availability = rf.get('get_availability', '0')
    get_postage = rf.get('get_postage', '0')
    get_limited = rf.get('get_limited', '0')
    get_label = rf.get('get_label', '0')
    get_maker_code = rf.get('get_maker_code', '0')
    get_review_count = rf.get('get_review_count', '0')
    get_review_average = rf.get('get_review_average', '0')



    params = {
        "applicationId": app_id,
        "affiliateId": affiliate_id,
        "title": game_search,
        "sort": game_sort,
        "availability": availability_game_search,
        "hits": want_game_length_search,
        "page": 1,
    } 

    # レスポンス
    response = requests.get(url, params=params) 
    res = response.json()
    res_code = response.status_code
    
    print(res_code)

    items = res['Items']
    count = 1
    
    if not items:
        result = "<h2>商品がありません</h2>"
    else:
        result = "<div class='grid-container'>"
        for i in items:
            item = i['Item']
            # length of items.
            product_num = f'商品No.{count}'


            # URL
            url = item['affiliateUrl']

            result += f"<table class='tb01'><h2>{product_num}</h2>"
            
            # ゲームタイトル
            game_title = item['title']
            result += create_columns(title='タイトル', body=game_title, sentence_type=0)

            # 価格
            price = item['itemPrice']
            result += create_columns(title='価格', body=f'{price}円', sentence_type=0)
            
            # ハード
            if get_hardware == '1':
                hardware = item['hardware']
                result += create_columns(title='対応機種', body=hardware, sentence_type=0)

            # JANコード
            if get_jan_code == '1':
                jan_code = item['jan']
                result += create_columns(title='JANコード', body=jan_code, sentence_type=0)

            # 発売日
            if get_sales_date == '1':
                sales_date = item['salesDate']
                result += create_columns(title='発売日', body=sales_date, sentence_type=0)

            # 販売種別
            if get_limited == '1':
                limited_type = item['limitedFlag']
                if limited_type == 0:
                    limited = '通常販売'
                elif limited_type == 1:
                    limited = '限定販売'
                else: 
                    raise ValueError('This value is nothing.')
                result += create_columns(title='販売種別', body=limited, sentence_type=0)

            # 在庫状況
            if get_availability == '1':
                availability_type = int(item['availability'])
                
                if availability_type == 1:
                    availability = '在庫あり'
                elif availability_type == 2:
                    availability = '通常3～7日程度で発送'
                elif availability_type == 3:
                    availability = '通常3～9日程度で発送'
                elif availability_type == 4:
                    availability = 'メーカー取り寄せ'
                elif availability_type == 5:
                    availability = '予約受付中'
                elif availability_type == 6:
                    availability = 'メーカーに在庫確認'
                else:
                    raise ValueError('This value is nothing.')
                result += create_columns(title='在庫状況', body=availability, sentence_type=0)

            # 送料
            if get_postage == '1':
                # There is a if postage.
                postage_flag = item['postageFlag']
                if postage_flag == 0:
                    postage = "送料別"
                elif postage_flag == 1:
                    postage = "宅配送料無料"
                elif postage_flag == 2:
                    postage = "完全送料無料"
                else: 
                    raise ValueError('Invalid value.')
                result += create_columns(title='送料', body=postage, sentence_type=0)

            # レビュー数
            if get_review_count == '1':
                review_count = item['reviewCount']
                result += create_columns(title='レビュー数', body=f'{review_count}件', sentence_type=0)

            # レビュー平均点数
            if get_review_average == '1':
                review_average = item['reviewAverage']
                result += create_columns(title='レビュー平均', body=f'{review_average}点', sentence_type=0)

            # 販売元
            if get_label == '1':
                label = item['label']
                result += create_columns(title='販売元', body=label, sentence_type=0)

            # 販売店コード
            if get_maker_code == '1':
                maker_code = item['makerCode']
                result += create_columns(title='販売店コード', body=maker_code, sentence_type=0)

            # 商品説明
            if get_item_caption == '1':
                caption = item['itemCaption']
                result += create_columns(title='商品説明', body=caption, sentence_type=2)

            result += "</table></div>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>製品はこちら</a>"
            
            count += 1

    result += "<form action='/game' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    sl(1)
    
    return render_template(result_html, result=result)    

# 本の検索
@app.route('/search_book', methods=['post'])
def book_search():
    url = 'https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404'
    rf = request.form

    # HTMLから値を取得する。
    # 1, type is text of input_tag.
    title = rf['book_name']
    if title is not None and title.strip() == '':
        title = None
    
    author = rf['author_name']
    if author is not None and author.strip() == '':
        author = None
    
    publisher = rf['publisher_name']
    if publisher is not None and publisher.strip() == '':
        publisher = None
    
    if title == None and author == None and publisher == None:
        raise ValueError('Value is missing. Please be sure to enter the name of the book, author, or publisher.')

    # 2, type is select_tag.
    want_get_book_length = int(rf['want_book'])
    get_sort = rf['book_sort']
    get_book_type = int(rf['book_type'])
    
    # 3, type is checkbox of input_tag.
    get_book_caption = rf.get('get_book_caption', '0')
    get_postage = rf.get('get_postage', '0')
    get_isbn_code = rf.get('get_isbn_code', '0')
    get_book_availability = rf.get('get_book_availability', '0')
    get_book_sales_date = rf.get('get_book_sales_date', '0')
    get_book_review_count = rf.get('get_book_review_count', '0')
    get_book_review_average = rf.get('get_book_review_average', '0')

    # パラメーター 
    params = {
        'applicationId': app_id,
        'affiliateId': affiliate_id,
        'title': title,
        'author': author,
        'publisherName': publisher,
        'size': get_book_type,
        'sort': get_sort,
        'hits': want_get_book_length,
    }
    
    # レスポンス
    response = requests.get(url, params=params) 
    res = response.json()
    res_code = response.status_code
    
    print(res_code)

    items = res['Items']
    count = 1
    
    # 
    if not items:
        result = "<h2>商品がありません</h2>"
    else:
        result = "<div class='grid-container'>"
        for i in items:
            item = i['Item']
            # length of items.
            product_num = f'商品No.{count}'

            # URL
            url = item['affiliateUrl']

            result += f"<table class='tb01'><h2>{product_num}</h2>"

            # タイトル
            book_title = item['title']
            result += create_columns(title='タイトル', body=book_title, sentence_type=0)
            
            # 価格
            price = item['itemPrice']
            result += create_columns(title='価格', body=f'{price}円', sentence_type=0)
            
            # 著者
            author_name = item['author']
            result += create_columns(title='著者', body=author_name, sentence_type=0)

            # 出版社
            publisher_name = item['publisherName']
            result += create_columns(title='出版社', body=publisher_name, sentence_type=0)

            # 書籍コード
            if get_isbn_code == '1':
                isbn = item['isbn']
                result += create_columns(title='ISBN', body=isbn, sentence_type=0)

            # 発売日
            if get_book_sales_date == '1':
                sales_date = item['salesDate']
                sales_date = sales_date.replace('頃', '')
                result += create_columns(title='発売日', body=sales_date, sentence_type=0)

            # 送料
            if get_postage == '1':
                # There is a if postage.
                postage_flag = int(item['postageFlag'])
                if postage_flag == 0:
                    postage = "送料別"
                elif postage_flag == 1:
                    postage = "宅配送料無料"
                elif postage_flag == 2:
                    postage = "完全送料無料"
                else: 
                    raise ValueError('Invalid value.')
                result += create_columns(title='送料', body=postage, sentence_type=0)

            # 在庫状況
            if get_book_availability == '1':
                availability_type = int(item['availability'])
                
                if availability_type == 1:
                    availability = '在庫あり'
                
                elif availability_type == 2:
                    availability = '通常3～7日程度で発送'
                
                elif availability_type == 3:
                    availability = '通常3～9日程度で発送'
                
                elif availability_type == 4:
                    availability = 'メーカー取り寄せ'
                
                elif availability_type == 5:
                    availability = '予約受付中'
                
                elif availability_type == 6:
                    availability = 'メーカーに在庫確認'
                
                else:
                    raise ValueError('This value is nothing.')
                
                result += create_columns(title='在庫状況', body=availability, sentence_type=0)


            # レビュー数
            if get_book_review_count == '1':
                review_count = item['reviewCount']
                result += create_columns(title='レビュー数', body=f'{review_count}件', sentence_type=0)

            # レビュー平均点数
            if get_book_review_average == '1':
                review_average = item['reviewAverage']
                result += create_columns(title='レビュー平均', body=f'{review_average}点', sentence_type=0)
            
            # 商品説明
            if get_book_caption == '1':
                caption = item['itemCaption']
                result += create_columns(title='商品説明', body=caption, sentence_type=2)

            result += "</table></div>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>書籍はこちら</a>"
            count += 1

    result += "<form action='/book' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"    
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    sl(1)
    return render_template(result_html, result=result)    


# ゴルフ場検索
@app.route('/search_golf', methods=['post'])
def golf_search():
    url = 'https://app.rakuten.co.jp/services/api/Gora/GoraGolfCourseSearch/20170623'
    
    # HTMLから値を取得
    rf = request.form
    # 1, text
    # ゴルフ場
    golf_course = rf['golf_course']
    if golf_course is not None and golf_course.strip() == '':
        golf_course = None
        

    # 2, select
    prefectures = int(rf['prefectures'])
    golf_sort = rf['golf_sort']
    want_golf = rf['want_golf']
    
    # 3, checkbox
    get_caption = rf.get('get_caption', '0')
    get_evaluation = rf.get('get_evaluation', '0')
    get_id = rf.get('get_id', '0')
    get_latitude = rf.get('get_latitude', '0')
    get_longitude = rf.get('get_longitude', '0')
    get_highway = rf.get('get_highway', '0')
    
    # パラメーター 
    params = {
        'applicationId': app_id,
        'affiliateId': affiliate_id,
        'keyword': golf_course,
        'areaCode': prefectures,
        'hits': want_golf,
        'sort': golf_sort,
        'reservation': 1
    }
    
    # レスポンス
    response = requests.get(url, params=params) 
    res = response.json()
    res_code = response.status_code
    
    print(res_code)
    
    items = res['Items']
    count = 1
    
    if not items:
        result = "<h2>ゴルフ場情報がありません</h2>"
    else:
        result = "<div class='grid-container'>"
        for i in items:
            item = i['Item']
            
            golf_num = f'ゴルフ場No.{count}'
            result += f"<table class='tb01'><h2>{golf_num}</h2>"

            # URL
            url1 = item['golfCourseDetailUrl']
            url2 = item['reserveCalUrl']


            # ゴルフ場
            golf_course_name = item['golfCourseName']
            result += create_columns(title='ゴルフ場', body=golf_course_name, sentence_type=0)
            
            # ゴルフ場ID
            if get_id == '1':
                golf_course_id = item['golfCourseId']
                result += create_columns(title='ゴルフ場ID', body=golf_course_id, sentence_type=0)
                
            # 総合評価
            if get_evaluation == '1':
                evaluation = item['evaluation']
                result += create_columns(title='総合評価', body=evaluation, sentence_type=0)

            # 所在地
            address = item['address']
            result += create_columns(title='所在地', body=address, sentence_type=0)

            # 緯度
            if get_latitude == '1':
                latitude = item['latitude']
                result += create_columns(title='緯度', body=latitude, sentence_type=0)

            # 経度
            if get_longitude == '1':
                longitude = item['longitude']
                result += create_columns(title='経度', body=longitude, sentence_type=0)
                
            # 高速道路
            if get_highway == '1':
                highway = item['highway']
                result += create_columns(title='最寄り高速道路', body=highway, sentence_type=0)

            # ゴルフ場説明
            if get_caption == '1':
                caption = item['golfCourseCaption']
                result += create_columns(title='ゴルフ場説明', body=caption, sentence_type=2)

            

            
            result += "</table></div>"
            result += f"<a href='{url1}' class='btn_03' ontouchstart=''>詳細はこちら</a>"
            result += f"<a href='{url2}' class='btn_03' ontouchstart=''>予約はこちら</a>"

            count += 1


    result += "<form action='/golf' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    sl(1)
    return render_template(result_html, result=result) 


# 宿泊施設検索
@app.route('/search_hotel', methods=['post'])
def hotel_search():
    url = 'https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426'
    rf = request.form

    # 1. input
    keyword = rf['keyword']
    # 2. select_box
    hotel_sort = rf['hotel_sort']
    want_hotel = int(rf['want_hotel'])
    prefecture = rf['prefecture']
    review = int(rf['review'])
    # 3. checkbox
    get_hotel_number = rf.get('get_hotel_number', '0')
    get_hotel_special = rf.get('get_hotel_special', '0')
    get_hotel_latitude = rf.get('get_hotel_latitude', '0')
    get_hotel_longitude = rf.get('get_hotel_longitude', '0')
    get_hotel_postal_code = rf.get('get_hotel_postal_code', '0')
    get_hotel_address = rf.get('get_hotel_address', '0')
    get_hotel_telephone = rf.get('get_hotel_telephone', '0')
    get_hotel_fax = rf.get('get_hotel_fax', '0')
    get_hotel_access = rf.get('get_hotel_access', '0')
    get_hotel_parking = rf.get('get_hotel_parking', '0')
    get_hotel_station = rf.get('get_hotel_station', '0')
    get_review_count = rf.get('get_review_count', '0')
    get_reviews = rf.get('get_reviews', '0')
    get_reserve_telephone = rf.get('get_reserve_telephone', '0')
    get_area_name = rf.get('get_area_name', '0')
    get_hotel_class_code = rf.get('get_hotel_class_code', '0')
    get_check_time = rf.get('get_check_time', '0')
    get_hotel_room_num = rf.get('get_hotel_room_num', '0')
    get_room_facilities = rf.get('get_room_facilities', '0')
    get_all_hotel_facilities = rf.get('get_all_hotel_facilities', '0')   
    get_about_leisure = rf.get('get_about_leisure', '0')
    get_handicapped_facilities = rf.get('get_handicapped_facilities', '0')
    get_linguistic_level = rf.get('get_linguistic_level', '0')
    get_note = rf.get('get_note', '0')
    get_cancel_policy = rf.get('get_cancel_policy', '0')
    get_credit_card = rf.get('get_credit_card', '0')
    get_privilege = rf.get('get_privilege', '0')



    params = {
        'applicationId': app_id,
        'affiliateId': affiliate_id,
        'keyword': keyword,
        'middleClassCode': prefecture,
        'sort': hotel_sort,
        'hits': want_hotel,
        'responseType': 'large',
        'formatVersion': 2
    }
    
    # レスポンス
    response = requests.get(url, params=params) 
    res = response.json()
    res_code = response.status_code
    print(res_code)

    hotels = res['hotels']
    count = 1
    
    
    if not hotels:
        result = '<h2>この条件では見つかりませんでした。</h2>'
    else:
        result = "<div class='grid-container'>"
        for hotel in hotels:

            #  
            hotel_num = f'ホテルNo.{count}'
            result += f"<table class='tb01'><h2>{hotel_num}</h2>"
            
            
            
            # 1, 基本情報
            hotel_basic = hotel[0]['hotelBasicInfo']
            
            # URL 
            url1 = hotel_basic['hotelInformationUrl']
            url2 = hotel_basic['planListUrl']

            # ホテル名
            hotel_name = hotel_basic['hotelName']
            result += create_columns(title='ホテル', body=hotel_name, sentence_type=0)
            
            # 価格
            hotel_min_price = hotel_basic['hotelMinCharge']
            if hotel_min_price is None:
                result += create_columns(title='最安値', body=f'詳細についてをクリック', sentence_type=0)
            else:
                result += create_columns(title='最安値', body=hotel_min_price, sentence_type=5)

            # ホテル番号
            if get_hotel_number == '1':
                hotel_number = hotel_basic['hotelNo']
                result += create_columns(title='ホテル番号', body=hotel_number, sentence_type=0)

            # ホテル説明
            if get_hotel_special == '1':
                hotel_special = hotel_basic['hotelSpecial']
                result += create_columns(title='ホテル説明', body=hotel_special, sentence_type=0)


            # 緯度
            if get_hotel_latitude == '1':
                latitude = hotel_basic['latitude']
                result += create_columns(title='緯度', body=latitude, sentence_type=0)
                
            # 経度
            if get_hotel_longitude == '1':
                longitude = hotel_basic['longitude']
                result += create_columns(title='経度', body=longitude, sentence_type=0)

            # 郵便番号
            if get_hotel_postal_code == '1':
                postal_code = hotel_basic['postalCode']
                result += create_columns(title='郵便番号', body=postal_code, sentence_type=0)

            # 住所
            if get_hotel_address == '1':
                address1 = hotel_basic['address1']
                address2 = hotel_basic['address2']
                address = address1 + address2
                result += create_columns(title='住所', body=address, sentence_type=0)

            # 施設電話番号
            if get_hotel_telephone == '1':
                telephone = hotel_basic['telephoneNo']
                result += create_columns(title='電話番号', body=telephone, sentence_type=0)

            # FAX
            if get_hotel_fax == '1':
                fax = hotel_basic['faxNo']
                result += create_columns(title='FAX番号', body=fax, sentence_type=0)

            # アクセス
            if get_hotel_access == '1':
                access = hotel_basic['access']
                result += create_columns(title='アクセス', body=access, sentence_type=0)

            # 駐車場情報
            if get_hotel_parking == '1':
                parking = hotel_basic['parkingInformation']
                result += create_columns(title='駐車場', body=parking, sentence_type=0)

            # 最寄り駅
            if get_hotel_station == '1':
                station = hotel_basic['nearestStation']
                result += create_columns(title='最寄り駅', body=station, sentence_type=0)

            # レビュー数
            if get_review_count == '1':
                review_count = hotel_basic['reviewCount']
                if review_count is None:
                    review_count = 'なし'
                    result += create_columns(title='レビュー数', body=review_count, sentence_type=0)
                else:
                    result += create_columns(title='レビュー数', body=review_count, sentence_type=4)

            
            
            
            
            # 2, レビュー・サービス・ロケーション・部屋・施設・風呂・食事
            
            if get_reviews == '1':
                review_average = hotel_basic['reviewAverage']
                hotel_rating = hotel[1]['hotelRatingInfo']
                service_average = hotel_rating['serviceAverage']
                location_average = hotel_rating['locationAverage']
                room_average = hotel_rating['roomAverage']
                equipment_average = hotel_rating['equipmentAverage']
                bath_average = hotel_rating['bathAverage']
                meal_average = hotel_rating['mealAverage']
                
                if review == 1:
                    reviews = f"<ul><li>平均:{star(obj=review_average)}</li><li>接客:{star(obj=service_average)}</li><li>立地:{star(obj=location_average)}</li><li>部屋:{star(obj=room_average)}</li><li>施設:{star(obj=equipment_average)}</li><li>風呂:{star(obj=bath_average)}</li><li>食事:{star(obj=meal_average)}</li></ul>"
                else:
                    reviews = f"<ul><li>平均:{review_average}</li><li>接客:{service_average}</li><li>立地:{location_average}</li><li>部屋:{room_average}</li><li>施設:{equipment_average}</li><li>風呂:{bath_average}</li><li>食事:{meal_average}</li></ul>"

                result += create_columns(title='レビュー', body=reviews, sentence_type=0)
                
            
            
            
            
            
            # 3, ホテル詳細情報
            hotel_detail = hotel[2]['hotelDetailInfo']

            # 予約センター電話番号
            if get_reserve_telephone == '1':
                reserve_telephone = hotel_detail['reserveTelephoneNo']
                result += create_columns(title='予約センター電話番号', body=reserve_telephone, sentence_type=0)

            # エリア
            if get_area_name == '1':
                area_name = hotel_detail['areaName']
                result += create_columns(title='エリア', body=area_name, sentence_type=0)

            # ホテルクラスコード
            if get_hotel_class_code == '1':
                hotel_class_code = hotel_detail['hotelClassCode']
                result += create_columns(title='ホテルクラスコード', body=hotel_class_code, sentence_type=0)

            # チェックイン・チェックアウト
            if get_check_time == '1':
                checkin_time = hotel_detail['checkinTime']
                last_checkin_time = hotel_detail['lastCheckinTime']
                checkout_time = hotel_detail['checkoutTime']
                if last_checkin_time is None:
                    last_checkin_time = 'なし'
                else:
                    last_checkin_time = last_checkin_time
                
                check_time = f"<ul><li>チェックイン:{checkin_time}</li><li>最終チェックイン:{last_checkin_time}</li><li>チェックアウト:{checkout_time}</li></ul>"

                result += create_columns(title='チェック時刻', body=check_time, sentence_type=0)
            
            
            
            
            
            
            
            # 4, ホテル施設詳細情報
            hotel_facilities = hotel[3]['hotelFacilitiesInfo']

            # 部屋数
            if get_hotel_room_num == '1':
                hotel_room_num = hotel_facilities['hotelRoomNum']
                result += create_columns(title='部屋数', body=hotel_room_num, sentence_type=0)

            # 部屋の設備・備品
            if get_room_facilities == '1':
                room_facilities = hotel_facilities['roomFacilities']
                room_facility= ''
                for fac in room_facilities:
                    facility = f"[{fac['item']}]、" 
                    room_facility += facility
                
                result += create_columns(title='設備・備品', body=room_facility, sentence_type=2)

            # 館内の設備
            if get_all_hotel_facilities == '1':
                all_hotel_facilities = hotel_facilities['hotelFacilities']
                all_hotel_facility= ''
                
                for fac in all_hotel_facilities:
                    facility = f"[{fac['item']}]、" 
                    all_hotel_facility += facility
                
                result += create_columns(title='館内設備', body=all_hotel_facility, sentence_type=2)

            # レジャー
            if get_about_leisure == '1':
                about_leisure = hotel_facilities['aboutLeisure']
                if about_leisure is None:
                    about_leisure = 'なし'
                    result += create_columns(title='近くのレジャー施設', body=about_leisure, sentence_type=0)
                else:
                    result += create_columns(title='近くのレジャー施設', body=about_leisure, sentence_type=2)
                
            
            # 身体障害者設備
            if get_handicapped_facilities == '1':
                handicapped_facilities = hotel_facilities['handicappedFacilities']
                handicappeds = ''
                if not handicapped_facilities:
                    handicappeds = 'なし'
                    result += create_columns(title='身体障者設備', body=handicappeds, sentence_type=0)
                else:
                    for h in handicapped_facilities:
                        handicapped = f"{h['item']}、"
                        handicappeds += handicapped
                    result += create_columns(title='身体障者設備', body=handicappeds, sentence_type=2)
            
            # スタッフの言語レベル
            if get_linguistic_level == '1':
                linguistic_level = hotel_facilities['linguisticLevel']
                if linguistic_level is None:
                    linguistic_level = 'なし'
                    
                result += create_columns(title='スタッフ外国語レベル', body=linguistic_level, sentence_type=0)
                
            
            
            
            
            # 5, 宿泊条件・決済関連
            hotel_policy_info = hotel[4]['hotelPolicyInfo']

            # 条件・注意事項・備考
            if get_note == '1':
                note = hotel_policy_info['note']
                result += create_columns(title='条件・注意事項・備考', body=note, sentence_type=2)

            # キャンセル
            if get_cancel_policy == '1':
                cancel_policy = hotel_policy_info['cancelPolicy']
                if cancel_policy is None:
                    cancel = 'なし'
                else:
                    cancel = cancel_policy
                
                result += create_columns(title='キャンセル', body=cancel, sentence_type=0)

            # 使用可能カード
            if get_credit_card == '1':
                available_credit_card = hotel_policy_info['availableCreditCard']
                about_credit_card_note = hotel_policy_info['aboutCreditCardNote']
                if available_credit_card is None:
                    credit_card = '不可'
                else:
                    credit_card = "<ul class='card-list'>"
                    for c in available_credit_card:
                        card = c['card']
                        credit_card += f"<li>{card}</li>"
                    credit_card += '</ul>'
                
                result += create_columns(title='クレジットカード', body=credit_card, sentence_type=2)
                    
                if about_credit_card_note is not None:
                    result += create_columns(title='クレジットカード利用における注意', body=about_credit_card_note,sentence_type=0)
                
            


            # 6, その他
            other_info = hotel[5]['hotelOtherInfo']
            # 特典

            if get_privilege == '1':
                privilege = other_info['privilege']            
                if privilege is not None:
                    privilege = 'なし'
                else: 
                    privilege = privilege
                
                result += create_columns(title='特典', body=privilege, sentence_type=0)
                
            
            
            result += '</table></div>'
            # リンク
            result += f"<a href='{url1}' class='btn_03' ontouchstart=''>詳細はこちら</a>"
            result += f"<a href='{url2}' class='btn_03' ontouchstart=''>予約はこちら</a>"

            count += 1

    result += "<form action='/hotel' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    sl(1)
    
    return render_template(result_html, result=result)
