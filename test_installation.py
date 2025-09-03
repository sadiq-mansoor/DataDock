#!/usr/bin/env python3
"""
Test script to verify Data Retrieval System installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt imported successfully")
    except ImportError as e:
        print(f"❌ bcrypt import failed: {e}")
        return False
    
    try:
        import reportlab
        print("✅ ReportLab imported successfully")
    except ImportError as e:
        print(f"❌ ReportLab import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        "app.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "database/__init__.py",
        "database/connection.py",
        "database/models.py",
        "data_connectors/__init__.py",
        "data_connectors/base.py",
        "data_connectors/factory.py",
        "data_connectors/sql_connector.py",
        "data_connectors/file_connector.py",
        "services/__init__.py",
        "services/data_source_service.py",
        "services/search_service.py",
        "services/export_service.py",
        "utils/__init__.py",
        "utils/auth.py",
        "utils/audit.py",
        "pages/__init__.py",
        "pages/login.py",
        "pages/dashboard.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from database.connection import db_manager
        db_manager.create_tables()
        print("✅ Database connection and table creation successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("✅ Configuration loaded successfully")
        print(f"   - Data directory: {Config.DATA_DIR}")
        print(f"   - Logs directory: {Config.LOGS_DIR}")
        print(f"   - Exports directory: {Config.EXPORTS_DIR}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_sample_data():
    """Test sample data files"""
    print("\nTesting sample data...")
    
    sample_files = [
        "sample_data/employees.csv",
        "sample_data/customers.json"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️  {file_path} (optional)")
    
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("Data Retrieval System - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Project Structure Test", test_project_structure),
        ("Database Connection Test", test_database_connection),
        ("Configuration Test", test_configuration),
        ("Sample Data Test", test_sample_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the application, run:")
        print("   streamlit run app.py")
        print("\nOr use the provided scripts:")
        print("   run.bat (Windows)")
        print("   run.ps1 (PowerShell)")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Ensure Python 3.10+ is installed")
        print("3. Check file permissions")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
