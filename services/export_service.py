import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from database.models import ExportRecord
from database.connection import get_db
from utils.audit import log_action
from config import Config

class ExportService:
    """Service for handling data exports"""
    
    @staticmethod
    def export_to_csv(data: pd.DataFrame, filename: str, user_id: int, search_session_id: Optional[int] = None) -> tuple[bool, str]:
        """Export data to CSV file"""
        try:
            # Create exports directory if it doesn't exist
            os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(Config.EXPORTS_DIR, f"{filename}_{timestamp}.csv")
            
            # Export to CSV
            data.to_csv(filepath, index=False)
            
            # Create export record
            export_record = ExportService._create_export_record(
                user_id, search_session_id, 'csv', filepath, len(data)
            )
            
            # Log export action
            log_action(user_id, "export_csv", {
                "filename": filename,
                "filepath": filepath,
                "records_count": len(data),
                "export_record_id": export_record.id if export_record else None
            })
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error exporting to CSV: {str(e)}"
    
    @staticmethod
    def export_to_pdf(data: pd.DataFrame, filename: str, title: str, user_id: int, search_session_id: Optional[int] = None) -> tuple[bool, str]:
        """Export data to PDF file"""
        try:
            # Create exports directory if it doesn't exist
            os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(Config.EXPORTS_DIR, f"{filename}_{timestamp}.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add export information
            info_style = styles['Normal']
            export_info = f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            export_info += f"Total Records: {len(data)}<br/>"
            export_info += f"Columns: {', '.join(data.columns.tolist())}"
            story.append(Paragraph(export_info, info_style))
            story.append(Spacer(1, 20))
            
            # Convert DataFrame to table data
            if not data.empty:
                # Prepare table data
                table_data = [data.columns.tolist()]  # Header
                
                # Add data rows (limit to first 1000 rows for PDF)
                max_rows = min(1000, len(data))
                for _, row in data.head(max_rows).iterrows():
                    table_data.append([str(val) if pd.notna(val) else '' for val in row])
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(table)
                
                if len(data) > max_rows:
                    story.append(Spacer(1, 20))
                    story.append(Paragraph(f"Note: Only first {max_rows} records shown. Total records: {len(data)}", info_style))
            
            # Build PDF
            doc.build(story)
            
            # Create export record
            export_record = ExportService._create_export_record(
                user_id, search_session_id, 'pdf', filepath, len(data)
            )
            
            # Log export action
            log_action(user_id, "export_pdf", {
                "filename": filename,
                "filepath": filepath,
                "records_count": len(data),
                "export_record_id": export_record.id if export_record else None
            })
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error exporting to PDF: {str(e)}"
    
    @staticmethod
    def export_search_results(search_results: Dict[str, Dict[str, pd.DataFrame]], 
                             export_type: str, user_id: int, search_session_id: Optional[int] = None) -> tuple[bool, str]:
        """Export search results to file"""
        try:
            # Combine all results into a single DataFrame
            all_data = []
            
            for data_source_name, tables in search_results.items():
                for table_name, df in tables.items():
                    if not df.empty:
                        # Add source information
                        df_copy = df.copy()
                        df_copy['data_source'] = data_source_name
                        df_copy['table_name'] = table_name
                        all_data.append(df_copy)
            
            if not all_data:
                return False, "No data to export"
            
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"search_results_{timestamp}"
            title = f"Search Results - {timestamp}"
            
            if export_type.lower() == 'csv':
                return ExportService.export_to_csv(combined_df, filename, user_id, search_session_id)
            elif export_type.lower() == 'pdf':
                return ExportService.export_to_pdf(combined_df, filename, title, user_id, search_session_id)
            else:
                return False, f"Unsupported export type: {export_type}"
                
        except Exception as e:
            return False, f"Error exporting search results: {str(e)}"
    
    @staticmethod
    def export_person_provenance(provenance_data: Dict[str, Any], export_type: str, user_id: int) -> tuple[bool, str]:
        """Export person provenance data"""
        try:
            # Convert provenance data to DataFrame
            records = provenance_data.get('records', [])
            
            if not records:
                return False, "No provenance data to export"
            
            # Flatten records for export
            export_data = []
            for record in records:
                record_data = {
                    'data_source': record['data_source'],
                    'table_name': record['table'],
                    'person_identifier': record['person_identifier']
                }
                # Add record fields
                for key, value in record['record'].items():
                    record_data[f"field_{key}"] = str(value) if pd.notna(value) else ''
                export_data.append(record_data)
            
            df = pd.DataFrame(export_data)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            person_id = provenance_data.get('person_identifier', 'unknown')
            filename = f"provenance_{person_id}_{timestamp}"
            title = f"Person Provenance Report - {person_id}"
            
            if export_type.lower() == 'csv':
                return ExportService.export_to_csv(df, filename, user_id)
            elif export_type.lower() == 'pdf':
                return ExportService.export_to_pdf(df, filename, title, user_id)
            else:
                return False, f"Unsupported export type: {export_type}"
                
        except Exception as e:
            return False, f"Error exporting provenance: {str(e)}"
    
    @staticmethod
    def get_export_history(user_id: int, limit: int = 50) -> List[ExportRecord]:
        """Get export history for user"""
        db = next(get_db())
        try:
            return db.query(ExportRecord).filter(
                ExportRecord.user_id == user_id
            ).order_by(ExportRecord.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    @staticmethod
    def _create_export_record(user_id: int, search_session_id: Optional[int], export_type: str, filepath: str, records_count: int) -> Optional[ExportRecord]:
        """Create export record in database"""
        try:
            db = next(get_db())
            export_record = ExportRecord(
                user_id=user_id,
                search_session_id=search_session_id,
                export_type=export_type,
                file_path=filepath,
                records_count=records_count,
                created_at=datetime.utcnow()
            )
            db.add(export_record)
            db.commit()
            return export_record
        except Exception as e:
            print(f"Error creating export record: {e}")
            return None
        finally:
            db.close()
