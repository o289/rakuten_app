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
result_html = 'result.html'

# class

#環境変数 
load_dotenv()

app_id = os.environ['RAKUTEN_APPLICATION_ID']
affiliate_id = os.environ['RAKUTEN_AFFILIATE_ID']

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






# 商品検索
@app.route('/search_product', methods=['post'])
def product_search():
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'

    # 検索パラメーター
    rf = request.form
    product_search = rf['product']
    want_product_length_search = int(rf['want_product'])
    max_price_search = int(rf['max_price'])
    min_price_search = int(rf['min_price'])
    product_sort = rf['product_sort']
    postage_sort = int(rf['postage'])
    
    purchase_type = int(rf['purchase_type'])
    if purchase_type >= 3:
        ValueError('Invalid value.')

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
            # 画像
            images = item['mediumImageUrls']
            image = images[0]
            img = image.get('imageUrl')

            product_num = f'商品No.{count}'
            
            result += f"<table class='tb01'><h2>{product_num}</h2>"
            result += f"<img src='{img}' alt='{product_num}' class='image'>"
            # 商品名 
            name = item['itemName']
            result += f"<tr><th>商品名</th><td class='text-left'><a href='{url}'>{name}</a></td></tr>"
            


            # 価格
            price = item['itemPrice']
            result += f"<tr><th>価格</th><td>{price}円</td></tr>"
            
            # 税
            if get_tax == '1':
                # There is a if tax.
                tax_flag = item['taxFlag']
                if tax_flag == 0:
                    tax = "税込価格"
                elif tax_flag == 1:
                    tax = "税別価格"
                else: 
                    ValueError('Invalid value.')
                result += f"<tr><th>税</th><td>{tax}</td></tr>"

            # レビュー数
            if get_review_count == '1':
                review_count = item['reviewCount']
                result += f"<tr><th>レビュー数</th><td>{review_count}件</td></tr>"

            # レビュー平均点数
            if get_review_average == '1':
                review_average = item['reviewAverage']
                result += f"<tr><th>レビュー平均</th><td>{review_average}点</td></tr>"

            # 商品コード
            if get_code == '1':
                code = item['itemCode']
                result += f"<tr><th>商品コード</th><td>{code}</td></tr>"
            # 販売店
            if get_shop == '1':
                shop = item['shopName']
                result += f"<tr><th>販売店</th><td>{shop}</td></tr>"

            # 販売店コード
            if get_shop_code == '1':
                shop_code = item['shopCode']
                result += f"<tr><th>販売店コード</th><td>{shop_code}</td></tr>"

            # 送料
            if get_postage == '1':
                # There is a if postage.
                postage_flag = item['postageFlag']
                if postage_flag == 0:
                    postage = "送料込/送料無料"
                elif postage_flag == 1:
                    postage = "送料別"
                else: 
                    ValueError('Invalid value.')
                result += f"<tr><th>送料</th><td>{postage}</td></tr>"

            # 翌日配送
            if get_asuraku == '1':
                # There is a if asuraku.
                asuraku_flag = item['asurakuFlag']
                if asuraku_flag == 0:
                    asuraku = '不可'
                    result += f"<tr><th>翌日配送</th><td>{asuraku}</td></tr>"

                elif asuraku_flag == 1:
                    asuraku = '可'
                    asuraku_area = item['asurakuArea']
                    asuraku_closing_time = item['asurakuClosingTime']
                    asuraku_area = asuraku_area.replace('/', '|')
                    asuraku_data = f"<td class='text-left'>{asuraku_area}</td>"

                    result += f"<tr><th>翌日配送</th><td>{asuraku}</td></tr>"
                    result += f"<tr><th>翌日配送可能地域</th>{asuraku_data}</tr>"
                    result += f"<tr><th>翌日発送締め切り</th><td>{asuraku_closing_time}</td/tr>"

                else:
                    ValueError('Invalid value.')

            # 海外配送
            if get_overseas == '1':
                ship_overseas_flag = item['shipOverseasFlag']
                if ship_overseas_flag == 0:
                    ship_overseas = '不可'
                    result += f"<tr><th>海外配送</th><td>{ship_overseas}</td></tr>"
                
                elif ship_overseas_flag == 1:
                    ship_overseas = '可'
                    ship_overseas_area = item['shipOverseasArea']
                    ship_overseas_area = ship_overseas_area.replace('/', '|')
                    ship_overseas_data = f"<td class='text-left'>{ship_overseas_area}</td>"
                    
                    result += f"<tr><th>海外配送</th><td>{ship_overseas}</td></tr>"
                    result += f"<tr><th>海外配送可能地域</th>{ship_overseas_data}</tr>"
                    
                else:
                    ValueError('Invalid value.')

            # クレジットカード
            if get_credit_card == '1':
                credit_card_flag = item['creditCardFlag']
                if credit_card_flag == 0:
                    credit_card = '不可'
                elif credit_card_flag == 1:
                    credit_card = '可'
                else:
                    ValueError('Invalid value.')

                result += f"<tr><th>カード</th><td>{credit_card}</td></tr>"

            # ギフト包装
            if get_gift_flag == '1':
                gift_flag = item['giftFlag']
                if gift_flag == 0:
                    gift = '不可'
                elif gift_flag == 1:
                    gift = '可'
                else:
                    ValueError('Invalid value.')

                result += f"<tr><th>ギフト包装</th><td>{gift}</td></tr>"

            # 商品説明
            if get_caption == '1':
                caption = item['itemCaption']
                result += f"<tr><th>商品説明</th><td class='text-left text-container'><p class='long-sentence'>{caption}</p></td></tr>"

            result += "</table>"
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
    game_title_display_type = int(rf['game_title_display_type'])
    
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

            # 画像
            img = item['smallImageUrl']
            
            # URL
            url = item['affiliateUrl']

            result += f"<table class='tb01'><h2>{product_num}</h2>"
            result += f"<img src='{img}' alt='{product_num}' class='image'>"
            
            # ゲームタイトル（通常）と（カタカナ）
            template_of_game = '<th>タイトル</th>'
            if game_title_display_type == 0:
                game_title = item['title']
                
            elif game_title_display_type == 1:
                game_title = item['titleKana']
            else:
                ValueError("This value is nothing.")
            result += f"<tr>{template_of_game}<td><a href='{url}'>{game_title}</a></td></tr>"

            # 価格
            price = item['itemPrice']
            result += f"<tr><th>価格</th><td>{price}円</td></tr>"
            
            # ハード
            if get_hardware == '1':
                hardware = item['hardware']
                result += f"<tr><th>対応機種</th><td>{hardware}</td></tr>"

            # JANコード
            if get_jan_code == '1':
                jan_code = item['jan']
                result += f"<tr><th>JANコード</th><td>{jan_code}</td></tr>"
            
            # 発売日
            if get_sales_date == '1':
                sales_date = item['salesDate']
                result += f"<tr><th>発売日</th><td>{sales_date}</td></tr>"
            # 
            if get_limited == '1':
                limited_type = item['limitedFlag']
                if limited_type == 0:
                    limited = '通常販売'
                elif limited_type == 1:
                    limited = '限定販売'
                else: 
                    ValueError('This value is nothing.')
                result += f"<tr><th>発売種別</th><td>{limited}</td></tr>"
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
                    ValueError('This value is nothing.')
                result += f"<tr><th>在庫状況</th><td>{availability}</td></tr>"

            # 送料
            if get_postage == '1':
                # There is a if postage.
                postage_flag = item['postageFlag']
                if postage_flag == 0:
                    postage = "送料込/送料無料"
                elif postage_flag == 1:
                    postage = "宅配送料無料"
                elif postage_flag == 2:
                    postage = "完全送料無料"
                else: 
                    ValueError('Invalid value.')
                result += f"<tr><th>送料</th><td>{postage}</td></tr>"
            
            # レビュー数
            if get_review_count == '1':
                review_count = item['reviewCount']
                result += f"<tr><th>レビュー数</th><td>{review_count}件</td></tr>"

            # レビュー平均点数
            if get_review_average == '1':
                review_average = item['reviewAverage']
                result += f"<tr><th>レビュー平均</th><td>{review_average}点</td></tr>"
            
            # 販売元
            if get_label == '1':
                label = item['label']
                result += f"<tr><th>販売元</th><td>{label}</td></tr>"
            
            # 販売店コード
            if get_maker_code == '1':
                maker_code = item['makerCode']
                result += f"<tr><th>販売店コード</th><td>{maker_code}</td></tr>"
            
            # 商品説明
            if get_item_caption == '1':
                caption = item['itemCaption']
                result += f"<tr><th>商品説明</th><td class='text-left text-container'><p class='long-sentence'>{caption}</p></td></tr>"


            result += "</table>"
            count += 1

    result += "<form action='/game' method='get' class='research'><input type='submit' value='再検索' class='submit btn--radius'></form>"
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.prettify()
    
    return render_template(result_html, result=result)    










