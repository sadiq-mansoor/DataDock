import streamlit as st
import pandas as pd
from utils.auth import get_current_user, require_auth
from services.search_service import SearchService
from services.export_service import ExportService
from services.data_source_service import DataSourceService
import plotly.express as px
import plotly.graph_objects as go

def dashboard_page():
    """Main dashboard page"""
    require_auth()
    user = get_current_user()
    
    st.title("🏠 Data Retrieval Dashboard")
    st.markdown(f"Welcome, **{user.full_name}** ({user.role.title()})")
    
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Global Search", "Data Sources", "Schema Management", "Audit Logs", "User Management", "Settings"]
        )
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Data Sources"):
            st.rerun()
        
        if st.button("📊 View Statistics"):
            st.session_state.show_stats = True
        
        # Theme toggle
        st.markdown("---")
        st.markdown("### Appearance")
        theme_col1, theme_col2 = st.columns([3, 1])
        with theme_col1:
            st.write("Theme Mode:")
        with theme_col2:
            if st.toggle("🌙" if st.session_state.theme == 'light' else "☀️", key="theme_toggle"):
                st.session_state.theme = 'dark'
            else:
                st.session_state.theme = 'light'
        
        # Apply theme
        if st.session_state.theme == 'dark':
            st.markdown("""
                <style>
                    .stApp {
                        background-color: #0E1117;
                        color: #FAFAFA;
                    }
                    .stMarkdown, .stText {
                        color: #FAFAFA !important;
                    }
                    .stButton button {
                        background-color: #262730;
                        color: #FAFAFA;
                        border: 1px solid #4A4A4A;
                    }
                    .stTextInput input {
                        background-color: #262730;
                        color: #FAFAFA;
                    }
                    .stSelectbox select {
                        background-color: #262730;
                        color: #FAFAFA;
                    }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    .stApp {
                        background-color: #FFFFFF;
                        color: #000000;
                    }
                    .stMarkdown, .stText {
                        color: #000000 !important;
                    }
                    .stButton button {
                        background-color: #F0F2F6;
                        color: #000000;
                        border: 1px solid #E0E0E0;
                    }
                </style>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            from utils.auth import logout
            logout()
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard_content(user)
    elif page == "Global Search":
        show_global_search(user)
    elif page == "Data Sources":
        show_data_sources(user)
    elif page == "Schema Management":
        show_schema_management(user)
    elif page == "Audit Logs":
        show_audit_logs(user)
    elif page == "User Management":
        show_user_management(user)
    elif page == "Settings":
        show_settings(user)

def show_dashboard_content(user):
    """Show dashboard content"""
    st.header("📊 System Overview")
    
    # Get system statistics
    data_sources = DataSourceService.get_all_data_sources()
    total_data_sources = len(data_sources)
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Data Sources", total_data_sources)
    
    with col2:
        st.metric("Active Users", "1")  # Current user
    
    with col3:
        st.metric("System Status", "🟢 Online")
    
    with col4:
        st.metric("Security Level", "🔒 High")
    
    # Quick search section
    st.header("🔍 Quick Search")
    with st.form("quick_search"):
        search_query = st.text_input("Search for person by name or identifier:", placeholder="Enter name, ID, or other identifier")
        search_button = st.form_submit_button("Search", type="primary")
        
        if search_button and search_query:
            with st.spinner("Searching across all data sources..."):
                results = SearchService.global_search(search_query, user.id)
                
                # Debug: Show raw results
                st.write("**Debug Info:**")
                st.write(f"Total records: {results.get('total_records', 0)}")
                st.write(f"Data sources queried: {results.get('data_sources_queried', [])}")
                st.write(f"Results keys: {list(results.get('results', {}).keys())}")
                
                if results.get("total_records", 0) > 0:
                    st.success(f"Found {results['total_records']} records across {len(results['data_sources_queried'])} data sources")
                    
                    # Display results in a clear, organized way
                    st.subheader("🔍 Search Results")
                    
                    # Show summary
                    st.info(f"📊 **Summary:** {results['total_records']} records found in {len(results['data_sources_queried'])} data sources")
                    
                    # Display results by data source
                    for data_source_name, tables in results["results"].items():
                        st.markdown(f"### 📁 **{data_source_name}**")
                        
                        for table_name, df in tables.items():
                            if not df.empty:
                                st.markdown(f"#### 📋 **{table_name}** ({len(df)} records)")
                                
                                # Display the data in a clean table
                                st.dataframe(
                                    df,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        col: st.column_config.TextColumn(
                                            col,
                                            help=f"Column: {col}",
                                            max_chars=50
                                        ) for col in df.columns
                                    }
                                )
                                
                                # Show record count
                                st.caption(f"📈 Showing {len(df)} records from {table_name}")
                    
                    # Group results by person if possible
                    person_groups = SearchService.group_results_by_person(results["results"])
                    
                    if person_groups:
                        st.subheader("👥 Grouped by Person")
                        st.info(f"Found {len(person_groups)} unique persons across all records")
                        
                        for person_id, records in person_groups.items():
                            with st.expander(f"👤 **{person_id}** ({len(records)} records)", expanded=True):
                                for i, record in enumerate(records, 1):
                                    st.markdown(f"**Record {i}:** {record['data_source']} > {record['table']}")
                                    
                                    # Display record data in a clean format
                                    record_df = pd.DataFrame([record['record']])
                                    st.dataframe(
                                        record_df,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                    st.divider()
                else:
                    # Check if there are any results but they might not be grouped properly
                    if results.get("results") and any(len(tables) > 0 for tables in results["results"].values()):
                        st.warning("Records found but could not be grouped by person. Showing raw results:")
                        st.subheader("📋 Raw Search Results")
                        for data_source_name, tables in results["results"].items():
                            st.write(f"**Data Source:** {data_source_name}")
                            for table_name, df in tables.items():
                                if not df.empty:
                                    st.write(f"**Table:** {table_name} ({len(df)} records)")
                                    st.dataframe(df.head(10), use_container_width=True)
                    else:
                        st.warning("No records found matching your search criteria.")
    
    # Recent activity
    st.header("📈 Recent Activity")
    
    # Get recent search history
    search_history = SearchService.get_search_history(user.id, limit=5)
    if search_history:
        for session in search_history:
            st.write(f"**{session.created_at.strftime('%Y-%m-%d %H:%M')}** - Searched for '{session.search_query}' - Found {session.results_count} records")
    else:
        st.info("No recent search activity.")
    
    # System information
    st.header("ℹ️ System Information")
    st.info("""
    **Data Retrieval System v1.0**
    
    This is a complete offline data retrieval system with the following features:
    - 🔍 Global search across multiple data sources
    - 🔒 Secure access control with role-based permissions
    - 📊 Schema management and data source configuration
    - 📝 Comprehensive audit logging
    - 📤 Export capabilities (CSV/PDF)
    - 🛡️ Sensitive data protection
    
    **Supported Data Sources:**
    - PostgreSQL databases
    - MySQL databases
    - CSV files
    - JSON files
    - XML files
    """)

def show_global_search(user):
    """Show global search page"""
    st.header("🔍 Global Search")
    
    # Search form
    with st.form("global_search_form"):
        st.subheader("Search Across All Data Sources")
        
        search_query = st.text_input("Enter search term:", placeholder="Name, ID, or other identifier")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_button = st.form_submit_button("🔍 Search", type="primary")
        
        with col2:
            if st.form_submit_button("📊 Advanced Search"):
                st.session_state.show_advanced_search = True
        
        if search_button and search_query:
            with st.spinner("Searching across all data sources..."):
                results = SearchService.global_search(search_query, user.id)
                
                if results.get("total_records", 0) > 0:
                    st.success(f"Found {results['total_records']} records across {len(results['data_sources_queried'])} data sources")
                    
                    # Display results in a clear, organized way
                    st.subheader("🔍 Search Results")
                    
                    # Show summary
                    st.info(f"📊 **Summary:** {results['total_records']} records found in {len(results['data_sources_queried'])} data sources")
                    
                    # Display results by data source
                    for data_source_name, tables in results["results"].items():
                        st.markdown(f"### 📁 **{data_source_name}**")
                        
                        for table_name, df in tables.items():
                            if not df.empty:
                                st.markdown(f"#### 📋 **{table_name}** ({len(df)} records)")
                                
                                # Display the data in a clean table
                                st.dataframe(
                                    df,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        col: st.column_config.TextColumn(
                                            col,
                                            help=f"Column: {col}",
                                            max_chars=50
                                        ) for col in df.columns
                                    }
                                )
                                
                                # Show record count
                                st.caption(f"📈 Showing {len(df)} records from {table_name}")
                    
                    # Group results by person if possible
                    person_groups = SearchService.group_results_by_person(results["results"])
                    
                    if person_groups:
                        st.subheader("👥 Grouped by Person")
                        st.info(f"Found {len(person_groups)} unique persons across all records")
                        
                        for person_id, records in person_groups.items():
                            with st.expander(f"👤 **{person_id}** ({len(records)} records)", expanded=True):
                                for i, record in enumerate(records, 1):
                                    st.markdown(f"**Record {i}:** {record['data_source']} > {record['table']}")
                                    
                                    # Display record data in a clean format
                                    record_df = pd.DataFrame([record['record']])
                                    st.dataframe(
                                        record_df,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                    st.divider()
                    
                    # Export section (outside of form)
                    st.subheader("📤 Export Options")
                    st.markdown("Export your search results in different formats:")
                    
                    export_col1, export_col2, export_col3 = st.columns(3)
                    
                    with export_col1:
                        if st.button("📥 Export to CSV", key="export_csv_global"):
                            with st.spinner("Exporting to CSV..."):
                                success, filepath = ExportService.export_search_results(results["results"], "csv", user.id, results.get("search_session_id"))
                                if success:
                                    st.success(f"✅ Exported to: {filepath}")
                                else:
                                    st.error(f"❌ Export failed: {filepath}")
                    
                    with export_col2:
                        if st.button("📄 Export to PDF", key="export_pdf_global"):
                            with st.spinner("Exporting to PDF..."):
                                success, filepath = ExportService.export_search_results(results["results"], "pdf", user.id, results.get("search_session_id"))
                                if success:
                                    st.success(f"✅ Exported to: {filepath}")
                                else:
                                    st.error(f"❌ Export failed: {filepath}")
                    
                    with export_col3:
                        if st.button("📊 Export Person Provenance", key="export_provenance_global"):
                            with st.spinner("Exporting person provenance..."):
                                success, filepath = ExportService.export_person_provenance(results["results"], user.id, results.get("search_session_id"))
                                if success:
                                    st.success(f"✅ Exported to: {filepath}")
                                else:
                                    st.error(f"❌ Export failed: {filepath}")
                else:
                    st.warning("No records found matching your search criteria.")

def show_data_sources(user):
    """Show data sources management"""
    st.header("📁 Data Sources")
    
    # Only super admin and admin can manage data sources
    if user.role not in ['super_admin', 'admin']:
        st.error("You don't have permission to manage data sources.")
        return
    
    # Add new data source
    with st.expander("➕ Add New Data Source"):
        with st.form("add_data_source"):
            st.subheader("Add New Data Source")
            
            name = st.text_input("Data Source Name")
            source_type = st.selectbox("Data Source Type", ["postgres", "mysql", "csv", "json", "xml"])
            
            if source_type in ["postgres", "mysql"]:
                host = st.text_input("Host", value="localhost")
                port = st.text_input("Port", value="5432" if source_type == "postgres" else "3306")
                database = st.text_input("Database Name")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                config = {
                    "name": name,
                    "type": source_type,
                    "host": host,
                    "port": port,
                    "database": database,
                    "username": username,
                    "password": password
                }
            else:
                # File upload for CSV, JSON, XML data sources
                uploaded_file = st.file_uploader(
                    f"Upload {source_type.upper()} file",
                    type=[source_type],
                    help=f"Select a {source_type.upper()} file to upload"
                )
                
                if uploaded_file is not None:
                    # Save the uploaded file to the data directory
                    import os
                    from config import Config
                    
                    # Create data directory if it doesn't exist
                    os.makedirs(Config.DATA_DIR, exist_ok=True)
                    
                    # Generate a unique filename
                    import uuid
                    file_extension = source_type.lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(Config.DATA_DIR, unique_filename)
                    
                    # Save the uploaded file
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"File uploaded successfully: {uploaded_file.name}")
                    
                    config = {
                        "name": name,
                        "type": source_type,
                        "file_path": file_path
                    }
                else:
                    config = None
            
            if st.form_submit_button("Add Data Source"):
                if name:
                    if source_type in ["postgres", "mysql"] or config is not None:
                        success, message = DataSourceService.create_data_source(config, user.id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error(f"Please upload a {source_type.upper()} file.")
                else:
                    st.error("Please provide a data source name.")
    
    # List existing data sources
    st.subheader("📋 Existing Data Sources")
    data_sources = DataSourceService.get_all_data_sources()
    
    if data_sources:
        for ds in data_sources:
            with st.expander(f"📁 {ds.name} ({ds.type})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {ds.type}")
                    st.write(f"**Created:** {ds.created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Last Updated:** {ds.last_updated.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if st.button("🔄 Test Connection", key=f"test_{ds.id}"):
                        success, message = DataSourceService.test_data_source_connection(ds.id)
                        if success:
                            st.success("✅ Connected")
                        else:
                            st.error(f"❌ {message}")
                    
                    if st.button("🗑️ Delete", key=f"delete_{ds.id}"):
                        success, message = DataSourceService.delete_data_source(ds.id, user.id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    else:
        st.info("No data sources configured yet.")

def show_schema_management(user):
    """Show schema management"""
    st.header("🗂️ Schema Management")
    
    if user.role not in ['super_admin', 'admin']:
        st.error("You don't have permission to manage schemas.")
        return
    
    # Select data source
    data_sources = DataSourceService.get_all_data_sources()
    if not data_sources:
        st.info("No data sources available. Please add data sources first.")
        return
    
    selected_ds = st.selectbox("Select Data Source:", data_sources, format_func=lambda x: x.name)
    
    if selected_ds:
        st.subheader(f"Schema for: {selected_ds.name}")
        
        # Refresh schema button
        if st.button("🔄 Refresh Schema"):
            success, message = DataSourceService.refresh_schema(selected_ds.id, user.id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        # Display schema
        if selected_ds.schema_info:
            for table_name, table_info in selected_ds.schema_info.items():
                with st.expander(f"📋 {table_name}"):
                    st.write(f"**Columns:** {len(table_info.get('columns', []))}")
                    
                    # Display columns
                    columns_df = pd.DataFrame(table_info.get('columns', []))
                    if not columns_df.empty:
                        st.dataframe(columns_df, use_container_width=True)
        else:
            st.info("No schema information available.")

def show_audit_logs(user):
    """Show audit logs"""
    st.header("📝 Audit Logs")
    
    if user.role not in ['super_admin', 'admin']:
        st.error("You don't have permission to view audit logs.")
        return
    
    from utils.audit import get_audit_logs
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        action_filter = st.selectbox("Filter by Action:", ["All", "login", "logout", "search", "export", "create_data_source"])
    with col2:
        limit = st.slider("Number of logs:", 10, 100, 50)
    
    # Get audit logs
    action = None if action_filter == "All" else action_filter
    logs = get_audit_logs(action=action, limit=limit)
    
    if logs:
        st.subheader(f"Recent Audit Logs ({len(logs)} entries)")
        
        for log in logs:
            with st.expander(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log.action}"):
                st.write(f"**User ID:** {log.user_id}")
                st.write(f"**Action:** {log.action}")
                st.write(f"**IP Address:** {log.ip_address or 'N/A'}")
                if log.details:
                    st.write("**Details:**")
                    st.json(log.details)
    else:
        st.info("No audit logs found.")
    
    # Export audit logs
    st.subheader("📤 Export Audit Logs")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export to CSV"):
            from utils.audit import export_audit_logs
            filepath = export_audit_logs(format='csv')
            st.success(f"Exported to: {filepath}")
    
    with col2:
        if st.button("📄 Export to JSON"):
            from utils.audit import export_audit_logs
            filepath = export_audit_logs(format='json')
            st.success(f"Exported to: {filepath}")

def show_user_management(user):
    """Show user management"""
    st.header("👥 User Management")
    
    if user.role != 'super_admin':
        st.error("Only Super Admins can manage users.")
        return
    
    # Add new user
    with st.expander("➕ Add New User"):
        with st.form("add_user"):
            st.subheader("Add New User")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["user", "admin", "super_admin"])
            
            if st.form_submit_button("Add User"):
                if username and password and full_name and email:
                    from utils.auth import create_user
                    success, message = create_user(username, password, full_name, email, role, user.id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields.")
    
    # List users
    st.subheader("📋 User List")
    from database.models import User
    from database.connection import get_db
    
    db = next(get_db())
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        if users:
            for u in users:
                with st.expander(f"👤 {u.username} ({u.role})"):
                    st.write(f"**Full Name:** {u.full_name}")
                    st.write(f"**Email:** {u.email}")
                    st.write(f"**Role:** {u.role}")
                    st.write(f"**Created:** {u.created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Last Login:** {u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never'}")
                    
                    if u.id != user.id:  # Can't delete yourself
                        if st.button("🗑️ Deactivate User", key=f"deactivate_{u.id}"):
                            u.is_active = False
                            db.commit()
                            st.success(f"User {u.username} deactivated.")
                            st.rerun()
        else:
            st.info("No users found.")
    finally:
        db.close()

def show_settings(user):
    """Show settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("User Profile")
    st.write(f"**Username:** {user.username}")
    st.write(f"**Full Name:** {user.full_name}")
    st.write(f"**Email:** {user.email}")
    st.write(f"**Role:** {user.role}")
    st.write(f"**Account Created:** {user.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    st.subheader("System Settings")
    st.info("""
    **Data Retrieval System Settings**
    
    - **Environment:** Offline/On-premise
    - **Security:** Complete offline system
    - **Audit Logging:** Enabled
    - **Sensitive Data Protection:** Enabled
    - **Export Formats:** CSV, PDF
    
    Contact your system administrator for configuration changes.
    """)

if __name__ == "__main__":
    dashboard_page()
