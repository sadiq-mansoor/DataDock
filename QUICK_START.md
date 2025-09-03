# Quick Start Guide - Data Retrieval System

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run app.py
```

### Step 3: Login
- Open your browser to `http://localhost:8501`
- Use default admin credentials:
  - **Username**: `admin`
  - **Password**: `admin123`

### Step 4: Add Sample Data Sources
1. Navigate to "Data Sources" in the sidebar
2. Click "Add New Data Source"
3. Add the sample CSV file:
   - **Name**: `Sample Employees`
   - **Type**: `csv`
   - **File Path**: `sample_data/employees.csv`
4. Click "Add Data Source"

### Step 5: Search for Data
1. Go to "Global Search"
2. Enter a name like "John" or "Sarah"
3. View results and export to CSV/PDF

## 🧪 Test the System

### Run Installation Test
```bash
python test_installation.py
```

### Test with Sample Data
1. Add both sample files as data sources:
   - `sample_data/employees.csv`
   - `sample_data/customers.json`
2. Search for "Johnson" to find records across both sources
3. Export results to see the full functionality

## 🔧 Quick Configuration

### Add Your Own Data Sources

#### CSV File
```json
{
    "name": "My Data",
    "type": "csv",
    "file_path": "C:/path/to/your/file.csv"
}
```

#### PostgreSQL Database
```json
{
    "name": "My Database",
    "type": "postgres",
    "host": "localhost",
    "port": "5432",
    "database": "mydb",
    "username": "postgres",
    "password": "password"
}
```

## 📋 Default Users

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| Super Admin | `admin` | `admin123` | Full access |
| Demo User | `demo` | `demo123` | Search only |

## 🆘 Need Help?

### Common Issues
1. **Import errors**: Run `pip install -r requirements.txt`
2. **Port conflicts**: Change port with `streamlit run app.py --server.port 8502`
3. **File not found**: Use absolute paths for data sources

### Quick Commands
```bash
# Test installation
python test_installation.py

# Start with custom port
streamlit run app.py --server.port 8502

# View logs
tail -f logs/audit.log
```

## 🎯 Next Steps

1. **Add your data sources** in the Data Sources section
2. **Configure sensitive fields** in `config.py` if needed
3. **Create user accounts** for your team
4. **Set up regular backups** of the database and logs
5. **Review audit logs** for compliance

---

**Ready to go!** The system is now fully functional with sample data. Add your own data sources and start searching!
