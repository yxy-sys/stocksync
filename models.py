from app import db
from datetime import datetime
from sqlalchemy import func

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to inventory items
    inventory_items = db.relationship('InventoryItem', backref='location', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to inventory items
    inventory_items = db.relationship('InventoryItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.inventory_items)
    
    @property
    def stock_status(self):
        total = self.total_quantity
        if total == 0:
            return 'out-of-stock'
        elif total < 10:  # Low stock threshold
            return 'low-stock'
        else:
            return 'in-stock'

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reserved_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate product-location combinations
    __table_args__ = (db.UniqueConstraint('product_id', 'location_id', name='unique_product_location'),)
    
    def __repr__(self):
        return f'<InventoryItem {self.product.name} at {self.location.name}: {self.quantity}>'
    
    @property
    def available_quantity(self):
        return max(0, self.quantity - self.reserved_quantity)

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'adjustment', 'sync', 'sale', 'purchase'
    quantity_change = db.Column(db.Integer, nullable=False)
    previous_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    inventory_item = db.relationship('InventoryItem', backref='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type}: {self.quantity_change}>'
