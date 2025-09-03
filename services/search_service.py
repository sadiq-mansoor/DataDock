import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from database.models import SearchSession
from database.connection import get_db
from data_connectors.factory import ConnectorFactory
from services.data_source_service import DataSourceService
from utils.audit import log_action
from config import Config

class SearchService:
    """Service for handling searches across data sources"""
    
    @staticmethod
    def global_search(identifier: str, user_id: int, data_sources: Optional[List[int]] = None) -> Dict[str, Any]:
        """Perform global search across all data sources"""
        try:
            # Get all active data sources
            if data_sources is None:
                data_sources = [ds.id for ds in DataSourceService.get_all_data_sources()]
            
            all_results = {}
            total_records = 0
            data_sources_queried = []
            
            for data_source_id in data_sources:
                try:
                    data_source = DataSourceService.get_data_source_by_id(data_source_id)
                    if not data_source:
                        continue
                    
                    # Create connector
                    config = json.loads(data_source.connection_string)
                    connector = ConnectorFactory.create_connector(config)
                    
                    if connector.connect():
                        # Search for person records
                        results = connector.search_person_records(identifier)
                        connector.disconnect()
                        
                        if results:
                            all_results[data_source.name] = results
                            data_sources_queried.append(data_source.name)
                            
                            # Count total records
                            for table_results in results.values():
                                total_records += len(table_results)
                
                except Exception as e:
                    print(f"Error searching data source {data_source_id}: {e}")
                    continue
            
            # Create search session (don't fail if this doesn't work)
            search_session = None
            try:
                search_session = SearchService._create_search_session(
                    user_id, identifier, total_records, data_sources_queried
                )
            except Exception as e:
                print(f"Warning: Could not create search session: {e}")
            
            # Log search action
            try:
                log_action(user_id, "global_search", {
                    "identifier": identifier,
                    "results_count": total_records,
                    "data_sources_queried": data_sources_queried,
                    "search_session_id": search_session.id if search_session else None
                })
            except Exception as e:
                print(f"Warning: Could not log search action: {e}")
            
            return {
                "results": all_results,
                "total_records": total_records,
                "data_sources_queried": data_sources_queried,
                "search_session_id": search_session.id if search_session else None
            }
            
        except Exception as e:
            print(f"Error in global search: {e}")
            return {
                "results": {},
                "total_records": 0,
                "data_sources_queried": [],
                "error": str(e)
            }
    
    @staticmethod
    def search_by_data_source(data_source_id: int, identifier: str, user_id: int) -> Dict[str, Any]:
        """Search in a specific data source"""
        try:
            data_source = DataSourceService.get_data_source_by_id(data_source_id)
            if not data_source:
                return {"error": "Data source not found"}
            
            # Create connector
            config = json.loads(data_source.connection_string)
            connector = ConnectorFactory.create_connector(config)
            
            if not connector.connect():
                return {"error": "Failed to connect to data source"}
            
            # Search for person records
            results = connector.search_person_records(identifier)
            connector.disconnect()
            
            total_records = sum(len(df) for df in results.values())
            
            # Log search action
            log_action(user_id, "data_source_search", {
                "data_source_id": data_source_id,
                "data_source_name": data_source.name,
                "identifier": identifier,
                "results_count": total_records
            })
            
            return {
                "results": results,
                "total_records": total_records,
                "data_source_name": data_source.name
            }
            
        except Exception as e:
            print(f"Error searching data source: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def execute_custom_query(data_source_id: int, query: str, user_id: int) -> Dict[str, Any]:
        """Execute custom query on data source"""
        try:
            data_source = DataSourceService.get_data_source_by_id(data_source_id)
            if not data_source:
                return {"error": "Data source not found"}
            
            # Create connector
            config = json.loads(data_source.connection_string)
            connector = ConnectorFactory.create_connector(config)
            
            if not connector.connect():
                return {"error": "Failed to connect to data source"}
            
            # Execute query
            results = connector.execute_query(query)
            connector.disconnect()
            
            # Filter sensitive fields
            results = connector.filter_sensitive_fields(results, "custom_query")
            
            # Log query execution
            log_action(user_id, "custom_query", {
                "data_source_id": data_source_id,
                "data_source_name": data_source.name,
                "query": query,
                "results_count": len(results)
            })
            
            return {
                "results": results,
                "total_records": len(results),
                "data_source_name": data_source.name
            }
            
        except Exception as e:
            print(f"Error executing custom query: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_search_history(user_id: int, limit: int = 50) -> List[SearchSession]:
        """Get search history for user"""
        db = next(get_db())
        try:
            return db.query(SearchSession).filter(
                SearchSession.user_id == user_id
            ).order_by(SearchSession.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    @staticmethod
    def _create_search_session(user_id: int, query: str, results_count: int, data_sources_queried: List[str]) -> Optional[SearchSession]:
        """Create search session record"""
        try:
            db = next(get_db())
            search_session = SearchSession(
                user_id=user_id,
                search_query=query,
                results_count=results_count,
                data_sources_queried=data_sources_queried,
                created_at=datetime.utcnow()
            )
            db.add(search_session)
            db.commit()
            db.refresh(search_session)  # Refresh to get the ID
            return search_session
        except Exception as e:
            print(f"Error creating search session: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def group_results_by_person(search_results: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group search results by person"""
        person_groups = {}
        
        for data_source_name, tables in search_results.items():
            for table_name, df in tables.items():
                if df.empty:
                    continue
                
                # Find person identifier columns
                person_columns = []
                for col in df.columns:
                    col_lower = col.lower()
                    if any(identifier in col_lower for identifier in ['name', 'first', 'last', 'full', 'person', 'user', 'customer', 'client', 'id', 'customerid', 'customer_id', 'userid', 'user_id']):
                        person_columns.append(col)
                
                if person_columns:
                    # Group by person identifier
                    for _, row in df.iterrows():
                        person_key = None
                        
                        # Try to create a person key from identifier columns
                        for col in person_columns:
                            if pd.notna(row[col]) and str(row[col]).strip():
                                person_key = str(row[col]).strip().lower()
                                break
                        
                        if person_key:
                            if person_key not in person_groups:
                                person_groups[person_key] = []
                            
                            person_groups[person_key].append({
                                "data_source": data_source_name,
                                "table": table_name,
                                "record": row.to_dict(),
                                "person_identifier": person_key
                            })
        
        return person_groups
    
    @staticmethod
    def get_person_provenance(person_identifier: str, user_id: int) -> Dict[str, Any]:
        """Get provenance information for a person across all data sources"""
        # Perform global search for the person
        search_results = SearchService.global_search(person_identifier, user_id)
        
        if "error" in search_results:
            return search_results
        
        # Group results by person
        person_groups = SearchService.group_results_by_person(search_results["results"])
        
        # Get detailed provenance
        provenance = {
            "person_identifier": person_identifier,
            "total_records": search_results["total_records"],
            "data_sources": search_results["data_sources_queried"],
            "records": person_groups.get(person_identifier.lower(), [])
        }
        
        return provenance
