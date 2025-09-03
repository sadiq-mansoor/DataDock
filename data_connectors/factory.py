from typing import Dict, Any
from .sql_connector import SQLConnector
from .file_connector import FileConnector
from config import Config

class ConnectorFactory:
    """Factory class to create appropriate data connectors"""
    
    @staticmethod
    def create_connector(data_source_config: Dict[str, Any]):
        """Create connector based on data source configuration"""
        connector_type = data_source_config.get('type')
        name = data_source_config.get('name')
        
        if connector_type in ['postgres', 'mysql']:
            # SQL database connector
            connection_string = data_source_config.get('connection_string')
            if not connection_string:
                # Build connection string from components
                host = data_source_config.get('host', 'localhost')
                port = data_source_config.get('port', '5432' if connector_type == 'postgres' else '3306')
                database = data_source_config.get('database')
                username = data_source_config.get('username')
                password = data_source_config.get('password')
                
                if connector_type == 'postgres':
                    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                else:  # mysql
                    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            
            return SQLConnector(connection_string, name, connector_type)
        
        elif connector_type in ['csv', 'json', 'xml']:
            # File connector
            file_path = data_source_config.get('file_path')
            return FileConnector(file_path, name, connector_type)
        
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")
    
    @staticmethod
    def test_connection(data_source_config: Dict[str, Any]) -> tuple[bool, str]:
        """Test connection to data source"""
        try:
            connector = ConnectorFactory.create_connector(data_source_config)
            success = connector.connect()
            connector.disconnect()
            
            if success:
                return True, "Connection successful"
            else:
                return False, "Failed to connect"
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    @staticmethod
    def get_supported_types() -> Dict[str, str]:
        """Get supported connector types and their descriptions"""
        return {
            'postgres': 'PostgreSQL Database',
            'mysql': 'MySQL Database',
            'csv': 'CSV File',
            'json': 'JSON File',
            'xml': 'XML File'
        }
