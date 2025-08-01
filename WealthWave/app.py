import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
from utils.data_processor import DataProcessor
from utils.visualizations import create_visualizations

# Custom CSS for styling
def load_css():
    with open('WealthWave/styles/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
                    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                        "▣ Summary Dashboard", 
                        "▣ Summary Table",
                        "▸ Queue Analysis", 
                        "▸ LOA Tracking", 
                        "▸ Role Hierarchy", 
                        "▸ Department Insights",
                        "▸ LOB Deep Dive"
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
                    
                    with tab7:
                        display_lob_deep_dive(cleaned_df, processor)
                    
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

def display_lob_deep_dive(df, processor):
    """Display detailed LOB analysis with visual summary table format"""
    st.markdown("### ▸ LOB Deep Dive Analysis")
    st.markdown("Complete LOB breakdown with detailed metrics in PSOne Headcount Tracker format")
    
    if 'department' not in df.columns:
        st.warning("⚠ No department data found in the uploaded file.")
        return
    
    # Generate comprehensive LOB summary table in exact format requested
    lob_detailed_summary = generate_lob_visual_summary(df)
    
    # Display the detailed LOB summary table
    st.markdown("#### ▸ Complete LOB Summary Table")
    st.dataframe(lob_detailed_summary, use_container_width=True)
    
    # Add visual charts for better insights
    st.markdown("#### ▸ Visual LOB Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # LOB size comparison chart
        lob_chart_data = lob_detailed_summary[lob_detailed_summary['LOB'] != 'Total'].copy()
        fig1 = px.bar(
            lob_chart_data, 
            x='LOB', 
            y='Total',
            title="Total Employees by LOB",
            color='Total',
            color_continuous_scale=['#97B067', '#437057', '#2F5249']
        )
        fig1.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Voice vs Non-Voice distribution
        voice_data = lob_chart_data[['LOB', 'Voice', 'Non-Voice']].melt(
            id_vars=['LOB'], 
            value_vars=['Voice', 'Non-Voice'],
            var_name='Queue_Type', 
            value_name='Count'
        )
        fig2 = px.bar(
            voice_data, 
            x='LOB', 
            y='Count',
            color='Queue_Type',
            title="Voice vs Non-Voice by LOB",
            color_discrete_map={'Voice': '#2F5249', 'Non-Voice': '#437057'}
        )
        fig2.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Management distribution chart
    st.markdown("#### ▸ Management Distribution")
    mgmt_data = lob_chart_data[['LOB', 'TL', 'Manager', 'Director']].melt(
        id_vars=['LOB'], 
        value_vars=['TL', 'Manager', 'Director'],
        var_name='Management_Level', 
        value_name='Count'
    )
    fig3 = px.bar(
        mgmt_data, 
        x='LOB', 
        y='Count',
        color='Management_Level',
        title="Management Roles Distribution by LOB",
        color_discrete_map={
            'TL': '#97B067', 
            'Manager': '#437057', 
            'Director': '#2F5249'
        }
    )
    fig3.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Add download button for LOB summary
    csv_buffer = io.StringIO()
    lob_detailed_summary.to_csv(csv_buffer, index=False)
    st.download_button(
        label="▼ Download LOB Summary Table",
        data=csv_buffer.getvalue(),
        file_name=f"lob_summary_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # LOB Selection for detailed drill-down
    st.markdown("#### ▸ Select LOB for Individual Analysis")
    selected_lob = st.selectbox(
        "Choose a LOB to analyze in detail:",
        options=sorted(df['department'].unique()),
        key="lob_selector"
    )
    
    if selected_lob:
        display_detailed_lob_analysis_with_verticals(df, selected_lob, processor)

def generate_lob_visual_summary(df):
    """Generate LOB summary table in the exact format shown in the image"""
    lob_summary_data = []
    
    # Get all unique LOBs
    unique_lobs = sorted(df['department'].unique())
    
    for lob in unique_lobs:
        lob_data = df[df['department'] == lob]
        
        # Calculate all required metrics
        voice_count = len(lob_data[lob_data.get('queue_type', '') == 'Voice'])
        non_voice_count = len(lob_data[lob_data.get('queue_type', '') == 'Non-Voice'])
        loa_count = len(lob_data[lob_data.get('loa_status', '') == 'LOA'])
        
        # ATT/Move out (Work from Home + Other statuses)
        att_move_out = len(lob_data[lob_data.get('loa_status', '').isin(['Work from Home', 'Other'])])
        
        # CTE/SE and Training (Project status)
        cte_se_count = 0  # This would need specific mapping if available
        training_count = len(lob_data[lob_data.get('loa_status', '') == 'Project'])
        
        # Management roles
        tl_count = len(lob_data[lob_data.get('role_category', '') == 'Team Leader'])
        manager_count = len(lob_data[lob_data.get('role_category', '') == 'Manager'])
        director_count = len(lob_data[lob_data.get('role_category', '') == 'Director'])
        quality_count = 0  # This would need specific queue or role mapping
        
        # Totals
        total_employees = len(lob_data)
        total_mgmt = tl_count + manager_count + director_count + quality_count
        
        lob_summary_data.append({
            'LOB': lob,
            'Voice': voice_count,
            'Non-Voice': non_voice_count,
            'LOA': loa_count,
            'ATT/Move out': att_move_out,
            'CTE/SE': cte_se_count,
            'Training': training_count,
            'Total': total_employees,
            'TL': tl_count,
            'Quality': quality_count,
            'Director': director_count,
            'Manager': manager_count,
            'Total Mgmt': total_mgmt
        })
    
    # Add total row
    total_row = {
        'LOB': 'Total',
        'Voice': sum(row['Voice'] for row in lob_summary_data),
        'Non-Voice': sum(row['Non-Voice'] for row in lob_summary_data),
        'LOA': sum(row['LOA'] for row in lob_summary_data),
        'ATT/Move out': sum(row['ATT/Move out'] for row in lob_summary_data),
        'CTE/SE': sum(row['CTE/SE'] for row in lob_summary_data),
        'Training': sum(row['Training'] for row in lob_summary_data),
        'Total': sum(row['Total'] for row in lob_summary_data),
        'TL': sum(row['TL'] for row in lob_summary_data),
        'Quality': sum(row['Quality'] for row in lob_summary_data),
        'Director': sum(row['Director'] for row in lob_summary_data),
        'Manager': sum(row['Manager'] for row in lob_summary_data),
        'Total Mgmt': sum(row['Total Mgmt'] for row in lob_summary_data)
    }
    
    lob_summary_data.append(total_row)
    
    return pd.DataFrame(lob_summary_data)

def display_detailed_lob_analysis_with_verticals(df, lob_name, processor):
    """Display comprehensive analysis for a specific LOB with vertical drill-down"""
    st.markdown(f"### ▣ Detailed Analysis: {lob_name}")
    
    # Filter data for selected LOB
    lob_data = df[df['department'] == lob_name]
    
    if lob_data.empty:
        st.warning(f"⚠ No data found for LOB: {lob_name}")
        return
    
    # Key metrics row for the LOB
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", len(lob_data))
    
    with col2:
        active_count = len(lob_data[lob_data.get('loa_status', '') != 'LOA'])
        st.metric("Active Employees", active_count)
    
    with col3:
        voice_count = len(lob_data[lob_data.get('queue_type', '') == 'Voice'])
        st.metric("Voice Queue", voice_count)
    
    with col4:
        manager_count = len(lob_data[lob_data.get('role_category', '').isin(['Manager', 'Director', 'Team Leader'])])
        st.metric("Management Staff", manager_count)
    
    # Vertical/Queue Analysis Section
    st.markdown(f"#### ▸ {lob_name} Verticals/Queues Analysis")
    
    # Get verticals/queues within this LOB
    if 'queue' in lob_data.columns:
        queue_summary = lob_data['queue'].value_counts().reset_index()
        queue_summary.columns = ['Vertical/Queue', 'Employee_Count']
        
        # Add additional metrics for each vertical
        vertical_metrics = []
        for queue in queue_summary['Vertical/Queue']:
            queue_data = lob_data[lob_data['queue'] == queue]
            
            voice_count_q = len(queue_data[queue_data.get('queue_type', '') == 'Voice'])
            non_voice_count_q = len(queue_data[queue_data.get('queue_type', '') == 'Non-Voice'])
            loa_count_q = len(queue_data[queue_data.get('loa_status', '') == 'LOA'])
            manager_count_q = len(queue_data[queue_data.get('role_category', '').isin(['Manager', 'Director', 'Team Leader'])])
            
            vertical_metrics.append({
                'Vertical/Queue': queue,
                'Total_Employees': len(queue_data),
                'Voice': voice_count_q,
                'Non-Voice': non_voice_count_q,
                'LOA': loa_count_q,
                'Management': manager_count_q,
                'Active': len(queue_data) - loa_count_q
            })
        
        vertical_df = pd.DataFrame(vertical_metrics)
        
        # Display vertical summary table
        st.markdown(f"##### ▸ {lob_name} Vertical Summary")
        st.dataframe(vertical_df, use_container_width=True)
        
        # Vertical selection for detailed drill-down
        st.markdown(f"##### ▸ Select Vertical for Detailed Analysis")
        selected_vertical = st.selectbox(
            f"Choose a vertical/queue within {lob_name}:",
            options=[''] + sorted(queue_summary['Vertical/Queue'].unique()),
            key=f"vertical_selector_{lob_name}"
        )
        
        if selected_vertical:
            display_vertical_detailed_analysis(df, lob_name, selected_vertical, processor)
        
        # Visual charts for verticals
        col1, col2 = st.columns(2)
        
        with col1:
            # Top verticals by employee count
            top_verticals = vertical_df.head(10)
            fig1 = px.bar(
                top_verticals, 
                x='Vertical/Queue', 
                y='Total_Employees',
                title=f"Top 10 Verticals in {lob_name}",
                color='Total_Employees',
                color_continuous_scale=['#97B067', '#437057', '#2F5249']
            )
            fig1.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Voice vs Non-Voice by vertical (top 10)
            voice_vertical_data = top_verticals[['Vertical/Queue', 'Voice', 'Non-Voice']].melt(
                id_vars=['Vertical/Queue'], 
                value_vars=['Voice', 'Non-Voice'],
                var_name='Queue_Type', 
                value_name='Count'
            )
            fig2 = px.bar(
                voice_vertical_data, 
                x='Vertical/Queue', 
                y='Count',
                color='Queue_Type',
                title=f"Voice vs Non-Voice - Top {lob_name} Verticals",
                color_discrete_map={'Voice': '#2F5249', 'Non-Voice': '#437057'}
            )
            fig2.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    else:
        st.info(f"ⓘ Queue information not available for detailed vertical analysis of {lob_name}")

def display_vertical_detailed_analysis(df, lob_name, vertical_name, processor):
    """Display detailed analysis for a specific vertical within a LOB"""
    st.markdown(f"### ▣ Deep Dive: {lob_name} → {vertical_name}")
    
    # Filter data for selected LOB and vertical
    vertical_data = df[(df['department'] == lob_name) & (df['queue'] == vertical_name)]
    
    if vertical_data.empty:
        st.warning(f"⚠ No data found for {vertical_name} in {lob_name}")
        return
    
    # Key metrics for the vertical
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Employees", len(vertical_data))
    
    with col2:
        active_count = len(vertical_data[vertical_data.get('loa_status', '') != 'LOA'])
        st.metric("Active", active_count)
    
    with col3:
        voice_count = len(vertical_data[vertical_data.get('queue_type', '') == 'Voice'])
        st.metric("Voice", voice_count)
    
    with col4:
        loa_count = len(vertical_data[vertical_data.get('loa_status', '') == 'LOA'])
        st.metric("LOA", loa_count)
    
    with col5:
        mgmt_count = len(vertical_data[vertical_data.get('role_category', '').isin(['Manager', 'Director', 'Team Leader'])])
        st.metric("Management", mgmt_count)
    
    # Detailed breakdowns
    col1, col2 = st.columns(2)
    
    with col1:
        # Employee list with roles
        st.markdown("#### ▸ Employee Details")
        if 'employee_name' in vertical_data.columns:
            employee_details = vertical_data[['employee_name', 'role_category', 'loa_status']].copy()
            employee_details.columns = ['Employee Name', 'Role', 'Status']
            st.dataframe(employee_details, use_container_width=True)
        
        # Management team
        st.markdown("#### ▸ Management Team")
        mgmt_staff = vertical_data[vertical_data.get('role_category', '').isin(['Manager', 'Director', 'Team Leader'])]
        if not mgmt_staff.empty and 'employee_name' in mgmt_staff.columns:
            mgmt_details = mgmt_staff[['employee_name', 'role_category', 'loa_status']].copy()
            mgmt_details.columns = ['Name', 'Role', 'Status']
            st.dataframe(mgmt_details, use_container_width=True)
        else:
            st.info("ⓘ No management staff in this vertical")
    
    with col2:
        # Status breakdown
        st.markdown("#### ▸ Status Distribution")
        if 'loa_status' in vertical_data.columns:
            status_dist = vertical_data['loa_status'].value_counts()
            fig = px.pie(
                values=status_dist.values, 
                names=status_dist.index,
                title=f"Status Distribution - {vertical_name}",
                color_discrete_map={
                    'Active': '#2F5249',
                    'LOA': '#E3DE61',
                    'Work from Home': '#437057',
                    'Other': '#97B067'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional details
        st.markdown("#### ▸ Additional Information")
        if 'location' in vertical_data.columns:
            locations = vertical_data['location'].value_counts().head(5)
            st.write("**Top Locations:**")
            for loc, count in locations.items():
                st.write(f"• {loc}: {count} employees")
        
        if 'shift' in vertical_data.columns:
            shifts = vertical_data['shift'].value_counts()
            st.write("**Shift Distribution:**")
            for shift, count in shifts.items():
                st.write(f"• {shift}: {count} employees")
    
    # Performance insights for this vertical
    st.markdown("#### ▸ Vertical Performance Insights")
    
    total_vertical = len(vertical_data)
    active_rate = (active_count / total_vertical * 100) if total_vertical > 0 else 0
    mgmt_ratio = (mgmt_count / total_vertical * 100) if total_vertical > 0 else 0
    voice_coverage = (voice_count / total_vertical * 100) if total_vertical > 0 else 0
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.metric("Active Rate", f"{active_rate:.1f}%")
    with insight_col2:
        st.metric("Management Ratio", f"{mgmt_ratio:.1f}%")
    with insight_col3:
        st.metric("Voice Coverage", f"{voice_coverage:.1f}%")
    
    # Export option for this vertical
    st.markdown("#### ▸ Export Vertical Data")
    csv_buffer = io.StringIO()
    vertical_data.to_csv(csv_buffer, index=False)
    st.download_button(
        label=f"▼ Download {lob_name} - {vertical_name} Data",
        data=csv_buffer.getvalue(),
        file_name=f"{lob_name}_{vertical_name}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def display_detailed_lob_analysis(df, lob_name, processor):
    """Display comprehensive analysis for a specific LOB"""
    st.markdown(f"### ▣ Detailed Analysis: {lob_name}")
    
    # Filter data for selected LOB
    lob_data = df[df['department'] == lob_name]
    
    if lob_data.empty:
        st.warning(f"⚠ No data found for LOB: {lob_name}")
        return
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", len(lob_data))
    
    with col2:
        active_count = len(lob_data[lob_data.get('loa_status', '') != 'LOA'])
        st.metric("Active Employees", active_count)
    
    with col3:
        voice_count = len(lob_data[lob_data.get('queue_type', '') == 'Voice'])
        st.metric("Voice Queue", voice_count)
    
    with col4:
        manager_count = len(lob_data[lob_data.get('role_category', '').isin(['Manager', 'Director', 'Team Leader'])])
        st.metric("Management Staff", manager_count)
    
    # Detailed sections
    col1, col2 = st.columns(2)
    
    with col1:
        # Management breakdown
        st.markdown("#### ▸ Management Structure")
        if 'role_category' in lob_data.columns:
            mgmt_breakdown = lob_data['role_category'].value_counts()
            mgmt_df = mgmt_breakdown.reset_index()
            mgmt_df.columns = ['Role', 'Count']
            st.dataframe(mgmt_df, use_container_width=True)
        
        # Queue distribution
        st.markdown("#### ▸ Queue Distribution")
        if 'queue_type' in lob_data.columns:
            queue_dist = lob_data['queue_type'].value_counts()
            fig = px.pie(
                values=queue_dist.values, 
                names=queue_dist.index,
                title=f"Queue Distribution - {lob_name}",
                color_discrete_map={
                    'Voice': '#2F5249',
                    'Non-Voice': '#437057',
                    'Not Assigned': '#97B067'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # LOA Status breakdown
        st.markdown("#### ▸ Employee Status")
        if 'loa_status' in lob_data.columns:
            status_breakdown = lob_data['loa_status'].value_counts()
            status_df = status_breakdown.reset_index()
            status_df.columns = ['Status', 'Count']
            st.dataframe(status_df, use_container_width=True)
        
        # Specific queue breakdown
        st.markdown("#### ▸ Specific Queue Details")
        if 'queue' in lob_data.columns:
            queue_details = lob_data['queue'].value_counts().head(10)
            queue_df = queue_details.reset_index()
            queue_df.columns = ['Queue Name', 'Employees']
            st.dataframe(queue_df, use_container_width=True)
    
    # Manager and Team Leader details
    st.markdown("#### ▸ Management Team Details")
    if 'role_category' in lob_data.columns and 'employee_name' in lob_data.columns:
        mgmt_staff = lob_data[lob_data['role_category'].isin(['Manager', 'Director', 'Team Leader'])]
        
        if not mgmt_staff.empty:
            mgmt_details = mgmt_staff[['employee_name', 'role_category', 'queue', 'loa_status']].copy()
            mgmt_details.columns = ['Name', 'Role', 'Queue', 'Status']
            st.dataframe(mgmt_details, use_container_width=True)
            
            # Management summary
            col1, col2, col3 = st.columns(3)
            with col1:
                directors = len(mgmt_staff[mgmt_staff['role_category'] == 'Director'])
                st.metric("Directors", directors)
            with col2:
                managers = len(mgmt_staff[mgmt_staff['role_category'] == 'Manager'])
                st.metric("Managers", managers)
            with col3:
                team_leaders = len(mgmt_staff[mgmt_staff['role_category'] == 'Team Leader'])
                st.metric("Team Leaders", team_leaders)
        else:
            st.info("ⓘ No management staff found in this LOB.")
    
    # Performance insights
    st.markdown("#### ▸ Performance Insights")
    
    total_employees = len(lob_data)
    active_rate = (active_count / total_employees * 100) if total_employees > 0 else 0
    mgmt_ratio = (manager_count / total_employees * 100) if total_employees > 0 else 0
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        st.metric("Active Employee Rate", f"{active_rate:.1f}%")
        st.metric("Management Ratio", f"{mgmt_ratio:.1f}%")
    
    with insight_col2:
        if voice_count > 0:
            voice_rate = (voice_count / total_employees * 100)
            st.metric("Voice Queue Coverage", f"{voice_rate:.1f}%")
        
        if 'queue' in lob_data.columns:
            unique_queues = lob_data['queue'].nunique()
            st.metric("Unique Queues", unique_queues)
    
    # Export option for this LOB
    st.markdown("#### ▸ Export LOB Data")
    csv_buffer = io.StringIO()
    lob_data.to_csv(csv_buffer, index=False)
    st.download_button(
        label=f"▼ Download {lob_name} Data",
        data=csv_buffer.getvalue(),
        file_name=f"{lob_name}_detailed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
