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

# ホテル検索画面
# @app.route('/hotel', methods=['get'])
# def hotel():
#     return render_template(hotel_html)

# 



# カラムを作成する This is creating columns of search result.
def create_columns(title, body, sentence_type: int):
    # 普通
    if sentence_type == 0:
        columns = f"<tr><th>{title}</th><td>{body}</td></tr>"
    # まあまあ長い文章
    elif sentence_type == 1:
        columns = f"<tr><th>{title}</th><td class='text-left'>{body}</td></tr>"
    # 長い文章
    elif sentence_type == 2:
        columns = f"<tr><th>{title}</th><td class='text-left text-container'><p class='long-sentence'>{body}</p></td></tr>"
    else:
        raise ValueError('You must set 0, 1 or 2 in sentence_type.')
    return columns



# 商品検索
@app.route('/search_product', methods=['post'])
def product_search():
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'
    rf = request.form
    
    # 検索パラメーター  
    product_search = rf['product']
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
    keyword = product_search
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

    res = requests.get(url, params=params).json()
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
            result += create_columns(title='価格', body=price, sentence_type=0)
            
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
            
            result += "</table>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>商品はこちら</a>"
            count += 1

            sl(1)

        result += "<form action='/product' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
        soup = BeautifulSoup(result, 'html.parser')
        result = soup.prettify()
    
    
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

    res = requests.get(url, params=params).json()
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
            result += create_columns(title='価格', body=price, sentence_type=0)

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
                result += create_columns(title='レビュー数', body=review_count, sentence_type=0)

            # レビュー平均点数
            if get_review_average == '1':
                review_average = item['reviewAverage']
                result += create_columns(title='レビュー平均', body=review_average, sentence_type=0)

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

            result += "</table>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>製品はこちら</a>"
            count += 1

    result += "<form action='/game' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    
    
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
    
    # 
    res = requests.get(url, params=params).json()
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
            result += create_columns(title='価格', body=price, sentence_type=0)
            
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

            result += "</table>"
            result += f"<a href='{url}' class='btn_03' ontouchstart=''>書籍はこちら</a>"
            count += 1

    result += "<form action='/book' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    
    return render_template(result_html, result=result)    


# 宿泊施設検索
# @app.route('/search_hotel', methods=['post'])
# def hotel_search():
#     url = 'https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20220416'
    
#     # HTMLから値を取得
#     rf = request.form

#     # 1, text
#     # ホテル番号
#     hotel_number = rf['hotel_number']
#     if hotel_number is not None and hotel_number.strip() == '':
#         hotel_number = None
#     else:
#         hotel_number = int(hotel_number) 
    
#     # 緯度
#     latitude = rf['latitude']
#     if latitude is not None and latitude.strip() == '':
#         latitude = None
#     else:
#         if '.' in latitude:
#             latitude = float(latitude)
#         else:
#             latitude = int(latitude)
        
#     # 経度
#     longitude = rf['longitude'] 
#     if longitude is not None and longitude.strip() == '':
#         longitude = None
#     else:
#         if '.' in longitude:
#             longitude = float(longitude)
#         else:
#             longitude = int(longitude)
        
#     # 2, select
#     prefectures = rf['prefectures']
#     hotel_sort = rf['hotel_sort']
#     want_hotel = rf['want_hotel']
#     # 3, checkbox


#     # パラメーター 
#     params = {
#         'applicationId': app_id,
#         'affiliateId': affiliate_id,
#         'hotelNo': hotel_number,
#         'latitude': latitude,
#         'longitude': longitude,
#         'largeClassCode': 'japan',
#         'middleClassCode': prefectures,
#         'hits': want_hotel,
#         'sort': hotel_sort,
#         'responseType': 'large',
#         'allReturnFlag': 1
#     }
    
#     # 
#     res = requests.get(url, params=params).json()
#     hotels = res['hotels']
#     count = 1
    
#     # 
#     if not hotels:
#         result = "<h2>ホテル情報がありません</h2>"
#     else:
#         result = "<div class='grid-container'>"
#         for h in hotels:
#             hotel = h['hotel']
            
#             hotel_title = hotel['hotelName']
#             hotel_num = f'商品No.{count}'


#             result += f"<table class='tb01'><h2>{hotel_num}</h2>"

#             result += f"<tr><th>ホテル</th><td>{hotel_title}<td></td/tr>"
        
#         result += "</table>"
#         count += 1


#     result += "<form action='/hotel' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
#     soup = BeautifulSoup(result, 'html.parser')
#     result = soup.prettify()
    
#     return render_template(result_html, result=result) 




