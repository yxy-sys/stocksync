from inventory_checker import check_amazon_inventory
from ebay_api import update_ebay_listing

def run_sync():
    print("🔁 GitHub Actions 启动库存同步")
    inventory = check_amazon_inventory()
    print(f"📦 获取库存结果：{inventory}")
    update_ebay_listing(inventory)
    print("✅ 同步完成，任务结束")

if __name__ == "__main__":
    run_sync()

