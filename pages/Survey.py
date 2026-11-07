# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import csv
import math
import os # The 'os' module is used for file system operations (e.g. checking if a file exists).

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("Data Collection Survey 📝")
st.write("Please fill out the form below to add your data to the dataset.")
st.caption("For example: Category = Statics, Value = hours studied this week.")

data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.csv")

# DATA INPUT FORM
# 'st.form' creates a container that groups input widgets.
# The form is submitted only when the user clicks the 'st.form_submit_button'.
# This is useful for preventing the app from re-running every time a widget is changed.
with st.form("survey_form"):
    # Create text input widgets for the user to enter data.
    # The first argument is the label that appears above the input box.
    category_input = st.text_input("Enter a category:")
    value_input = st.text_input("Enter a corresponding value:")

    # The submit button for the form.
    submitted = st.form_submit_button("Submit Data")

    # This block of code runs ONLY when the submit button is clicked.
    if submitted:
        # --- YOUR LOGIC GOES HERE ---
        # TO DO:
        # 1. Create a new row of data from 'category_input' and 'value_input'.
        # 2. Append this new row to the 'data.csv' file.
        #    - You can use pandas or Python's built-in 'csv' module.
        #    - Make sure to open the file in 'append' mode ('a').
        #    - Don't forget to add a newline character '\n' at the end.
        category_input = category_input.strip()
        try:
            numeric_value = float(value_input.strip())
        except ValueError:
            st.error("Enter a numerical value for hours studied.")
        else:
            if not category_input:
                st.error("Enter a category before submitting.")
            elif not math.isfinite(numeric_value) or not 0 <= numeric_value <= 168:
                st.error("Enter a number of hours between 0 and 168.")
            else:
                try:
                    with open(data_file, "a", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        if os.path.getsize(data_file) == 0:
                            writer.writerow(["Category", "Value"])
                        writer.writerow([category_input, numeric_value])
                except OSError:
                    st.error("Unable to save your response to data.csv.")
                else:
                    st.success("Your data has been submitted!")
                    st.write(f"You entered: **Category:** {category_input}, **Value:** {value_input}")


# DATA DISPLAY
# This section shows the current contents of the CSV file, which helps in debugging.
st.divider() # Adds a horizontal line for visual separation.
st.header("Current Data in CSV")

# Check if the CSV file exists and is not empty before trying to read it.
if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
    # Read the CSV file into a pandas DataFrame.
    current_data_df = pd.read_csv(data_file)
    # Display the DataFrame as a table.
    st.dataframe(current_data_df)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")