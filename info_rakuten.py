import os, requests, json
# 
from flask import Flask, render_template, request

# 環境変数を使用する際に必須
from dotenv import load_dotenv
from time import sleep as sl
from bs4 import BeautifulSoup



app = Flask(__name__)

root_html = 'index.html'

@app.route('/')
def root():
    return render_template(root_html)
    

@app.route('/search_product', methods=['post'])
def search():
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'

    load_dotenv()

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
    if 'get_code' in rf:
        get_code = rf['get_code']
    else:
        get_code = '0'
    
    if 'get_tax' in rf:
        get_tax = rf['get_tax']
    else:
        get_tax = '0'
    
    if 'get_shop' in rf:
        get_shop = rf['get_shop']
    else:
        get_shop = '0'
    
    if 'get_shop_code' in rf:
        get_shop_code = rf['get_shop_code']
    else:
        get_shop_code = '0'
    
    if 'get_caption' in rf:
        get_caption = rf['get_caption']
    else:
        get_caption = '0'
    
    if 'get_postage' in rf:
        get_postage = rf['get_postage']
    else:
        get_postage = '0'
    
    if 'get_asuraku' in rf:
        get_asuraku = rf['get_asuraku']
    else:
        get_asuraku = '0'

    if 'get_overseas' in rf:
        get_overseas = rf['get_overseas']
    else:
        get_overseas = '0'
    
    if 'get_credit_card' in rf:
        get_credit_card = rf['get_credit_card']
    else:
        get_credit_card = '0'
    
    if 'get_review_count' in rf:
        get_review_count = rf['get_review_count']
    else:
        get_review_count = '0'
    
    if 'get_review_average' in rf:
        get_review_average = rf['get_review_average']
    else:
        get_review_average = '0'

    if 'get_gift_flag' in rf:
        get_gift_flag = rf['get_gift_flag']
    else:
        get_gift_flag = '0'

    # 楽天APIにリクエストするためのパラメーター
    app_id = os.environ['RAKUTEN_APPLICATION_ID']
    affiliate_id = os.environ['RAKUTEN_AFFILIATE_ID']
    
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
            print(img)


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
        
        result += "<div>"

        soup = BeautifulSoup(result, 'html.parser')
        result = soup.prettify()
        

    return render_template('result.html', result=result)
    

@app.route('/search')
def search_again():
    return render_template(root_html)





if __name__ =='__main__':
    app.run(port=9000, debug=True)