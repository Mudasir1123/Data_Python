import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title('Data Sweeper')
st.write('Transform your files between CSV and Excel formats with built-in data cleaning and visualization!')

uploaded_files = st.file_uploader("Upload your CSV or Excel files:", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(file)
        elif file_ext == '.xlsx':
            df = pd.read_excel(file, engine="openpyxl")  # ✅ Fixed: Explicitly use openpyxl
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display file information
        st.write(f'**File Name:** {file.name}')
        st.write(f'**File Size:** {file.getbuffer().nbytes / 1024:.2f} KB')

        # Show 5 rows of the dataframe
        st.write("Preview of the Data Frame")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    df = df.drop_duplicates()
                    st.write("Duplicates removed!")

            with col2:
                if st.button(f"Fill Missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values have been filled!")

            # Choose specific columns to keep for conversion
            st.subheader("Select Columns to Convert")
            columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Data Visualization
            st.subheader("Data Visualization")
            if st.checkbox(f"Show a visualization for {file.name}"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

            # File Conversion
            st.subheader("🔁 Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to", ["CSV", "Excel"], key=file.name)

            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")  # ✅ Fixed: Explicitly use openpyxl
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)

                # Download Button
                st.download_button(
                    label=f"Download {file_name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type,
                )

st.success("All files processed!")
