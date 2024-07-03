import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Load data
file_path = 'Quality Report Analytics - Main List.csv'
df = pd.read_csv(file_path)

# Convert date column to datetime
df['r_date'] = pd.to_datetime(df['r_date'], format="%d-%m-%Y")

# Streamlit app
st.title('Sankey Diagram for QC Data')

# Date filter
start_date = st.date_input('Start date', df['r_date'].min().date())
start_date = pd.to_datetime(start_date, format="%d-%m-%Y")
start_date = start_date.strftime('%d-%m-%Y')
end_date = st.date_input('End date', df['r_date'].max().date())
end_date = pd.to_datetime(end_date, format="%d-%m-%Y")
end_date = end_date.strftime('%d-%m-%Y')

# Ensure end_date is not before start_date
if start_date > end_date:
    st.error('Error: End date must fall after start date.')
else:
    # Filter dataframe by date range
    filtered_df = df[(df['r_date'] >= start_date) & (df['r_date'] <= end_date)]

    # Add "All" option to company name dropdown
    company_names = ['All'] + list(filtered_df['company_name'].unique())

    # Dropdown for selecting customer
    selected_customers = st.selectbox(
        'Select Customer',
        company_names
    )

    if 'All' not in selected_customers:
        filtered_df = filtered_df[filtered_df['company_name']==selected_customers]

    # Prepare the base numbers
    num_ids = filtered_df['id'].nunique()
    num_control_plan = filtered_df[filtered_df['control_plan'].notna()]['id'].nunique()
    num_no_control_plan = num_ids - num_control_plan
    ncpdf = filtered_df[filtered_df['control_plan'].notna()]
    nncpdf = filtered_df[filtered_df['control_plan'].isna()]
    num_supplier_name = ncpdf[ncpdf['supplier_name'].notna()]['id'].nunique()
    num_no_supplier_name = num_control_plan - num_supplier_name
    num_ncp_supplier_name = nncpdf[nncpdf['supplier_name'].notna()]['id'].nunique()
    num_ncp_no_supplier_name = num_no_control_plan - num_ncp_supplier_name

    # Split under control plan
    num_control_plan_accepted = ncpdf[(ncpdf['status_accepted'].notna())]['id'].nunique()
    num_control_plan_rejected = ncpdf[(ncpdf['status_rejected'].notna())]['id'].nunique()
    num_control_plan_not_attended = ncpdf[(ncpdf['status_not_attended'].notna())]['id'].nunique()

    # Split under no control plan
    num_no_control_plan_accepted = nncpdf[(nncpdf['status_accepted'].notna())]['id'].nunique()
    num_no_control_plan_rejected = nncpdf[(nncpdf['status_rejected'].notna())]['id'].nunique()
    num_no_control_plan_not_attended = nncpdf[(nncpdf['status_not_attended'].notna())]['id'].nunique()

    # Flow 1 data for Sankey diagram
    sankey_flow1_data = {
        "source": [0, 0, 1, 1, 2, 2],
        "target": [1, 2, 3, 4, 5, 6],
        "value": [num_control_plan, num_no_control_plan, num_supplier_name, num_no_supplier_name, num_ncp_supplier_name, num_ncp_no_supplier_name]
    }

    labels_flow1 = [
        "Total IDs", "Control Plan", "No Control Plan",
        "Supplier Name", "No Supplier Name", "Supplier Name", "No Supplier Name"
    ]

    # Flow 2 data for Sankey diagram
    sankey_flow2_data = {
        "source": [0, 0, 1, 1, 1, 2, 2, 2],
        "target": [1, 2, 3, 4, 5, 6, 7, 8],
        "value": [
            num_control_plan, num_no_control_plan,
            num_control_plan_accepted, num_control_plan_rejected, num_control_plan_not_attended,
            num_no_control_plan_accepted, num_no_control_plan_rejected, num_no_control_plan_not_attended
        ]
    }

    labels_flow2 = [
        "Total IDs", "Control Plan", "No Control Plan",
        "Accepted", "Rejected", "Not Attended",
        "Accepted", "Rejected", "Not Attended"
    ]

    # Create the Sankey diagram for Flow 1
    fig_flow1 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=labels_flow1,
            color="blue"
        ),
        link=dict(
            source=sankey_flow1_data['source'],
            target=sankey_flow1_data['target'],
            value=sankey_flow1_data['value'],
            hovertemplate='Value: %{value}<extra></extra>',
        )
    )])

    # Create the Sankey diagram for Flow 2
    fig_flow2 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=labels_flow2,
            color="green"
        ),
        link=dict(
            source=sankey_flow2_data['source'],
            target=sankey_flow2_data['target'],
            value=sankey_flow2_data['value'],
            hovertemplate='Value: %{value}<extra></extra>',
        )
    )])

    # Update layout for better spacing
    fig_flow1.update_layout(
        title_text="Flow 1: Control Plan, Supplier Name, and Price",
        font_size=10,
        width=1000,
        height=700,
    )

    fig_flow2.update_layout(
        title_text="Flow 2: Control Plan and Status",
        font_size=10,
        width=1000,
        height=700,
    )

    st.plotly_chart(fig_flow1)
    st.plotly_chart(fig_flow2)
