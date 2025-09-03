import pandas as pd
from sqlalchemy import create_engine, text, inspect
from typing import Dict, List, Any
from .base import BaseConnector
from config import Config

class SQLConnector(BaseConnector):
    """SQL database connector for PostgreSQL and MySQL"""
    
    def __init__(self, connection_string: str, name: str, db_type: str):
        super().__init__(connection_string, name)
        self.db_type = db_type
        self.engine = None
        self.inspector = None
    
    def connect(self) -> bool:
        """Connect to SQL database"""
        try:
            self.engine = create_engine(self.connection_string)
            self.inspector = inspect(self.engine)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            self.engine.dispose()
        self.is_connected = False
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.is_connected:
            return {}
        
        schema_info = {}
        
        try:
            tables = self.inspector.get_table_names()
            
            for table in tables:
                columns = self.inspector.get_columns(table)
                primary_keys = self.inspector.get_pk_constraint(table)
                foreign_keys = self.inspector.get_foreign_keys(table)
                
                schema_info[table] = {
                    'columns': [
                        {
                            'name': col['name'],
                            'type': str(col['type']),
                            'nullable': col['nullable'],
                            'default': col.get('default'),
                            'is_sensitive': self._is_sensitive_field(col['name']),
                            'is_person_identifier': self._is_person_identifier(col['name'])
                        }
                        for col in columns
                    ],
                    'primary_keys': primary_keys.get('constrained_columns', []),
                    'foreign_keys': foreign_keys
                }
                
        except Exception as e:
            print(f"Error getting schema: {e}")
        
        return schema_info
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        if not self.is_connected:
            return pd.DataFrame()
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def list_tables(self) -> List[str]:
        """List available tables"""
        if not self.is_connected:
            return []
        
        try:
            return self.inspector.get_table_names()
        except Exception as e:
            print(f"Error listing tables: {e}")
            return []
    
    def _is_sensitive_field(self, column_name: str) -> bool:
        """Check if a column contains sensitive data"""
        column_lower = column_name.lower()
        return any(sensitive in column_lower for sensitive in Config.SENSITIVE_FIELDS)
    
    def _is_person_identifier(self, column_name: str) -> bool:
        """Check if a column can be used to identify persons"""
        column_lower = column_name.lower()
        person_identifiers = ['name', 'first', 'last', 'full', 'person', 'user', 'customer', 'client', 'id']
        return any(identifier in column_lower for identifier in person_identifiers)
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table"""
        if not self.is_connected:
            return 0
        
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            df = self.execute_query(query)
            return df['count'].iloc[0] if not df.empty else 0
        except Exception as e:
            print(f"Error getting row count for {table_name}: {e}")
            return 0
    
    def get_table_sample(self, table_name: str, limit: int = 10) -> pd.DataFrame:
        """Get sample data from a table"""
        if not self.is_connected:
            return pd.DataFrame()
        
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = self.execute_query(query)
            return self.filter_sensitive_fields(df, table_name)
        except Exception as e:
            print(f"Error getting sample from {table_name}: {e}")
            return pd.DataFrame()
