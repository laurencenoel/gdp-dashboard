import streamlit as st

import pandas as pd

import plotly.express as px
import re




def guess_column_types(file_path, delimiter=',', has_headers=True):
    try:
        # Read the CSV file using the specified delimiter and header settings
        df = pd.read_csv(file_path, sep=delimiter, header=0 if has_headers else None)

        # Initialize a dictionary to store column data types
        column_types = {}

        dtype_map = {
         'integer': 'int64',
          'floating': 'float64',
           'string': 'string',
          'unicode': 'object',
          'bytes': 'object',
          'boolean': 'bool',
          'datetime': 'datetime64[ns]',
          'date': 'datetime64[ns]',
          'timedelta': 'timedelta64[ns]',
          'complex': 'complex128',
          'mixed': 'object',
          'mixed-integer': 'object',
         'mixed-integer-float': 'float64',
         'empty': 'object',
        }

        # Loop through columns and infer data types
        for column in df.columns:
            # sample_values = df[column].dropna().sample(min(5, len(df[column])), random_state=42)

            # Check for datetime format "YYYY-MM-DD HH:MM:SS"
            is_datetime = all(re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(value)) for value in df[column])

            # Check for date format "YYYY-MM-DD"
            is_date = all(re.match(r'\d{4}-\d{2}-\d{2}', str(value)) for value in df[column])

            # Assign data type based on format detection
            if is_datetime:
                target_dtype = 'datetime64[ns]'
            elif is_date:
                target_dtype = 'datetime64[ns]'
            else:
                inferred_type = pd.api.types.infer_dtype(df[column], skipna=True)
                target_dtype = dtype_map.get(inferred_type, 'object')

            column_types[column] = target_dtype

        return (True, column_types)  # Return success and column types
    except pd.errors.ParserError:
        return (False, str(e))  # Return error message


# Title

st.title("Simple Chart Viewer with CSV upload")



# Upload data

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is None:

    st.stop()

# Read the first line from the uploaded file (as a file-like object)
header_line = uploaded_file.readline().decode('utf-8')

# Reset the file pointer to the beginning so it can be read again later
uploaded_file.seek(0)

# Determine separator based on counts in the header line
sep = ',' if header_line.count(',') > header_line.count(';') else ';'

# Reset the file pointer to the beginning so it can be read again later
uploaded_file.seek(0)

# Determine column types
success, column_types = guess_column_types(uploaded_file, sep, has_headers=True)
# Reset the file pointer to the beginning so it can be read again later
uploaded_file.seek(0)

st.write("Type:", column_types)

# Load data

df = pd.read_csv(uploaded_file, sep=sep, dtype=column_types)
#st.write("Data Preview", df)
st.write("Info:", df.info())

st.write("Header Preview:", df.head())



# Select plot type

plot_type = st.selectbox("Select plot type", ["Bar Plot", "Pie Chart"])



# Select x and y axes (for bar plot)

if plot_type == "Bar Plot":

    idx = df.applymap(lambda x: isinstance(x, str)).all(0)
    #if header_line.contains('year|Year') : 
       # y_index= df.index("Year")
      
    st.write("Header Preview:", idx)


    x_axis = st.selectbox("Select x-axis", df.columns[idx])
    st.write("X:", x_axis)

    y_axis = st.selectbox("Select y-axis", df.columns[~idx])

    stack_by = st.selectbox("Group by (optional)", ["None"] + list(df.columns[idx]))

    #distinct = st.checkbox("Show distinct values only")

    #only keep the columns of interest
    if stack_by != "None":

        df_filtered = df[[x_axis,y_axis,stack_by]].copy()

    else :
        df_filtered = df[[x_axis,y_axis]].copy()

    # Group by x_axis and calculate mean
    df_result = df_filtered.groupby(x_axis, as_index=False)[y_axis].mean()

    #if distinct:

       # df = df.drop_duplicates(subset=[x_axis])



    #if stack_by != "None":

        #df = df.groupby(stack_by).sum(numeric_only=True).reset_index()



    fig = px.bar(df_result, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")

    st.plotly_chart(fig, use_container_width=True)



# Select fields for pie chart

elif plot_type == "Pie Chart":

    names = st.selectbox("Select names", df.columns)

    values = st.selectbox("Select values", df.columns)

    fig = px.pie(df, names=names, values=values, title=f"Pie Chart of {values} by {names}")

    st.plotly_chart(fig, use_container_width=True)




