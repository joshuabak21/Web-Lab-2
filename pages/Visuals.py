# This creates the page for displaying data visualizations.

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path


root = Path(__file__).resolve().parent.parent


def show_statistics(values, identifier, selection):
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        col1, col2 = st.columns(2)
        col1.metric("Mean Hours", "N/A")
        col2.metric("Median Hours", "N/A")
        return

    mean = float(values.mean())
    median = float(values.median())
    state_key = identifier + "_statistics"
    current = (mean, median)
    if state_key not in st.session_state:
        st.session_state[state_key] = {"selection": selection, "current": current, "previous": None}

    state = st.session_state[state_key]
    if state["selection"] != selection:
        state["previous"] = state["current"]
        state["current"] = current
        state["selection"] = selection

    previous = state["previous"]
    mean_delta = f"{mean - previous[0]:+.2f}" if previous is not None else None
    median_delta = f"{median - previous[1]:+.2f}" if previous is not None else None
    col1, col2 = st.columns(2)
    col1.metric("Mean Hours", f"{mean:.2f}", delta=mean_delta)
    col2.metric("Median Hours", f"{median:.2f}", delta=median_delta)



# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visuals",
    page_icon="📈",
)

# PAGE TITLE
st.title("Data Visualizations 📈")


# PART 1: GRAPHS FROM data.json
# --- YOUR CODE GOES HERE ---
st.header("Part 1: JSON Visualizations")

with (root / "data.json").open("r", encoding="utf-8") as file:
    json_data = json.load(file)

json_df = pd.DataFrame(json_data["data_points"])
json_df["value"] = pd.to_numeric(json_df["value"], errors="coerce")
json_df = json_df.dropna(subset=["value"])

st.subheader("1. Study Hours by Course (Static Bar Chart)")
st.bar_chart(json_df, x="label", y="value", x_label="Course", y_label="Weekly Study Hours")

st.subheader("2. Study Hours Distribution (Dynamic Pie Chart)")
course_options = json_df["label"].tolist()
if "json_courses" not in st.session_state:
    st.session_state["json_courses"] = course_options.copy()
else:
    st.session_state["json_courses"] = [course for course in st.session_state["json_courses"] if course in course_options]

st.multiselect("Select courses to display", course_options, key="json_courses")
json_filtered = json_df[json_df["label"].isin(st.session_state["json_courses"])]

if not json_filtered.empty:
    pie = px.pie(
        json_filtered,
        names="label",
        values="value",
        title=json_data["chart_title"],
        labels={"label": "Course", "value": "Weekly Study Hours"},
    )
    pie.update_traces(textinfo="percent+label")
    st.plotly_chart(pie, use_container_width=True)
else:
    st.info("Select at least one course to view the pie chart.")

show_statistics(json_filtered["value"], "json", tuple(st.session_state["json_courses"]))
st.divider()



# PART 2: GRAPHS FROM data.csv
# --- YOUR CODE GOES HERE ---
st.header("Part 2: CSV Visualizations")

try:
    csv_df = pd.read_csv(root / "data.csv")
except (FileNotFoundError, pd.errors.EmptyDataError):
    csv_df = pd.DataFrame(columns=["Category", "Value"])

if not {"Category", "Value"}.issubset(csv_df.columns):
    st.error("data.csv must contain Category and Value columns.")
    st.stop()

csv_df["Value"] = pd.to_numeric(csv_df["Value"], errors="coerce")
csv_df = csv_df.dropna(subset=["Category", "Value"])
csv_df = csv_df[csv_df["Category"].astype(str).str.strip().ne("")].copy()
csv_df["Response"] = range(1, len(csv_df) + 1)

if csv_df.empty:
    st.info("Submit a response on the Survey page to see the CSV visualizations.")
    st.stop()

st.subheader("3. Total Survey Study Hours by Course (Static Bar Chart)")
csv_totals = csv_df.groupby("Category", as_index=False)["Value"].sum()
st.bar_chart(csv_totals, x="Category", y="Value", x_label="Course", y_label="Total Reported Hours")

st.subheader("4. Survey Responses (Dynamic Scatter Plot)")
categories = sorted(csv_df["Category"].unique().tolist())
options = ["All"] + categories
if "csv_category" not in st.session_state or st.session_state["csv_category"] not in options:
    st.session_state["csv_category"] = "All"

max_hours = max(1.0, float(csv_df["Value"].max()))
if "csv_max_hours" not in st.session_state:
    st.session_state["csv_max_hours"] = max_hours
elif st.session_state["csv_max_hours"] > max_hours:
    st.session_state["csv_max_hours"] = max_hours

st.selectbox("Choose a course", options, key="csv_category")
st.slider("Maximum study hours to display", min_value=0.0, max_value=max_hours, key="csv_max_hours")

csv_filtered = csv_df[csv_df["Value"] <= st.session_state["csv_max_hours"]]
if st.session_state["csv_category"] != "All":
    csv_filtered = csv_filtered[csv_filtered["Category"] == st.session_state["csv_category"]]

if not csv_filtered.empty:
    scatter = px.scatter(
        csv_filtered,
        x="Response",
        y="Value",
        color="Category",
        title="Survey Study Hours by Response",
        labels={"Response": "Response Number", "Value": "Hours Studied", "Category": "Course"},
    )
    scatter.update_xaxes(dtick=1)
    st.plotly_chart(scatter, use_container_width=True)
else:
    st.info("No survey responses match the chosen settings.")

show_statistics(
    csv_filtered["Value"],
    "csv",
    (st.session_state["csv_category"], st.session_state["csv_max_hours"], len(csv_df)),
)

