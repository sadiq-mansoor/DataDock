import pandas as pd
import json
import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Any, Optional
from .base import BaseConnector

class FileConnector(BaseConnector):
    """File connector for CSV, JSON, and XML files"""
    
    def __init__(self, file_path: str, name: str, file_type: str):
        super().__init__(file_path, name)
        self.file_path = file_path
        self.file_type = file_type
        self.data = None
    
    def connect(self) -> bool:
        """Load file data"""
        try:
            if self.file_type == 'csv':
                self.data = pd.read_csv(self.file_path)
            elif self.file_type == 'json':
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    if isinstance(json_data, list):
                        self.data = pd.DataFrame(json_data)
                    else:
                        # Flatten nested JSON
                        self.data = pd.json_normalize(json_data)
            elif self.file_type == 'xml':
                self.data = self._parse_xml()
            else:
                raise ValueError(f"Unsupported file type: {self.file_type}")
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error loading file {self.file_path}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Clear loaded data"""
        self.data = None
        self.is_connected = False
    
    def get_schema(self) -> Dict[str, Any]:
        """Get file schema information"""
        if not self.is_connected or self.data is None:
            return {}
        
        schema_info = {
            'main_table': {
                'columns': [
                    {
                        'name': col,
                        'type': str(self.data[col].dtype),
                        'nullable': bool(self.data[col].isnull().any()),
                        'is_sensitive': self._is_sensitive_field(col),
                        'is_person_identifier': self._is_person_identifier(col)
                    }
                    for col in self.data.columns
                ],
                'row_count': len(self.data)
            }
        }
        
        return schema_info
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute query on file data (limited query support)"""
        if not self.is_connected or self.data is None:
            return pd.DataFrame()
        
        try:
            # Simple query parsing for file data
            query_lower = query.lower()
            
            if 'select' in query_lower and 'from' in query_lower:
                # Extract column names from SELECT clause
                select_part = query[query_lower.find('select')+6:query_lower.find('from')].strip()
                
                if select_part == '*':
                    result_df = self.data.copy()
                else:
                    columns = [col.strip() for col in select_part.split(',')]
                    available_columns = [col for col in columns if col in self.data.columns]
                    result_df = self.data[available_columns]
                
                # Apply WHERE clause if present
                if 'where' in query_lower:
                    where_part = query[query_lower.find('where')+5:].strip()
                    # Simple LIKE condition parsing
                    if 'like' in where_part.lower():
                        for col in self.data.columns:
                            if col.lower() in where_part.lower():
                                # Extract search term
                                search_term = where_part.split("'")[1] if "'" in where_part else where_part.split('"')[1]
                                search_term = search_term.replace('%', '')
                                result_df = result_df[result_df[col].astype(str).str.contains(search_term, case=False, na=False)]
                
                # Apply LIMIT if present
                if 'limit' in query_lower:
                    limit_part = query[query_lower.find('limit')+5:].strip()
                    limit = int(limit_part)
                    result_df = result_df.head(limit)
                
                return result_df
            else:
                return self.data.copy()
                
        except Exception as e:
            print(f"Error executing query on file: {e}")
            return self.data.copy()
    
    def list_tables(self) -> List[str]:
        """List available tables (for files, just return main table)"""
        if self.is_connected:
            return ['main_table']
        return []
    
    def _parse_xml(self) -> pd.DataFrame:
        """Parse XML file and convert to DataFrame"""
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            
            # Find all record elements
            records = []
            for record in root.findall('.//record') or root.findall('.//item') or root.findall('.//row'):
                record_data = {}
                for child in record:
                    record_data[child.tag] = child.text
                records.append(record_data)
            
            if records:
                return pd.DataFrame(records)
            else:
                # If no record structure found, try to parse as flat XML
                data = {}
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        data[elem.tag] = elem.text.strip()
                return pd.DataFrame([data])
                
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return pd.DataFrame()
    
    def _is_sensitive_field(self, column_name: str) -> bool:
        """Check if a column contains sensitive data"""
        column_lower = column_name.lower()
        sensitive_fields = ['password', 'ssn', 'credit_card', 'phone', 'email', 'address', 'salary']
        return any(sensitive in column_lower for sensitive in sensitive_fields)
    
    def _is_person_identifier(self, column_name: str) -> bool:
        """Check if a column can be used to identify persons"""
        column_lower = column_name.lower()
        person_identifiers = ['name', 'first', 'last', 'full', 'person', 'user', 'customer', 'client', 'id', 'customerid', 'customer_id', 'userid', 'user_id']
        return any(identifier in column_lower for identifier in person_identifiers)
    
    def search_person_records(self, identifier: str, tables: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """Search for person-related records in file data"""
        if not self.is_connected or self.data is None:
            return {}
        
        results = {}
        
        # Find person identifier columns
        person_columns = []
        for col in self.data.columns:
            if self._is_person_identifier(col):
                person_columns.append(col)
        
        if person_columns:
            # Search in person identifier columns
            mask = None
            for col in person_columns:
                col_mask = self.data[col].astype(str).str.contains(identifier, case=False, na=False)
                if mask is None:
                    mask = col_mask
                else:
                    mask = mask | col_mask
            
            if mask is not None and mask.any():
                filtered_df = self.data[mask]
                filtered_df = self.filter_sensitive_fields(filtered_df, 'main_table')
                results['main_table'] = filtered_df
        
        return results
