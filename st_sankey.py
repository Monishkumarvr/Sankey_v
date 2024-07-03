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
end_date = st.date_input('End date', df['r_date'].max().date())

# Ensure end_date is not before start_date
if start_date > end_date:
    st.error('Error: End date must fall after start date.')
else:
    # Filter dataframe by date range
    filtered_df = df[(df['r_date'] >= pd.to_datetime(start_date)) & (df['r_date'] <= pd.to_datetime(end_date))]

    # Dropdown for selecting customer
    selected_customer = st.selectbox(
        'Select Customer',
        filtered_df['company_name'].unique()
    )

    filtered_df = filtered_df[filtered_df['company_name'] == selected_customer]

    # Prepare the base numbers
    num_ids = filtered_df['id'].nunique()
    num_control_plan = filtered_df[filtered_df['control_plan'].notna()]['id'].nunique()
    num_no_control_plan = num_ids - num_control_plan
    num_supplier_name = filtered_df[filtered_df['supplier_name'].notna()]['id'].nunique()
    num_price = filtered_df[filtered_df['price'].notna()]['id'].nunique()

    # Split under control plan
    num_control_plan_accepted = filtered_df[(filtered_df['control_plan'].notna()) & (filtered_df['status_accepted'].notna())]['id'].nunique()
    num_control_plan_rejected = filtered_df[(filtered_df['control_plan'].notna()) & (filtered_df['status_rejected'].notna())]['id'].nunique()
    num_control_plan_not_attended = filtered_df[(filtered_df['control_plan'].notna()) & (filtered_df['status_not_attended'].notna())]['id'].nunique()

    # Split under no control plan
    num_no_control_plan_accepted = filtered_df[(filtered_df['control_plan'].isna()) & (filtered_df['status_accepted'].notna())]['id'].nunique()
    num_no_control_plan_rejected = filtered_df[(filtered_df['control_plan'].isna()) & (filtered_df['status_rejected'].notna())]['id'].nunique()
    num_no_control_plan_not_attended = filtered_df[(filtered_df['control_plan'].isna()) & (filtered_df['status_not_attended'].notna())]['id'].nunique()

    # Split under supplier name
    num_supplier_name_accepted = filtered_df[(filtered_df['supplier_name'].notna()) & (filtered_df['status_accepted'].notna())]['id'].nunique()
    num_supplier_name_rejected = filtered_df[(filtered_df['supplier_name'].notna()) & (filtered_df['status_rejected'].notna())]['id'].nunique()
    num_supplier_name_not_attended = filtered_df[(filtered_df['supplier_name'].notna()) & (filtered_df['status_not_attended'].notna())]['id'].nunique()

    # Split under price
    num_price_accepted = filtered_df[(filtered_df['price'].notna()) & (filtered_df['status_accepted'].notna())]['id'].nunique()
    num_price_rejected = filtered_df[(filtered_df['price'].notna()) & (filtered_df['status_rejected'].notna())]['id'].nunique()
    num_price_not_attended = filtered_df[(filtered_df['price'].notna()) & (filtered_df['status_not_attended'].notna())]['id'].nunique()

    # Split under no price
    num_no_price_accepted = filtered_df[(filtered_df['price'].isna()) & (filtered_df['status_accepted'].notna())]['id'].nunique()
    num_no_price_rejected = filtered_df[(filtered_df['price'].isna()) & (filtered_df['status_rejected'].notna())]['id'].nunique()
    num_no_price_not_attended = filtered_df[(filtered_df['price'].isna()) & (filtered_df['status_not_attended'].notna())]['id'].nunique()

    # Combined data for Sankey diagram
    sankey_combined_data = {
        "source": [
            0, 0,  # Total IDs to Control Plan/No Control Plan
            1, 1,  # Control Plan to Supplier Name/No Supplier Name
            2, 2, 2,  # No Control Plan to Accepted/Rejected/Not Attended
            1, 1, 1,  # Control Plan to Accepted/Rejected/Not Attended
            3, 3,  # Supplier Name to Price/No Price
            5, 5, 5,  # Price to Accepted/Rejected/Not Attended
            6, 6, 6,  # No Price to Accepted/Rejected/Not Attended
        ],
        "target": [
            1, 2,  # Total IDs to Control Plan/No Control Plan
            3, 4,  # Control Plan to Supplier Name/No Supplier Name
            7, 8, 9,  # No Control Plan to Accepted/Rejected/Not Attended
            7, 8, 9,  # Control Plan to Accepted/Rejected/Not Attended
            5, 6,  # Supplier Name to Price/No Price
            7, 8, 9,  # Price to Accepted/Rejected/Not Attended
            7, 8, 9,  # No Price to Accepted/Rejected/Not Attended
        ],
        "value": [
            num_control_plan, num_no_control_plan,  # Total IDs to Control Plan/No Control Plan
            num_supplier_name, num_control_plan - num_supplier_name,  # Control Plan to Supplier Name/No Supplier Name
            num_no_control_plan_accepted, num_no_control_plan_rejected, num_no_control_plan_not_attended,  # No Control Plan to Accepted/Rejected/Not Attended
            num_control_plan_accepted, num_control_plan_rejected, num_control_plan_not_attended,  # Control Plan to Accepted/Rejected/Not Attended
            num_price, num_supplier_name - num_price,  # Supplier Name to Price/No Price
            num_price_accepted, num_price_rejected, num_price_not_attended,  # Price to Accepted/Rejected/Not Attended
            num_no_price_accepted, num_no_price_rejected, num_no_price_not_attended  # No Price to Accepted/Rejected/Not Attended
        ]
    }

    labels = [
        "Total IDs", "Control Plan", "No Control Plan", 
        "Supplier Name", "No Supplier Name", "Price", "No Price",
        "Accepted", "Rejected", "Not Attended"
    ]

    # Create the combined Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=labels,
            color=["blue", "green", "red", "green", "red", "green", "red", "green", "red", "grey"]
        ),
        link=dict(
            source=sankey_combined_data['source'],
            target=sankey_combined_data['target'],
            value=sankey_combined_data['value'],
            hovertemplate='Value: %{value}<extra></extra>',
        )
    )])

    # Update layout for better spacing
    fig.update_layout(
        title_text="Sankey Diagram of QC Data",
        font_size=10,
        width=1000,
        height=700,
    )

    st.plotly_chart(fig)
