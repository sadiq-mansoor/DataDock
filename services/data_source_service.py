import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from database.models import DataSource, SchemaMapping
from database.connection import get_db
from data_connectors.factory import ConnectorFactory
from utils.audit import log_action
from config import Config
import numpy as np

class DataSourceService:
    """Service for managing data sources"""
    
    @staticmethod
    def _ensure_json_serializable(obj):
        """Ensure object is JSON serializable by converting numpy types"""
        if isinstance(obj, dict):
            return {key: DataSourceService._ensure_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [DataSourceService._ensure_json_serializable(item) for item in obj]
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    @staticmethod
    def create_data_source(data_source_config: Dict[str, Any], created_by: int) -> tuple[bool, str]:
        """Create a new data source"""
        db = next(get_db())
        try:
            # Test connection first
            success, message = ConnectorFactory.test_connection(data_source_config)
            if not success:
                return False, f"Connection test failed: {message}"
            
            # Create connector to get schema
            connector = ConnectorFactory.create_connector(data_source_config)
            connector.connect()
            schema_info = connector.get_schema()
            connector.disconnect()
            
            # Ensure schema_info is JSON serializable
            schema_info = DataSourceService._ensure_json_serializable(schema_info)
            
            # Create data source record
            data_source = DataSource(
                name=data_source_config['name'],
                type=data_source_config['type'],
                connection_string=json.dumps(data_source_config),
                schema_info=schema_info,
                created_by=created_by,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            db.add(data_source)
            db.commit()
            
            # Create schema mappings
            DataSourceService._create_schema_mappings(db, data_source.id, schema_info)
            
            # Log action
            log_action(created_by, "create_data_source", {
                "data_source_name": data_source_config['name'],
                "data_source_type": data_source_config['type']
            })
            
            return True, "Data source created successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating data source: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def get_all_data_sources() -> List[DataSource]:
        """Get all active data sources"""
        db = next(get_db())
        try:
            return db.query(DataSource).filter(DataSource.is_active == True).all()
        finally:
            db.close()
    
    @staticmethod
    def get_data_source_by_id(data_source_id: int) -> Optional[DataSource]:
        """Get data source by ID"""
        db = next(get_db())
        try:
            return db.query(DataSource).filter(DataSource.id == data_source_id).first()
        finally:
            db.close()
    
    @staticmethod
    def update_data_source(data_source_id: int, updates: Dict[str, Any], updated_by: int) -> tuple[bool, str]:
        """Update data source"""
        db = next(get_db())
        try:
            data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
            if not data_source:
                return False, "Data source not found"
            
            # Update fields
            for key, value in updates.items():
                if hasattr(data_source, key):
                    setattr(data_source, key, value)
            
            data_source.last_updated = datetime.utcnow()
            db.commit()
            
            # Log action
            log_action(updated_by, "update_data_source", {
                "data_source_id": data_source_id,
                "updates": updates
            })
            
            return True, "Data source updated successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating data source: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def delete_data_source(data_source_id: int, deleted_by: int) -> tuple[bool, str]:
        """Delete data source (soft delete)"""
        db = next(get_db())
        try:
            data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
            if not data_source:
                return False, "Data source not found"
            
            data_source.is_active = False
            db.commit()
            
            # Log action
            log_action(deleted_by, "delete_data_source", {
                "data_source_id": data_source_id,
                "data_source_name": data_source.name
            })
            
            return True, "Data source deleted successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error deleting data source: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def test_data_source_connection(data_source_id: int) -> tuple[bool, str]:
        """Test connection to data source"""
        data_source = DataSourceService.get_data_source_by_id(data_source_id)
        if not data_source:
            return False, "Data source not found"
        
        try:
            config = json.loads(data_source.connection_string)
            return ConnectorFactory.test_connection(config)
        except Exception as e:
            return False, f"Error testing connection: {str(e)}"
    
    @staticmethod
    def refresh_schema(data_source_id: int, refreshed_by: int) -> tuple[bool, str]:
        """Refresh schema information for data source"""
        data_source = DataSourceService.get_data_source_by_id(data_source_id)
        if not data_source:
            return False, "Data source not found"
        
        try:
            config = json.loads(data_source.connection_string)
            connector = ConnectorFactory.create_connector(config)
            connector.connect()
            new_schema = connector.get_schema()
            connector.disconnect()
            
            # Ensure schema_info is JSON serializable
            new_schema = DataSourceService._ensure_json_serializable(new_schema)
            
            # Update schema
            db = next(get_db())
            data_source.schema_info = new_schema
            data_source.last_updated = datetime.utcnow()
            db.commit()
            
            # Update schema mappings
            DataSourceService._create_schema_mappings(db, data_source_id, new_schema)
            
            # Log action
            log_action(refreshed_by, "refresh_schema", {
                "data_source_id": data_source_id,
                "data_source_name": data_source.name
            })
            
            return True, "Schema refreshed successfully"
            
        except Exception as e:
            return False, f"Error refreshing schema: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def _create_schema_mappings(db, data_source_id: int, schema_info: Dict[str, Any]):
        """Create schema mappings for data source"""
        # Remove existing mappings
        db.query(SchemaMapping).filter(SchemaMapping.data_source_id == data_source_id).delete()
        
        # Create new mappings
        for table_name, table_info in schema_info.items():
            for column_info in table_info.get('columns', []):
                mapping = SchemaMapping(
                    data_source_id=data_source_id,
                    table_name=table_name,
                    column_name=column_info['name'],
                    data_type=column_info['type'],
                    is_sensitive=column_info.get('is_sensitive', False),
                    is_person_identifier=column_info.get('is_person_identifier', False),
                    category=column_info.get('category'),
                    created_at=datetime.utcnow()
                )
                db.add(mapping)
        
        db.commit()
    
    @staticmethod
    def get_schema_mappings(data_source_id: int) -> List[SchemaMapping]:
        """Get schema mappings for data source"""
        db = next(get_db())
        try:
            return db.query(SchemaMapping).filter(SchemaMapping.data_source_id == data_source_id).all()
        finally:
            db.close()
    
    @staticmethod
    def update_schema_mapping(mapping_id: int, updates: Dict[str, Any], updated_by: int) -> tuple[bool, str]:
        """Update schema mapping"""
        db = next(get_db())
        try:
            mapping = db.query(SchemaMapping).filter(SchemaMapping.id == mapping_id).first()
            if not mapping:
                return False, "Schema mapping not found"
            
            # Update fields
            for key, value in updates.items():
                if hasattr(mapping, key):
                    setattr(mapping, key, value)
            
            db.commit()
            
            # Log action
            log_action(updated_by, "update_schema_mapping", {
                "mapping_id": mapping_id,
                "updates": updates
            })
            
            return True, "Schema mapping updated successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating schema mapping: {str(e)}"
        finally:
            db.close()
