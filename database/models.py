from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # super_admin, admin, user
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")

class DataSource(Base):
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # postgres, mysql, csv, json, xml, logs
    connection_string = Column(Text, nullable=False)
    schema_info = Column(JSON)  # Store schema information
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    schema_mappings = relationship("SchemaMapping", back_populates="data_source")

class SchemaMapping(Base):
    __tablename__ = 'schema_mappings'
    
    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey('data_sources.id'))
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)
    is_sensitive = Column(Boolean, default=False)
    is_person_identifier = Column(Boolean, default=False)  # For person-related searches
    category = Column(String(50))  # For tagging/categorization
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="schema_mappings")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)  # login, search, export, etc.
    details = Column(JSON)  # Store action details
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class SearchSession(Base):
    __tablename__ = 'search_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    search_query = Column(String(500), nullable=False)
    results_count = Column(Integer, default=0)
    data_sources_queried = Column(JSON)  # List of data sources used
    filters_applied = Column(JSON)  # Search filters
    created_at = Column(DateTime, default=datetime.utcnow)

class ExportRecord(Base):
    __tablename__ = 'export_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    search_session_id = Column(Integer, ForeignKey('search_sessions.id'))
    export_type = Column(String(20), nullable=False)  # csv, pdf
    file_path = Column(String(500), nullable=False)
    records_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
