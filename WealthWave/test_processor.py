#!/usr/bin/env python3
"""
Test script for the data processor
"""
import pandas as pd
from utils.data_processor import DataProcessor

def test_data_processor():
    """Test the data processor with the actual roster data"""
    processor = DataProcessor()
    
    try:
        # Load the actual roster file
        print("Loading Excel file...")
        df = pd.read_excel('attached_assets/Latest Epicenter Roster 1_1753944279829.xlsx')
        print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        
        # Clean the data
        print("Cleaning data...")
        cleaned_df = processor.clean_data(df)
        print(f"After cleaning: {len(cleaned_df)} rows")
        
        # Check standard columns after cleaning
        standard_cols = ['employee_id', 'employee_name', 'department', 'queue', 'position', 'status']
        print(f"Standard columns found: {[col for col in standard_cols if col in cleaned_df.columns]}")
        
        # Check generated analysis columns
        analysis_cols = ['queue_type', 'loa_status', 'role_category']
        print(f"Analysis columns generated: {[col for col in analysis_cols if col in cleaned_df.columns]}")
        
        # Show sample values
        if 'queue_type' in cleaned_df.columns:
            print(f"\nQueue type distribution:")
            print(cleaned_df['queue_type'].value_counts())
        
        if 'loa_status' in cleaned_df.columns:
            print(f"\nLOA status distribution:")
            print(cleaned_df['loa_status'].value_counts())
        
        if 'role_category' in cleaned_df.columns:
            print(f"\nRole category distribution:")
            print(cleaned_df['role_category'].value_counts())
        
        # Test summary table generation
        print("\nGenerating summary table...")
        summary_table = processor.generate_summary_table(cleaned_df)
        
        if not summary_table.empty:
            print(f"Summary table generated with {len(summary_table)} rows")
            print("\nSummary table preview:")
            print(summary_table.to_string())
        else:
            print("Failed to generate summary table")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_processor()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")