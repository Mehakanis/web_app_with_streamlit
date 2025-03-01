
# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up the app
st.set_page_config(page_title="📀 Data Sweeper", layout="wide")
st.title("📀 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning, analysis, and visualization!")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

# Function to display file info and preview
def display_file_info(file, df):
    st.write(f"**File Name:** `{file.name}`")
    st.write(f"**File Size:** `{file.size / 1024:.2f} KB`")
    st.write(f"**Number of Rows:** `{len(df)}`")
    st.write(f"**Number of Columns:** `{len(df.columns)}`")

    # Display summary statistics
    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

    # Display preview of the DataFrame
    st.subheader("🔍 Preview the DataFrame")
    st.dataframe(df.head())

# Function for data cleaning
def clean_data(df):
    st.subheader("🧹 Data Cleaning Options")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Remove Duplicates"):
            df.drop_duplicates(inplace=True)
            st.success("Duplicates removed!")

    with col2:
        if st.button("Fill Missing Values"):
            numeric_cols = df.select_dtypes(include=["number"]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("Missing values filled!")

    return df

# Function for data visualization
def visualize_data(df):
    st.subheader("📊 Data Visualization")
    chart_type = st.selectbox(
        "Choose a chart type:", 
        ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"]
    )

    if chart_type == "Bar Chart":
        columns = st.multiselect("Select columns for the bar chart:", df.columns)
        if columns:
            st.bar_chart(df[columns])

    elif chart_type == "Line Chart":
        columns = st.multiselect("Select columns for the line chart:", df.columns)
        if columns:
            st.line_chart(df[columns])

    elif chart_type == "Scatter Plot":
        x_axis = st.selectbox("Select X-axis:", df.columns)
        y_axis = st.selectbox("Select Y-axis:", df.columns)
        if x_axis and y_axis:
            st.scatter_chart(df[[x_axis, y_axis]])

    elif chart_type == "Histogram":
        column = st.selectbox("Select a column for the histogram:", df.columns)
        if column:
            st.bar_chart(df[column].value_counts())

# Function for file conversion
def convert_file(df, file_name, conversion_type):
    buffer = BytesIO()
    if conversion_type == "CSV":
        df.to_csv(buffer, index=False)
        file_name = file_name.replace(".xlsx", ".csv")
        mime_type = "text/csv"
    elif conversion_type == "Excel":
        df.to_excel(buffer, index=False)
        file_name = file_name.replace(".csv", ".xlsx")
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    buffer.seek(0)
    return buffer, file_name, mime_type

# Main logic
if uploaded_files:
    for file in uploaded_files:
        st.divider()
        st.subheader(f"Processing: `{file.name}`")

        try:
            # Read the file
            file_ext = os.path.splitext(file.name)[-1].lower()
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue

            # Display file info and preview
            display_file_info(file, df)

            # Data cleaning
            df = clean_data(df)

            # Column selection
            st.subheader("🔧 Select Columns to Keep")
            columns = st.multiselect(
                f"Choose columns for `{file.name}`:", 
                df.columns, 
                default=list(df.columns)
            )
            df = df[columns]

            # Data visualization
            visualize_data(df)

            # File conversion
            st.subheader("🔄 File Conversion")
            conversion_type = st.radio(
                f"Convert `{file.name}` to:", 
                ["CSV", "Excel"], 
                key=file.name
            )

            if st.button(f"Convert `{file.name}` to {conversion_type}"):
                buffer, file_name, mime_type = convert_file(df, file.name, conversion_type)
                st.download_button(
                    label=f"Download `{file_name}`",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success(f"File converted to {conversion_type} and ready for download!")

        except Exception as e:
            st.error(f"An error occurred while processing `{file.name}`: {str(e)}")

st.success("🎉 All files processed!")
