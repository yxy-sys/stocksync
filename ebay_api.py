def update_ebay_listing(inventory_data):
    print("🧪 模拟更新 eBay 库存...")
    for asin, qty in inventory_data.items():
        print(f"🔄 更新 {asin} 库存为 {qty}")
