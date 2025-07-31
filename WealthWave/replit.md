# Employee Roster Analysis Tool

## Overview

This is a Streamlit-based web application designed for HR and management teams to analyze employee roster data. The application provides professional workforce analytics through interactive visualizations and data processing capabilities. Users can upload Excel files containing employee data and receive automated analysis with charts, metrics, and insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data applications with minimal frontend complexity
- **Layout**: Wide layout with expandable sidebar for controls and main content area for visualizations
- **Styling**: Custom CSS with a professional color palette (Primary: #2F5249, Secondary: #437057, Accent: #97B067, Highlight: #E3DE61)
- **Page Configuration**: Single-page application with responsive design

### Backend Architecture
- **Core Framework**: Python-based Streamlit application
- **Data Processing**: Modular approach with separate utility classes
- **File Handling**: Excel file upload and processing using pandas and openpyxl
- **Visualization Engine**: Plotly for interactive charts and graphs

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Entry point and UI orchestration
- **Responsibilities**: Page configuration, file upload handling, CSS loading, main UI layout
- **Architecture Decision**: Single-file main application with modular imports for better maintainability

### 2. Data Processing Module (utils/data_processor.py)
- **Purpose**: Handle data cleaning, validation, and transformation
- **Key Features**:
  - Excel file loading and validation
  - Data cleaning and standardization
  - Employee categorization (voice/non-voice, management roles, LOA status)
- **Architecture Decision**: Object-oriented approach with predefined keyword lists for consistent categorization

### 3. Visualization Module (utils/visualizations.py)
- **Purpose**: Create consistent, professional visualizations
- **Key Features**:
  - Custom color palette implementation
  - Standardized chart creation methods
  - Interactive Plotly charts with custom styling
- **Architecture Decision**: Helper class pattern for reusable visualization components

### 4. Styling System (styles/custom.css)
- **Purpose**: Professional visual appearance
- **Features**: Custom CSS with gradient backgrounds, consistent color scheme, responsive design
- **Architecture Decision**: Separate CSS file for maintainable styling rather than inline styles

## Data Flow

1. **Data Input**: User uploads Excel file through Streamlit file uploader
2. **Data Validation**: DataProcessor validates file format and basic structure
3. **Data Cleaning**: Automatic data cleaning and standardization based on user preferences
4. **Data Analysis**: Processing of employee data with categorization and metrics calculation
5. **Visualization**: Creation of interactive charts and graphs using VisualizationHelper
6. **Output**: Display of processed data and visualizations in the Streamlit interface

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework for data apps
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library (both express and graph_objects)
- **NumPy**: Numerical computing support
- **openpyxl**: Excel file reading capabilities

### Rationale for Technology Choices
- **Streamlit**: Chosen for rapid prototyping and ease of deployment for data-focused applications
- **Plotly**: Selected over matplotlib for interactive capabilities and professional appearance
- **Pandas**: Industry standard for data manipulation in Python
- **Excel Support**: openpyxl chosen for robust Excel file handling

## Deployment Strategy

### Development Environment
- **Structure**: Modular Python application with clear separation of concerns
- **Configuration**: Streamlit configuration handled in main application file
- **Asset Management**: Static assets (CSS) organized in dedicated styles directory

### Production Considerations
- **Scalability**: Designed for single-user sessions with file upload processing
- **Performance**: In-memory data processing suitable for typical HR roster sizes
- **Maintenance**: Modular structure allows for easy updates to processing logic and visualizations

### File Structure Rationale
- `app.py`: Single entry point for simplicity
- `utils/`: Utility modules for reusable functionality
- `styles/`: Separate styling for maintainability
- Clear separation between data processing, visualization, and presentation layers

## Key Architectural Decisions

1. **Streamlit over Flask/Django**: Chosen for rapid development and built-in data app features
2. **Modular Utility Classes**: Separate concerns for better maintainability and testing
3. **Plotly over Matplotlib**: Interactive visualizations enhance user experience
4. **Excel-First Approach**: Designed specifically for Excel file inputs common in HR workflows
5. **Custom CSS Styling**: Professional appearance to match enterprise requirements
6. **Object-Oriented Data Processing**: Encapsulation of business logic for employee categorization