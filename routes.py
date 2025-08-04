from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Product, Location, InventoryItem, InventoryTransaction
from sqlalchemy import or_

@app.route('/')
def index():
    # Get search and filter parameters
    search = request.args.get('search', '')
    location_filter = request.args.get('location', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'name')
    
    # Base query for products with their inventory items
    query = Product.query
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%')
            )
        )
    
    # Get all products
    products = query.all()
    
    # Filter by status if specified
    if status_filter:
        filtered_products = []
        for product in products:
            if product.stock_status == status_filter:
                filtered_products.append(product)
        products = filtered_products
    
    # Sort products
    if sort_by == 'name':
        products.sort(key=lambda x: x.name.lower())
    elif sort_by == 'sku':
        products.sort(key=lambda x: x.sku.lower())
    elif sort_by == 'quantity':
        products.sort(key=lambda x: x.total_quantity, reverse=True)
    
    # Get all locations for filter dropdown
    locations = Location.query.all()
    
    return render_template('index.html', 
                         products=products, 
                         locations=locations,
                         search=search,
                         location_filter=location_filter,
                         status_filter=status_filter,
                         sort_by=sort_by)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        sku = request.form.get('sku')
        description = request.form.get('description')
        price = request.form.get('price')
        
        # Validate required fields
        if not name or not sku:
            flash('Name and SKU are required', 'error')
            return render_template('add_item.html', locations=Location.query.all())
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=sku).first():
            flash('SKU already exists', 'error')
            return render_template('add_item.html', locations=Location.query.all())
        
        try:
            # Create new product
            product = Product(
                name=name,
                sku=sku,
                description=description,
                price=float(price) if price else None
            )
            db.session.add(product)
            db.session.flush()  # Get the product ID
            
            # Add inventory items for each location
            locations = Location.query.all()
            for location in locations:
                quantity = int(request.form.get(f'quantity_{location.id}', 0))
                
                inventory_item = InventoryItem(
                    product_id=product.id,
                    location_id=location.id,
                    quantity=quantity
                )
                db.session.add(inventory_item)
                
                # Create transaction record
                if quantity > 0:
                    transaction = InventoryTransaction(
                        inventory_item_id=inventory_item.id,
                        transaction_type='initial',
                        quantity_change=quantity,
                        previous_quantity=0,
                        new_quantity=quantity,
                        notes='Initial stock entry'
                    )
                    db.session.add(transaction)
            
            db.session.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
    
    locations = Location.query.all()
    return render_template('add_item.html', locations=locations)

@app.route('/product/<int:product_id>/update_quantity', methods=['POST'])
def update_quantity():
    try:
        data = request.get_json()
        inventory_item_id = data.get('inventory_item_id')
        new_quantity = int(data.get('quantity', 0))
        
        inventory_item = InventoryItem.query.get_or_404(inventory_item_id)
        old_quantity = inventory_item.quantity
        
        # Update quantity
        inventory_item.quantity = new_quantity
        
        # Create transaction record
        transaction = InventoryTransaction(
            inventory_item_id=inventory_item.id,
            transaction_type='adjustment',
            quantity_change=new_quantity - old_quantity,
            previous_quantity=old_quantity,
            new_quantity=new_quantity,
            notes='Manual quantity adjustment'
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'total_quantity': inventory_item.product.total_quantity,
            'stock_status': inventory_item.product.stock_status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/location/add', methods=['POST'])
def add_location():
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Location name is required', 'error')
        return redirect(url_for('locations'))
    
    try:
        location = Location(name=name, description=description)
        db.session.add(location)
        db.session.flush()
        
        # Add inventory items for all existing products at this new location
        products = Product.query.all()
        for product in products:
            inventory_item = InventoryItem(
                product_id=product.id,
                location_id=location.id,
                quantity=0
            )
            db.session.add(inventory_item)
        
        db.session.commit()
        flash('Location added successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding location: {str(e)}', 'error')
    
    return redirect(url_for('locations'))

@app.route('/sync_inventory', methods=['POST'])
def sync_inventory():
    """Sync inventory between locations - for demo purposes, this balances stock across locations"""
    try:
        products = Product.query.all()
        
        for product in products:
            # Get all inventory items for this product
            inventory_items = InventoryItem.query.filter_by(product_id=product.id).all()
            
            if len(inventory_items) > 1:
                # Calculate average quantity
                total_quantity = sum(item.quantity for item in inventory_items)
                avg_quantity = total_quantity // len(inventory_items)
                remainder = total_quantity % len(inventory_items)
                
                # Distribute quantities evenly
                for i, item in enumerate(inventory_items):
                    old_quantity = item.quantity
                    new_quantity = avg_quantity + (1 if i < remainder else 0)
                    
                    if old_quantity != new_quantity:
                        item.quantity = new_quantity
                        
                        # Create transaction record
                        transaction = InventoryTransaction(
                            inventory_item_id=item.id,
                            transaction_type='sync',
                            quantity_change=new_quantity - old_quantity,
                            previous_quantity=old_quantity,
                            new_quantity=new_quantity,
                            notes='Inventory synchronization'
                        )
                        db.session.add(transaction)
        
        db.session.commit()
        flash('Inventory synchronized successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error syncing inventory: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # Delete all related inventory items and transactions
        inventory_items = InventoryItem.query.filter_by(product_id=product_id).all()
        for item in inventory_items:
            # Delete transactions first
            InventoryTransaction.query.filter_by(inventory_item_id=item.id).delete()
            db.session.delete(item)
        
        # Delete the product
        db.session.delete(product)
        db.session.commit()
        
        flash('Product deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('index'))
