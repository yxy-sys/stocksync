import time
from inventory_checker import check_amazon_stock
from ebay_api import update_ebay_inventory

ASIN_EBAY_MAPPING = {
    "B0CXXXXXXX": "123456789012",  # 替换成您的ASIN和eBay Item ID
}

def run_sync_loop():
    while True:
        for asin, item_id in ASIN_EBAY_MAPPING.items():
            stock = check_amazon_stock(asin)
            print(f"{asin} 当前库存状态: {stock}")
            if stock in ["わずか", "1", "0"]:
                update_ebay_inventory(item_id, 0)
            else:
                print(f"{asin} 库存充足，无需操作")
        time.sleep(1800)
