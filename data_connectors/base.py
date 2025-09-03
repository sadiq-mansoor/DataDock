from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any, Optional
from config import Config

class BaseConnector(ABC):
    """Base class for all data connectors"""
    
    def __init__(self, connection_string: str, name: str):
        self.connection_string = connection_string
        self.name = name
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to data source"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from data source"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get schema information"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute query and return results as DataFrame"""
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        """List available tables"""
        pass
    
    def filter_sensitive_fields(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Filter out sensitive fields based on configuration"""
        if df.empty:
            return df
        
        # Get sensitive fields for this table
        sensitive_fields = self._get_sensitive_fields(table_name)
        
        # Remove sensitive columns
        columns_to_remove = []
        for col in df.columns:
            col_lower = col.lower()
            if any(sensitive in col_lower for sensitive in Config.SENSITIVE_FIELDS):
                columns_to_remove.append(col)
            elif any(sensitive in col_lower for sensitive in sensitive_fields):
                columns_to_remove.append(col)
        
        if columns_to_remove:
            df = df.drop(columns=columns_to_remove)
        
        return df
    
    def _get_sensitive_fields(self, table_name: str) -> List[str]:
        """Get sensitive fields for a specific table"""
        # This can be overridden by subclasses to provide table-specific sensitive fields
        return []
    
    def search_person_records(self, identifier: str, tables: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """Search for person-related records across tables"""
        results = {}
        
        if tables is None:
            tables = self.list_tables()
        
        for table in tables:
            try:
                # Search in person identifier columns
                person_columns = self._get_person_identifier_columns(table)
                
                if person_columns:
                    query_parts = []
                    for col in person_columns:
                        query_parts.append(f"LOWER({col}) LIKE LOWER('%{identifier}%')")
                    
                    where_clause = " OR ".join(query_parts)
                    query = f"SELECT * FROM {table} WHERE {where_clause}"
                    
                    df = self.execute_query(query)
                    if not df.empty:
                        # Filter sensitive fields
                        df = self.filter_sensitive_fields(df, table)
                        results[table] = df
                        
            except Exception as e:
                print(f"Error searching table {table}: {e}")
                continue
        
        return results
    
    def _get_person_identifier_columns(self, table_name: str) -> List[str]:
        """Get columns that can be used to identify persons"""
        # This can be overridden by subclasses to provide table-specific person identifiers
        schema = self.get_schema()
        if table_name in schema:
            columns = schema[table_name].get('columns', [])
            person_columns = []
            
            for col in columns:
                col_lower = col['name'].lower()
                if any(identifier in col_lower for identifier in ['name', 'first', 'last', 'full', 'person', 'user', 'customer', 'client']):
                    person_columns.append(col['name'])
            
            return person_columns
        
        return []
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
