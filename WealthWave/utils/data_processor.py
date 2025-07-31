import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
import re

class DataProcessor:
    """
    Data processing utilities for employee roster analysis
    """
    
    def __init__(self):
        self.voice_keywords = ['voice', 'call', 'phone', 'inbound', 'outbound', 'dialer']
        self.non_voice_keywords = ['chat', 'email', 'ticket', 'non-voice', 'nonvoice', 'back office']
        self.loa_keywords = ['loa', 'leave', 'absence', 'medical', 'maternity', 'vacation']
        self.management_roles = ['tl', 'team leader', 'manager', 'director', 'supervisor', 'head']
    
    def load_excel_data(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Load and validate Excel data from uploaded file
        """
        try:
            # Try to read the Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            if df.empty:
                return None
            
            # Basic validation
            if len(df.columns) < 2:
                return None
            
            return df
            
        except Exception as e:
            print(f"Error loading Excel file: {str(e)}")
            return None
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the employee data
        """
        if df is None or df.empty:
            return df
        
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Standardize column names - but avoid duplicates
        new_columns = []
        seen_columns = set()
        for col in cleaned_df.columns:
            standardized = self._standardize_column_name(col)
            if standardized in seen_columns:
                # If we already have this standardized name, keep original
                new_columns.append(col.lower().replace(' ', '_'))
            else:
                new_columns.append(standardized)
                seen_columns.add(standardized)
        cleaned_df.columns = new_columns
        
        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Clean text columns safely
        try:
            text_columns = cleaned_df.select_dtypes(include=['object']).columns
            for col in text_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].fillna('').astype(str).str.strip()
                    cleaned_df[col] = cleaned_df[col].replace('nan', '')
        except Exception as e:
            print(f"Warning: Could not clean text columns: {e}")
            pass
        
        # Standardize status values
        if 'status' in cleaned_df.columns:
            cleaned_df['status'] = cleaned_df['status'].str.upper()
        
        # Identify queue types
        cleaned_df = self._identify_queue_types(cleaned_df)
        
        # Identify LOA status
        cleaned_df = self._identify_loa_status(cleaned_df)
        
        # Categorize roles
        cleaned_df = self._categorize_roles(cleaned_df)
        
        return cleaned_df
    
    def _standardize_column_name(self, col_name: str) -> str:
        """
        Standardize column names for consistency
        """
        if not isinstance(col_name, str):
            return str(col_name)
        
        # Convert to lowercase and replace spaces/special chars with underscores
        standardized = re.sub(r'[^\w\s]', '', col_name.lower())
        standardized = re.sub(r'\s+', '_', standardized)
        
        # Map common variations to standard names
        mapping = {
            'badge': 'employee_id',
            'name': 'employee_name',
            'full_name': 'employee_name',
            'lob': 'department',
            'business_unit': 'department',
            'phone_queue': 'queue',
            'title': 'position',
            'role': 'position',
            'job_title': 'position',
            'queuestatus': 'status'
        }
        
        return mapping.get(standardized, standardized)
    
    def _identify_queue_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify voice vs non-voice queues based on available data
        """
        # Look for queue-related columns (including Phone Queue, queue, etc.)
        queue_columns = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['queue', 'phone_queue', 'channel', 'subqueue'])]
        
        if queue_columns:
            # Use the first queue column found
            queue_col = queue_columns[0]
            
            def categorize_queue(value):
                if pd.isna(value) or value == '' or str(value).lower() == 'not assigned':
                    return 'Not Assigned'
                
                value_str = str(value).lower()
                # Specific rules based on your data
                if any(keyword in value_str for keyword in ['support', 'commercial', 'enterprise', 'server', 'english', 'pro support']):
                    return 'Voice'
                elif any(keyword in value_str for keyword in ['chat', 'email', 'ticket', 'knowledge', 'operations', 'escalation']):
                    return 'Non-Voice'
                else:
                    # Default to Voice for most support queues
                    return 'Voice'
            
            df['queue_type'] = df[queue_col].apply(categorize_queue)
        
        return df
    
    def _identify_loa_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify employees on Leave of Absence
        """
        # Look for status or LOA-related columns (QueueStatus, status, etc.)
        status_columns = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['status', 'queuestatus', 'loa', 'leave', 'absence'])]
        
        if status_columns:
            status_col = status_columns[0]
            
            def identify_loa(value):
                if pd.isna(value) or value == '':
                    return 'Active'
                
                value_str = str(value).lower()
                if 'leave of absence' in value_str or 'loa' in value_str:
                    return 'LOA'
                elif 'normal' in value_str or 'active' in value_str:
                    return 'Active'
                elif 'work from home' in value_str:
                    return 'Work from Home'
                elif 'project' in value_str:
                    return 'Project'
                else:
                    return 'Other'
            
            df['loa_status'] = df[status_col].apply(identify_loa)
        
        return df
    
    def _categorize_roles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize roles into hierarchy levels
        """
        # Look for position/role columns (Title, position, role, etc.)
        role_columns = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['position', 'role', 'title', 'designation'])]
        
        if role_columns:
            role_col = role_columns[0]
            
            def categorize_role(value):
                if pd.isna(value) or value == '':
                    return 'Unknown'
                
                value_str = str(value).lower()
                if 'director' in value_str:
                    return 'Director'
                elif 'manager' in value_str or 'support manager' in value_str:
                    return 'Manager'
                elif any(tl in value_str for tl in ['lead', 'technical lead', 'team lead', 'tl']):
                    return 'Team Leader'
                elif any(keyword in value_str for keyword in ['specialist', 'expert', 'analyst', 'engineer', 'technician']):
                    return 'Individual Contributor'
                else:
                    return 'Individual Contributor'
            
            df['role_category'] = df[role_col].apply(categorize_role)
        
        return df
    
    def generate_key_insights(self, df: pd.DataFrame) -> List[str]:
        """
        Generate key insights from the data
        """
        insights = []
        
        if df.empty:
            return insights
        
        total_employees = len(df)
        
        # Active vs inactive insight
        if 'loa_status' in df.columns:
            active_count = len(df[df['loa_status'] == 'Active'])
            loa_count = len(df[df['loa_status'] == 'LOA'])
            if loa_count > 0:
                loa_percentage = (loa_count / total_employees) * 100
                insights.append(f"{loa_percentage:.1f}% of employees are currently on Leave of Absence")
        
        # Queue distribution insight
        if 'queue_type' in df.columns:
            voice_count = len(df[df['queue_type'] == 'Voice'])
            if voice_count > 0:
                voice_percentage = (voice_count / total_employees) * 100
                insights.append(f"{voice_percentage:.1f}% of employees work in Voice queues")
        
        # Management ratio insight
        if 'role_category' in df.columns:
            mgmt_count = len(df[df['role_category'].isin(['Manager', 'Director', 'Team Leader'])])
            if mgmt_count > 0:
                mgmt_ratio = total_employees / mgmt_count
                insights.append(f"Management ratio: 1 manager for every {mgmt_ratio:.1f} employees")
        
        # Department distribution
        if 'department' in df.columns:
            dept_count = df['department'].nunique()
            insights.append(f"Workforce spans across {dept_count} departments")
        
        return insights
    
    def get_summary_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics table
        """
        if df.empty:
            return pd.DataFrame()
        
        summary_data = []
        
        # Total count
        summary_data.append(['Total Employees', len(df)])
        
        # Status breakdown
        if 'loa_status' in df.columns:
            for status in df['loa_status'].unique():
                count = len(df[df['loa_status'] == status])
                summary_data.append([f'{status} Employees', count])
        
        # Queue breakdown
        if 'queue_type' in df.columns:
            for queue_type in df['queue_type'].unique():
                count = len(df[df['queue_type'] == queue_type])
                summary_data.append([f'{queue_type} Queue', count])
        
        # Role breakdown
        if 'role_category' in df.columns:
            for role in df['role_category'].unique():
                count = len(df[df['role_category'] == role])
                summary_data.append([role, count])
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.columns = ['Metric', 'Count']
        return summary_df
    
    def analyze_queue_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze queue type distribution
        """
        if 'queue_type' not in df.columns or df.empty:
            return pd.DataFrame()
        
        queue_counts = df['queue_type'].value_counts().reset_index()
        queue_counts.columns = ['Queue Type', 'Count']
        queue_counts['Percentage'] = (queue_counts['Count'] / len(df) * 100).round(2)
        
        return queue_counts
    
    def get_detailed_queue_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get detailed queue analysis by department
        """
        if 'queue_type' not in df.columns or 'department' not in df.columns or df.empty:
            return pd.DataFrame()
        
        detailed = df.groupby(['department', 'queue_type']).size().reset_index()
        detailed.columns = ['department', 'queue_type', 'Count']
        detailed = detailed.pivot(index='department', columns='queue_type', values='Count').fillna(0)
        detailed = detailed.reset_index()
        
        return detailed
    
    def analyze_loa_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze LOA status distribution
        """
        if 'loa_status' not in df.columns or df.empty:
            return pd.DataFrame()
        
        loa_counts = df['loa_status'].value_counts().reset_index()
        loa_counts.columns = ['Status', 'Count']
        loa_counts['Percentage'] = (loa_counts['Count'] / len(df) * 100).round(2)
        
        return loa_counts
    
    def get_loa_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get LOA trends by department
        """
        if 'loa_status' not in df.columns or 'department' not in df.columns or df.empty:
            return pd.DataFrame()
        
        trends = df.groupby(['department', 'loa_status']).size().reset_index()
        trends.columns = ['department', 'loa_status', 'Count']
        trends = trends.pivot(index='department', columns='loa_status', values='Count').fillna(0)
        trends = trends.reset_index()
        
        return trends
    
    def analyze_role_hierarchy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze role hierarchy distribution
        """
        if 'role_category' not in df.columns or df.empty:
            return pd.DataFrame()
        
        role_counts = df['role_category'].value_counts().reset_index()
        role_counts.columns = ['Role', 'Count']
        role_counts['Percentage'] = (role_counts['Count'] / len(df) * 100).round(2)
        
        return role_counts
    
    def calculate_management_ratios(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate management to employee ratios
        """
        if 'role_category' not in df.columns or df.empty:
            return {}
        
        ratios = {}
        total_employees = len(df)
        
        # Calculate ratios for different management levels
        directors = len(df[df['role_category'] == 'Director'])
        managers = len(df[df['role_category'] == 'Manager'])
        team_leaders = len(df[df['role_category'] == 'Team Leader'])
        ics = len(df[df['role_category'] == 'Individual Contributor'])
        
        if directors > 0:
            ratios['Employees per Director'] = round(total_employees / directors, 2)
        if managers > 0:
            ratios['Employees per Manager'] = round(total_employees / managers, 2)
        if team_leaders > 0:
            ratios['Employees per Team Leader'] = round(total_employees / team_leaders, 2)
        if ics > 0:
            ratios['Management to IC Ratio'] = round((directors + managers + team_leaders) / ics, 2)
        
        return ratios
    
    def analyze_departments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze department distribution
        """
        if 'department' not in df.columns or df.empty:
            return pd.DataFrame()
        
        dept_counts = df['department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Headcount']
        dept_counts['Percentage'] = (dept_counts['Headcount'] / len(df) * 100).round(2)
        
        return dept_counts
    
    def get_cross_department_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get cross-department analysis with multiple dimensions
        """
        if 'department' not in df.columns or df.empty:
            return pd.DataFrame()
        
        # Create cross-analysis with available dimensions
        analysis_columns = ['department']
        
        if 'queue_type' in df.columns:
            analysis_columns.append('queue_type')
        if 'loa_status' in df.columns:
            analysis_columns.append('loa_status')
        if 'role_category' in df.columns:
            analysis_columns.append('role_category')
        
        if len(analysis_columns) > 1:
            cross_analysis = df.groupby(analysis_columns).size().reset_index()
            cross_analysis.columns = list(analysis_columns) + ['Count']
            return cross_analysis
        
        return pd.DataFrame()
    
    def generate_summary_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a comprehensive summary report for export
        """
        if df.empty:
            return pd.DataFrame()
        
        summary_sections = []
        
        # Overall statistics
        overall_stats = self.get_summary_statistics(df)
        overall_stats['Category'] = 'Overall Statistics'
        summary_sections.append(overall_stats)
        
        # Queue analysis
        if 'queue_type' in df.columns:
            queue_stats = self.analyze_queue_distribution(df)
            queue_stats['Category'] = 'Queue Distribution'
            queue_stats = queue_stats.rename(columns={'Queue Type': 'Metric', 'Count': 'Count'})
            summary_sections.append(queue_stats[['Category', 'Metric', 'Count', 'Percentage']])
        
        # LOA analysis
        if 'loa_status' in df.columns:
            loa_stats = self.analyze_loa_status(df)
            loa_stats['Category'] = 'LOA Status'
            loa_stats = loa_stats.rename(columns={'Status': 'Metric'})
            summary_sections.append(loa_stats[['Category', 'Metric', 'Count', 'Percentage']])
        
        # Role hierarchy
        if 'role_category' in df.columns:
            role_stats = self.analyze_role_hierarchy(df)
            role_stats['Category'] = 'Role Hierarchy'
            role_stats = role_stats.rename(columns={'Role': 'Metric'})
            summary_sections.append(role_stats[['Category', 'Metric', 'Count', 'Percentage']])
        
        # Department analysis
        if 'department' in df.columns:
            dept_stats = self.analyze_departments(df)
            dept_stats['Category'] = 'Department Distribution'
            dept_stats = dept_stats.rename(columns={'Department': 'Metric', 'Headcount': 'Count'})
            summary_sections.append(dept_stats[['Category', 'Metric', 'Count', 'Percentage']])
        
        # Combine all sections
        if summary_sections:
            combined_report = pd.concat(summary_sections, ignore_index=True)
            return combined_report
        
        return pd.DataFrame()
    
    def generate_summary_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a summary table in the format of PSOne Headcount Tracker
        """
        if df.empty or 'department' not in df.columns:
            return pd.DataFrame()
        
        summary_rows = []
        
        # Group by department (LOB)
        dept_groups = df.groupby('department')
        for dept in sorted(dept_groups.groups.keys()):
            dept_df = df[df['department'] == dept]
            
            # Count Voice vs Non-Voice
            voice_count = len(dept_df[dept_df.get('queue_type', '') == 'Voice'])
            non_voice_count = len(dept_df[dept_df.get('queue_type', '') == 'Non-Voice'])
            
            # Count LOA and ATT/Move out (other statuses)
            loa_count = len(dept_df[dept_df.get('loa_status', pd.Series()) == 'LOA'])
            if 'loa_status' in dept_df.columns:
                att_moveout = len(dept_df[dept_df['loa_status'].isin(['Project', 'Other'])])
                training_count = len(dept_df[dept_df['loa_status'] == 'Training'])
            else:
                att_moveout = 0
                training_count = 0
            
            # Count CTE/FC (could be derived from status or queue)
            cte_fc = 0  # This might need specific logic based on your data
            
            # Total employees
            total = len(dept_df)
            
            # Count management roles
            tl_count = len(dept_df[dept_df.get('role_category', '') == 'Team Leader'])
            manager_count = len(dept_df[dept_df.get('role_category', '') == 'Manager'])
            director_count = len(dept_df[dept_df.get('role_category', '') == 'Director'])
            quality_count = 0  # This might need specific logic
            
            total_mgmt = tl_count + manager_count + director_count + quality_count
            
            summary_rows.append([
                dept,
                voice_count,
                non_voice_count,
                loa_count,
                att_moveout,
                cte_fc,
                training_count,
                total,
                tl_count,
                quality_count,
                director_count,
                manager_count,
                total_mgmt
            ])
        
        # Add totals row
        total_voice = sum(row[1] for row in summary_rows)
        total_non_voice = sum(row[2] for row in summary_rows)
        total_loa = sum(row[3] for row in summary_rows)
        total_att = sum(row[4] for row in summary_rows)
        total_cte = sum(row[5] for row in summary_rows)
        total_training = sum(row[6] for row in summary_rows)
        grand_total = sum(row[7] for row in summary_rows)
        total_tl = sum(row[8] for row in summary_rows)
        total_quality = sum(row[9] for row in summary_rows)
        total_director = sum(row[10] for row in summary_rows)
        total_manager = sum(row[11] for row in summary_rows)
        total_all_mgmt = sum(row[12] for row in summary_rows)
        
        summary_rows.append([
            'Total',
            total_voice,
            total_non_voice,
            total_loa,
            total_att,
            total_cte,
            total_training,
            grand_total,
            total_tl,
            total_quality,
            total_director,
            total_manager,
            total_all_mgmt
        ])
        
        columns = ['LOB', 'Voice', 'Non-Voice', 'LOA', 'ATT/Move out', 'CTE/FC', 'Training', 'Total', 'TL', 'Quality', 'Director', 'Manager', 'Total Mgmt']
        summary_df = pd.DataFrame(summary_rows)
        summary_df.columns = columns
        
        return summary_df
