import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
from utils.data_processor import DataProcessor
from utils.visualizations import create_visualizations

import os

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'styles', 'custom.css')
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("custom.css not found. Proceeding without custom styles.")

def main():
    # Page configuration
    st.set_page_config(
        page_title="Employee Roster Analysis Tool",
        page_icon="▣",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Header
    st.markdown("""
        <div class="header">
            <h1>▣ Employee Roster Analysis Tool</h1>
            <p>Professional workforce analytics for HR and management teams</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.markdown("### ▸ Data Upload")
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload your employee roster Excel file for analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"✓ File uploaded: {uploaded_file.name}")
            
            # Processing options
            st.markdown("### ▸ Processing Options")
            auto_clean = st.checkbox("Auto-clean data", value=True, help="Automatically clean and standardize data", key="auto_clean")
            include_loa = st.checkbox("Include LOA analysis", value=True, help="Analyze Leave of Absence data", key="include_loa")
            
            # Export options
            st.markdown("### ▸ Export Options")
            export_summary = st.button("▣ Export Summary Report", use_container_width=True, key="export_summary")
            export_detailed = st.button("▣ Export Detailed Analysis", use_container_width=True, key="export_detailed")
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Initialize data processor
            processor = DataProcessor()
            
            # Process the uploaded file
            with st.spinner("Processing your data..."):
                df = processor.load_excel_data(uploaded_file)
                
                if df is not None and not df.empty:
                    cleaned_df = processor.clean_data(df) if auto_clean else df
                    
                    # Display data overview
                    st.markdown("## ▣ Data Overview")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Employees", len(cleaned_df))
                    with col2:
                        if 'loa_status' in cleaned_df.columns:
                            active_count = len(cleaned_df[cleaned_df['loa_status'] == 'Active'])
                        else:
                            active_count = len(cleaned_df)
                        st.metric("Active Employees", int(active_count))
                    with col3:
                        if 'department' in cleaned_df.columns:
                            departments = cleaned_df['department'].nunique()
                        else:
                            departments = 0
                        st.metric("Departments", int(departments))
                    with col4:
                        if 'role_category' in cleaned_df.columns:
                            roles = cleaned_df['role_category'].nunique()
                        else:
                            roles = 0
                        st.metric("Unique Roles", int(roles))
                    
                    # Tabs for different analyses
                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                        "▣ Summary Dashboard", 
                        "▣ Summary Table",
                        "▸ Queue Analysis", 
                        "▸ LOA Tracking", 
                        "▸ Role Hierarchy", 
                        "▸ Department Insights"
                    ])
                    
                    with tab1:
                        display_summary_dashboard(cleaned_df, processor)
                    
                    with tab2:
                        display_summary_table(cleaned_df, processor)
                    
                    with tab3:
                        display_queue_analysis(cleaned_df, processor)
                    
                    with tab4:
                        if include_loa:
                            display_loa_analysis(cleaned_df, processor)
                        else:
                            st.info("LOA analysis is disabled. Enable it in the sidebar to view this section.")
                    
                    with tab5:
                        display_role_hierarchy(cleaned_df, processor)
                    
                    with tab6:
                        display_department_insights(cleaned_df, processor)
                    
                    # Handle exports
                    if export_summary:
                        summary_data = processor.generate_summary_report(cleaned_df)
                        csv_buffer = io.StringIO()
                        summary_data.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="▼ Download Summary Report",
                            data=csv_buffer.getvalue(),
                            file_name=f"roster_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    if export_detailed:
                        csv_buffer = io.StringIO()
                        cleaned_df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="▼ Download Detailed Data",
                            data=csv_buffer.getvalue(),
                            file_name=f"roster_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("✗ Unable to process the uploaded file. Please check the file format and try again.")
                    
        except Exception as e:
            st.error(f"✗ Error processing file: {str(e)}")
            st.info("Please ensure your Excel file contains valid employee roster data.")
    
    else:
        # Welcome screen
        st.markdown("""
            <div class="welcome-section">
                <h2>Welcome to the Employee Roster Analysis Tool</h2>
                <p>This professional tool helps HR teams and managers analyze workforce data with comprehensive insights including:</p>
                
                <div class="feature-grid">
                    <div class="feature-item">
                        <h3>▸ Queue Analysis</h3>
                        <p>Voice vs Non-Voice breakdown and performance metrics</p>
                    </div>
                    <div class="feature-item">
                        <h3>▸ LOA Tracking</h3>
                        <p>Leave of Absence monitoring and impact analysis</p>
                    </div>
                    <div class="feature-item">
                        <h3>▸ Role Hierarchy</h3>
                        <p>Team Leaders, Managers, and Directors analysis</p>
                    </div>
                    <div class="feature-item">
                        <h3>▸ Department Insights</h3>
                        <p>LOB headcount and departmental metrics</p>
                    </div>
                </div>
                
                <p><strong>Get started by uploading your Excel file using the sidebar.</strong></p>
            </div>
        """, unsafe_allow_html=True)

def display_summary_table(df, processor):
    """Display the summary table in PSOne Headcount Tracker format"""
    st.markdown("### ▣ Employee Roster Summary Table")
    st.markdown("This table provides a comprehensive breakdown similar to the PSOne Headcount Tracker format.")
    
    summary_table = processor.generate_summary_table(df)
    
    if not summary_table.empty:
        st.dataframe(summary_table, use_container_width=True)
        
        # Add download button for summary table
        csv_buffer = io.StringIO()
        summary_table.to_csv(csv_buffer, index=False)
        st.download_button(
            label="▼ Download Summary Table",
            data=csv_buffer.getvalue(),
            file_name=f"roster_summary_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Show key insights
        st.markdown("#### ▸ Key Insights")
        total_row = summary_table[summary_table['LOB'] == 'Total'].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Employees", int(total_row['Total']))
            st.metric("Voice Queue", int(total_row['Voice']))
        with col2:
            st.metric("Non-Voice Queue", int(total_row['Non-Voice']))
            st.metric("On LOA", int(total_row['LOA']))
        with col3:
            st.metric("Team Leaders", int(total_row['TL']))
            st.metric("Managers", int(total_row['Manager']))
    else:
        st.warning("⚠ Unable to generate summary table. Please check your data format.")

def display_summary_dashboard(df, processor):
    """Display the main summary dashboard"""
    st.markdown("### ▣ Executive Summary")
    
    # Key insights
    insights = processor.generate_key_insights(df)
    
    if insights:
        for insight in insights:
            st.info(f"ⓘ {insight}")
    
    # Summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ▸ Workforce Distribution")
        summary_stats = processor.get_summary_statistics(df)
        st.dataframe(summary_stats, use_container_width=True)
    
    with col2:
        st.markdown("#### ▸ Performance Metrics")
        if any(col in df.columns for col in ['Queue', 'Queue Type', 'Voice', 'Non-Voice']):
            queue_summary = processor.analyze_queue_distribution(df)
            if not queue_summary.empty:
                fig = px.pie(queue_summary, values='Count', names='Queue Type', 
                           color_discrete_sequence=['#2F5249', '#437057', '#97B067', '#E3DE61'])
                fig.update_layout(showlegend=True, height=300)
                st.plotly_chart(fig, use_container_width=True)

def display_queue_analysis(df, processor):
    """Display queue analysis section"""
    st.markdown("### ▸ Voice vs Non-Voice Queue Analysis")
    
    queue_data = processor.analyze_queue_distribution(df)
    
    if not queue_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Queue Distribution")
            st.dataframe(queue_data, use_container_width=True)
        
        with col2:
            st.markdown("#### Visual Breakdown")
            fig = px.bar(queue_data, x='Queue Type', y='Count', 
                        color='Queue Type',
                        color_discrete_sequence=['#2F5249', '#437057', '#97B067'])
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed queue analysis
        detailed_queue = processor.get_detailed_queue_analysis(df)
        if not detailed_queue.empty:
            st.markdown("#### Detailed Queue Breakdown")
            st.dataframe(detailed_queue, use_container_width=True)
    else:
        st.warning("⚠ No queue data found in the uploaded file.")

def display_loa_analysis(df, processor):
    """Display LOA analysis section"""
    st.markdown("### ▸ Leave of Absence Analysis")
    
    loa_data = processor.analyze_loa_status(df)
    
    if not loa_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### LOA Summary")
            st.dataframe(loa_data, use_container_width=True)
        
        with col2:
            st.markdown("#### LOA Impact")
            if len(loa_data) > 0:
                fig = px.pie(loa_data, values='Count', names='Status',
                           color_discrete_sequence=['#97B067', '#E3DE61', '#437057'])
                fig.update_layout(showlegend=True, height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # LOA trends
        loa_trends = processor.get_loa_trends(df)
        if not loa_trends.empty:
            st.markdown("#### LOA Trends by Department")
            st.dataframe(loa_trends, use_container_width=True)
    else:
        st.warning("⚠ No LOA data found in the uploaded file.")

def display_role_hierarchy(df, processor):
    """Display role hierarchy analysis"""
    st.markdown("### ▸ Role Hierarchy Analysis")
    
    hierarchy_data = processor.analyze_role_hierarchy(df)
    
    if not hierarchy_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Role Distribution")
            st.dataframe(hierarchy_data, use_container_width=True)
        
        with col2:
            st.markdown("#### Hierarchy Visualization")
            fig = px.treemap(hierarchy_data, path=['Role'], values='Count',
                           color='Count', color_continuous_scale='Greens')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Management ratios
        ratios = processor.calculate_management_ratios(df)
        if ratios:
            st.markdown("#### Management Ratios")
            ratio_data = []
            for metric, ratio in ratios.items():
                ratio_data.append([metric, ratio])
            ratio_df = pd.DataFrame(ratio_data)
            ratio_df.columns = ['Metric', 'Ratio']
            st.dataframe(ratio_df, use_container_width=True)
    else:
        st.warning("⚠ No role hierarchy data found in the uploaded file.")

def display_department_insights(df, processor):
    """Display department insights section"""
    st.markdown("### ▸ Department (LOB) Insights")
    
    dept_data = processor.analyze_departments(df)
    
    if not dept_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Department Headcount")
            st.dataframe(dept_data, use_container_width=True)
        
        with col2:
            st.markdown("#### Department Distribution")
            fig = px.bar(dept_data, x='Department', y='Headcount',
                        color='Headcount', color_continuous_scale='Greens')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Cross-functional analysis
        cross_analysis = processor.get_cross_department_analysis(df)
        if not cross_analysis.empty:
            st.markdown("#### Cross-Department Analysis")
            st.dataframe(cross_analysis, use_container_width=True)
    else:
        st.warning("⚠ No department data found in the uploaded file.")

if __name__ == "__main__":
    main()
