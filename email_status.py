import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import datetime


def month_num_to_name(month_num):
    return calendar.month_name[month_num]


# Load the data
df = pd.read_csv('email_status.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Streamlit app title
st.title("Dean's Email Status Dashboard")

# Add a file uploader and read the uploaded file
uploaded_file = st.file_uploader("Choose an updated CSV file", type=["csv"])

# If a file is uploaded, update the DataFrame
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    st.success("Data successfully uploaded!")

# Get the current year and month
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month
current_month_name = calendar.month_name[current_month]

# Sort and prepare the list of years and months
sorted_years = sorted(df['Year'].unique(), reverse=True)
sorted_months = [calendar.month_name[i] for i in sorted(df['Month'].unique(), reverse=True)]

# Find the index of the current year and month
index_current_year = sorted_years.index(current_year) if current_year in sorted_years else 0
index_current_month = sorted_months.index(current_month_name) if current_month_name in sorted_months else 0

# User control: Month and Year selection
selected_year = st.selectbox("Select Year:", sorted_years, index=index_current_year)
selected_month_name = st.selectbox("Select Month:", sorted_months, index=index_current_month)

# Convert month name back to month number for filtering
selected_month = list(calendar.month_name).index(selected_month_name)

# Initialize df_grouped as an empty DataFrame
df_grouped = pd.DataFrame()

# Filter the data based on the selected Month and Year
df_filtered = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

# Check if the filtered DataFrame is empty
if df_filtered.empty:
    st.error("Sorry, I cannot predict the future...")
else:
    # Group the data for the bar chart
    df_grouped = df_filtered.groupby(['Folder', 'Read Status']).agg({'Email Count': 'sum'}).reset_index()

# Any code here that uses df_grouped should be inside this if-statement
if not df_grouped.empty:

    # Create the bar chart
    fig, ax = plt.subplots()
    bottoms = {folder: 0 for folder in df_grouped['Folder'].unique()}
    colors = {'Read': 'g', 'Unread': 'r'}  # Green for Read, Red for Unread
    legend_added = set()

    for status in df_grouped['Read Status'].unique():
        subset = df_grouped[df_grouped['Read Status'] == status]
        for folder, email_count in zip(subset['Folder'], subset['Email Count']):
            label = status if status not in legend_added else ""
            ax.bar(folder, email_count, bottom=bottoms[folder], label=label, color=colors[status], alpha=0.7)
            bottoms[folder] += email_count  # Update the bottom for next stack

            # Add the total counts on top of the bars
            ax.text(folder, bottoms[folder], int(email_count), ha='center',
                    va='bottom')  # ha: horizontal alignment, va: vertical alignment

            if label:
                legend_added.add(status)

    # Customize the chart
    ax.set_xlabel('Folder')
    ax.set_ylabel('Email Count')
    ax.set_title(f'Email Status by Folder for {selected_month_name} {selected_year}')
    ax.legend(title='Read Status')

    # Show the chart in Streamlit
    st.pyplot(fig)

    # Add a separator line
    st.markdown("---")

    # Calculate Year-to-Date totals for each folder
    df_ytd = df[df['Year'] == selected_year]
    df_ytd_grouped = df_ytd.groupby(['Folder', 'Read Status']).agg({'Email Count': 'sum'}).reset_index()

    # Calculate YTD totals for each folder - Added for PIE chart
    df_ytd_folder = df_ytd.groupby(['Folder']).agg({'Email Count': 'sum'}).reset_index()

    # Create a pie chart
    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie(df_ytd_folder['Email Count'], labels=df_ytd_folder['Folder'], autopct='%1.1f%%', startangle=90)
    ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Calculate monthly totals from the start of the selected year to date
    df_monthly_totals = df[df['Year'] == selected_year].groupby(df['Date'].dt.month).agg(
        {'Email Count': 'sum'}).reset_index()
    df_monthly_totals['Month'] = df_monthly_totals['Date'].apply(month_num_to_name)  # Convert month numbers to names

    # Calculate the cumulative sum for the 'Email Count' column
    df_monthly_totals['Cumulative Email Count'] = df_monthly_totals['Email Count'].cumsum()

    # Create a line chart
    fig_line, ax_line = plt.subplots()
    ax_line.plot(df_monthly_totals['Month'], df_monthly_totals['Email Count'], marker='o')
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Total Email Count')
    ax_line.set_title(f'Monthly Email Totals for {selected_year}')

    # Arrange YTD table, pie chart side by side
    # Setting the middle column to be wider than the other two
    col1, col2 = st.columns([2, 2, ])

    # Show the YTD table in Streamlit
    col1.subheader(f'Year-to-Date Totals for {selected_year}')
    col1.write(df_ytd_grouped.set_index(['Folder', 'Read Status']))  # Display DataFrame without the index

    # Show the pie chart in Streamlit
    col2.subheader(f'Year-to-Date Percent Folder Distribution for {selected_year}')
    col2.pyplot(fig_pie)

    # Show the line chart in Streamlit
    # col3.subheader(f'Cumulative Monthly Email Totals for {selected_year}')
    # col3.pyplot(fig_line)
