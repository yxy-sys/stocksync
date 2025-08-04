# Overview

This is a Flask-based Inventory Management System designed to track products and inventory levels across multiple locations. The application provides a web interface for managing products, locations, and inventory quantities with features like search, filtering, and real-time quantity updates.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
The application uses Flask as the web framework with SQLAlchemy ORM for database operations. The architecture follows a traditional MVC pattern with clear separation of concerns:

- **Models**: Define database schema using SQLAlchemy with relationships between Products, Locations, and InventoryItems
- **Routes**: Handle HTTP requests and business logic in a dedicated routes module
- **Templates**: Jinja2 templates for server-side rendering with Bootstrap for responsive UI

## Database Design
The system uses a relational database with three core entities:

- **Product**: Stores product information (name, SKU, description, price)
- **Location**: Represents physical locations/warehouses
- **InventoryItem**: Junction table linking products to locations with quantity tracking

The database supports both SQLite (default) and PostgreSQL through environment configuration, with connection pooling and health checks enabled.

## Frontend Architecture
The frontend uses server-side rendering with:

- **Bootstrap 5**: For responsive design and UI components
- **Font Awesome**: For icons and visual elements
- **Vanilla JavaScript**: For interactive features like AJAX quantity updates
- **Template inheritance**: Base template system for consistent layout

## Key Features
- **Multi-location inventory tracking**: Products can exist in multiple locations with separate quantity tracking
- **Real-time updates**: AJAX-powered quantity modifications without page reloads
- **Search and filtering**: Dynamic product filtering by name, SKU, stock status, and location
- **Stock status indicators**: Automatic categorization (in-stock, low-stock, out-of-stock)
- **Responsive design**: Mobile-friendly interface using Bootstrap grid system

## Configuration Management
The application uses environment variables for configuration:

- Database connection strings (supports SQLite and PostgreSQL)
- Session secrets for security
- Debug mode settings

# External Dependencies

## Python Packages
- **Flask**: Web framework for handling HTTP requests and routing
- **Flask-SQLAlchemy**: ORM for database operations and model definitions
- **Werkzeug**: WSGI utilities including proxy fix for deployment
- **SQLAlchemy**: Core database toolkit with relationship management

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive design and components
- **Font Awesome 6.4.0**: Icon library for user interface elements

## Database Support
- **SQLite**: Default embedded database for development
- **PostgreSQL**: Production database option via DATABASE_URL environment variable

## Deployment Considerations
- **ProxyFix**: Configured for reverse proxy deployments
- **Connection pooling**: Enabled with 300-second recycle time
- **Health checks**: Pre-ping enabled for connection reliability