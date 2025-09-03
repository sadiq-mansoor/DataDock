# Data Retrieval System

A comprehensive offline data retrieval system built with Python and Streamlit, designed for secure, role-based access to multiple data sources with full audit logging.

## 🚀 Features

### Core Functionality
- **Multi-Data Source Support**: PostgreSQL, MySQL, CSV, JSON, XML files
- **Global Search**: Search across all data sources simultaneously
- **Person-Based Retrieval**: Find all records related to a specific person
- **Schema Management**: Auto-detect and manage data schemas
- **Sensitive Data Protection**: Automatic filtering of sensitive fields

### Security & Access Control
- **Role-Based Access**: Super Admin, Admin, and User roles
- **Complete Offline System**: No internet connectivity required
- **Audit Logging**: Comprehensive logging of all user actions
- **Immutable Logs**: Local file-based audit trail

### Export & Reporting
- **CSV Export**: Export search results to CSV format
- **PDF Export**: Generate detailed PDF reports
- **Provenance Tracking**: Track data lineage and sources
- **Search History**: Maintain search session history

## 📋 System Requirements

- Python 3.10 or higher
- Windows 10/11 (tested on Windows 10.0.22000)
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space

## 🛠️ Installation

### 1. Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd data-retrieval-system

# Or download and extract the ZIP file
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root (optional):
```env
# Database configurations (optional - defaults will be used)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=data_retrieval
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=data_retrieval
MYSQL_USER=root
MYSQL_PASSWORD=password
```

### 4. Run the Application
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 👤 Default Users

### Super Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Capabilities**: Full system access, user management, data source management

### Demo User Account
- **Username**: `demo`
- **Password**: `demo123`
- **Capabilities**: Search and export data (limited access)

> **Note**: The demo user will be created automatically when you click "Create Demo Account" on the login page.

## 📊 System Architecture

```
Data Retrieval System
├── Frontend (Streamlit)
│   ├── Login/Authentication
│   ├── Dashboard
│   ├── Global Search
│   ├── Data Source Management
│   ├── Schema Management
│   ├── Audit Logs
│   └── User Management
├── Backend Services
│   ├── Authentication Service
│   ├── Data Source Service
│   ├── Search Service
│   ├── Export Service
│   └── Audit Service
├── Data Connectors
│   ├── SQL Connectors (PostgreSQL, MySQL)
│   ├── File Connectors (CSV, JSON, XML)
│   └── Base Connector Interface
└── Database Layer
    ├── SQLite (Application Metadata)
    └── External Data Sources
```

## 🔧 Configuration

### Data Source Types

#### PostgreSQL Database
```json
{
    "name": "My PostgreSQL DB",
    "type": "postgres",
    "host": "localhost",
    "port": "5432",
    "database": "mydb",
    "username": "postgres",
    "password": "password"
}
```

#### MySQL Database
```json
{
    "name": "My MySQL DB",
    "type": "mysql",
    "host": "localhost",
    "port": "3306",
    "database": "mydb",
    "username": "root",
    "password": "password"
}
```

#### File Sources
```json
{
    "name": "My CSV File",
    "type": "csv",
    "file_path": "C:/path/to/your/file.csv"
}
```

### Sensitive Fields Configuration
The system automatically detects and filters sensitive fields. You can configure this in `config.py`:

```python
SENSITIVE_FIELDS = [
    'password', 'ssn', 'credit_card', 'phone', 'email',
    'address', 'salary', 'medical_record', 'bank_account'
]
```

## 🔍 Usage Guide

### 1. Login
- Open the application in your browser
- Use the default admin credentials or create a demo account
- The system will automatically create necessary directories and database tables

### 2. Add Data Sources (Admin/Super Admin)
- Navigate to "Data Sources" in the sidebar
- Click "Add New Data Source"
- Select the data source type and provide connection details
- Test the connection before saving

### 3. Search for Data
- Use the "Global Search" feature to search across all data sources
- Enter a person's name, ID, or other identifier
- View results grouped by person and data source
- Export results to CSV or PDF

### 4. Manage Schemas (Admin/Super Admin)
- Navigate to "Schema Management"
- Select a data source to view its schema
- Refresh schemas when data structures change
- Configure sensitive field detection

### 5. Monitor Activity (Admin/Super Admin)
- View audit logs in the "Audit Logs" section
- Export audit logs for compliance purposes
- Monitor user activities and system usage

## 📁 Directory Structure

```
data-retrieval-system/
├── app.py                          # Main application file
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── project_plan.text              # Original project plan
├── database/                       # Database layer
│   ├── __init__.py
│   ├── connection.py              # Database connection management
│   └── models.py                  # Database models
├── data_connectors/               # Data source connectors
│   ├── __init__.py
│   ├── base.py                    # Base connector interface
│   ├── factory.py                 # Connector factory
│   ├── sql_connector.py           # SQL database connectors
│   └── file_connector.py          # File connectors
├── services/                      # Business logic services
│   ├── __init__.py
│   ├── data_source_service.py     # Data source management
│   ├── search_service.py          # Search functionality
│   └── export_service.py          # Export functionality
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── auth.py                    # Authentication utilities
│   └── audit.py                   # Audit logging
├── pages/                         # Streamlit pages
│   ├── __init__.py
│   ├── login.py                   # Login page
│   └── dashboard.py               # Main dashboard
├── data/                          # Application data (auto-created)
├── logs/                          # Audit logs (auto-created)
├── exports/                       # Exported files (auto-created)
└── schemas/                       # Schema files (auto-created)
```

## 🔒 Security Features

### Access Control
- **Super Admin**: Full system access, user management, data source management
- **Admin**: Data source management, audit log access, limited user management
- **User**: Search and export capabilities only

### Data Protection
- Automatic filtering of sensitive fields
- No internet connectivity required
- Local audit logging with immutable records
- Password hashing with bcrypt

### Audit Trail
- All user actions are logged with timestamps
- User identification and IP tracking
- Export activity monitoring
- Immutable log files stored locally

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
- Ensure database servers are running
- Verify connection credentials
- Check firewall settings for database ports

#### 2. File Access Issues
- Ensure file paths are correct and accessible
- Check file permissions
- Use absolute paths for file data sources

#### 3. Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.10+ required)
- Ensure all files are in the correct directory structure

#### 4. Streamlit Issues
- Clear browser cache
- Restart the Streamlit application
- Check for port conflicts (default: 8501)

### Getting Help
1. Check the audit logs for error details
2. Verify configuration settings in `config.py`
3. Ensure all required directories exist
4. Check database connectivity

## 📈 Performance Optimization

### For Large Datasets
- Use database indexes on search columns
- Implement pagination for large result sets
- Consider data source-specific optimizations

### System Resources
- Monitor memory usage with large exports
- Use appropriate database connection pooling
- Implement result caching for frequent searches

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor audit log file sizes
- Clean up old export files
- Update sensitive field configurations as needed
- Review and rotate user passwords

### Backup Recommendations
- Backup the SQLite database (`data/data_retrieval.db`)
- Backup audit log files (`logs/audit.log`)
- Backup configuration files
- Document data source configurations

## 📄 License

This project is designed for internal organizational use. Please ensure compliance with your organization's data handling policies and regulations.

## 🤝 Contributing

For internal development:
1. Follow the existing code structure
2. Add appropriate audit logging
3. Test with multiple data source types
4. Update documentation for new features

---

**Data Retrieval System v1.0** - Complete offline data retrieval solution with comprehensive security and audit capabilities.
