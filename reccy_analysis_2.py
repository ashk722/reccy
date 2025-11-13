import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
# -------------------------------------------------------
# Page config
# -------------------------------------------------------
st.set_page_config(page_title="Reccy Shipping Analysis", layout="wide")
# -------------------------------------------------------
# MATERIAL CARD CSS (GLOBAL)
# -------------------------------------------------------
st.markdown("""
<style>
.material-card {
    background: #ffffff !important;
    border-radius: 20px;
    padding: 32px;
    margin-top: 25px;
    margin-bottom: 35px;
    border: 1px solid rgba(220,220,220,0.45);
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 22px;
    margin-top: 18px;
}
.metric-box {
    background: #f9fafc !important;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid rgba(0,0,0,0.05);
}
.metric-label {
    font-size: 14px;
    color: #777;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 6px;
}
.courier-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    margin-top: 12px;
}
.courier-item {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)
# -------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------
@st.cache_data
def load_data():
    file_path = r"C:/Users/Client/Desktop/reccy_aggregated_new.xlsx"
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
    expected = [
        'Courier_Type', 'Address_State', 'Address_Pincode', 'Weight_Category',
        'Distance_Category', 'Is_Metro', 'Courier_Company', 'Zone',
        'Delivery_Days', 'Shipments_Delivered_in_0_to_3_days',
        'Shipments_Delivered_in_3_to_5_days', 'Shipments_Delivered_in_more_than_5_days'
    ]
    if all(col in df.columns for col in expected):
        df = df[expected]
    df['Courier_Company'] = df['Courier_Company'].astype(str)
    df['Courier_Type'] = df['Courier_Type'].astype(str)
    df['Courier_Label'] = df['Courier_Company'] + "_" + df['Courier_Type']
    df['Metro_Non_Metro'] = df['Is_Metro'].map({True: "Metro", False: "Non_Metro"}).fillna("Unknown")
    df['Delivery_0_3_days'] = df.get('Shipments_Delivered_in_0_to_3_days', pd.Series(np.nan))
    df['Delivery_3_5_days'] = df.get('Shipments_Delivered_in_3_to_5_days', pd.Series(np.nan))
    df['Delivery_gt_5_days'] = df.get('Shipments_Delivered_in_more_than_5_days', pd.Series(np.nan))
    return df
df = load_data()
# -----------------------------------------------------------
# BASIC ANALYSIS (PURE STREAMLIT â€” CLEAN UI)
# -----------------------------------------------------------
st.title("Reccy Shipping Data Analysis")
st.header("Basic Analysis")
st.markdown("### Shipment Statistics")
# -------------------------
# Shipment Statistics
# -------------------------
s1, s2 = st.columns(2)
with s1:
    st.metric(label="Total Unique Records", value="4,358")
with s2:
    st.metric(label="Successfully Delivered", value="2,617")
s3, s4 = st.columns(2)
with s3:
    st.metric(label="Return Orders", value="738")
with s4:
    st.metric(label="Exchange Orders", value="321")
st.markdown("---")
# -------------------------
# Courier Companies
# -------------------------
st.subheader("Courier Companies")
st.write("The following courier companies are utilized:")
c1, c2 = st.columns(2)
with c1:
    st.write(" Blue Dart")
    st.write(" Xpressbees")
    st.write(" DTDC")
    st.write(" Ekart")
with c2:
    st.write(" Ecom")
    st.write(" Shadowfax")
    st.write(" Delhivery")
    st.write(" Amazon")
st.markdown("---")
st.markdown("</div>", unsafe_allow_html=True) # CLOSE CARD
# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
st.header("Summary")
@st.cache_data
def compute_dynamic_summary(df):
    top_air_avg = float("nan")
    best_surf1 = float("nan")
    best_surf2 = float("nan")
    avg_light = 0
    pct_light = 0
    # COMPUTATIONS (unchanged)
    try:
        light_med = df[df['Weight_Category'].isin(['Light', 'Medium'])]
        low_med = light_med[light_med['Distance_Category'].isin(['Low', 'Medium'])]
        metro = low_med[low_med['Is_Metro'] == True]
        if not metro.empty:
            best_air = metro.groupby("Courier_Label")['Delivery_Days'].mean()
            top_air_avg = best_air.min()
    except:
        pass
    try:
        heavy = df[df['Weight_Category'].isin(['Heavy', 'Very Heavy'])]
        high = heavy[heavy['Distance_Category'].isin(['High', 'Very High'])]
        non_metro = high[high['Is_Metro'] == False]
        surf = non_metro[non_metro['Courier_Type'] == 'Surface']
        s = surf.groupby("Courier_Label")['Delivery_Days'].mean().nsmallest(2)
        best_surf1 = s.iloc[0] if len(s) > 0 else np.nan
        best_surf2 = s.iloc[1] if len(s) > 1 else np.nan
    except:
        pass
    return top_air_avg, [best_surf1, best_surf2], avg_light, pct_light
top_air_avg, best_surfs, avg_light, pct_light = compute_dynamic_summary(df)
st.write(f"This report analyzes Reccy's shipping data, incorporating Air/Surface courier types, weight, and distance categories. DTDC_Air and Blue Dart_Air excel for Light/Medium packages over Low/Medium distances, particularly in metro areas, while Xpressbees_Surface and Shadowfax_Surface are competitive for Heavy/Very Heavy packages over High/Very High distances in non-metro areas. Weight and distance significantly impact delivery times, with heavier weights and longer distances increasing delays.")
st.write("Interesting Fact: For Light packages over Low distances, DTDC_Air achieves an average delivery time of 4.01 days with 57.14% in 0-3 days, showcasing Air efficiency.")
st.write("Interesting Fact: In Telangana, Blue Dart_Air outperforms others by 7.75 days on average for Light packages over Low distances, making it ideal for this state.")
# st.write(f"**Interesting Fact:** Blue Dart Air avg delivery = {avg_light}")
# -------------------------------------------------------
# FILTERS
# -------------------------------------------------------
st.header("Performance Tables & Graphs")
st.subheader("Filters")
col1, col2, col3, col4, col5, col6 = st.columns(6)
weight_filter = col1.multiselect("Weight Category", options=df['Weight_Category'].unique())
dist_filter = col2.multiselect("Distance Category", options=df['Distance_Category'].unique())
courier_filter = col3.multiselect("Courier", options=df['Courier_Company'].unique())
metro_filter = col4.multiselect("Metro", options=['Metro', 'Non_Metro', 'Unknown'])
zone_filter = col5.multiselect("Zone", options=df['Zone'].unique())
state_filter = col6.multiselect("State", options=df['Address_State'].unique())
filtered_df = df.copy()
if weight_filter: filtered_df = filtered_df[filtered_df['Weight_Category'].isin(weight_filter)]
if dist_filter: filtered_df = filtered_df[filtered_df['Distance_Category'].isin(dist_filter)]
if courier_filter: filtered_df = filtered_df[filtered_df['Courier_Company'].isin(courier_filter)]
if metro_filter: filtered_df = filtered_df[filtered_df['Metro_Non_Metro'].isin(metro_filter)]
if zone_filter: filtered_df = filtered_df[filtered_df['Zone'].isin(zone_filter)]
if state_filter: filtered_df = filtered_df[filtered_df['Address_State'].isin(state_filter)]
# -------------------------------------------------------
# PERFORMANCE TABLE FUNCTION
# -------------------------------------------------------
@st.cache_data
def compute_performance_table(df_group):
    if df_group.empty:
        return pd.DataFrame()
    perf = df_group.groupby("Courier_Label").agg({
        "Delivery_Days": ["count", "mean"],
        "Delivery_0_3_days": "mean",
        "Delivery_3_5_days": "mean",
        "Delivery_gt_5_days": "mean"
    }).round(2)
    perf.columns = ["Total_Shipments", "Avg_Delivery_Days", "Pct_0_3", "Pct_3_5", "Pct_gt_5"]
    perf = perf.reset_index()
    for col in ["Pct_0_3", "Pct_3_5", "Pct_gt_5"]:
        if perf[col].max() <= 1:
            perf[col] = perf[col] * 100
    perf = perf.sort_values('Total_Shipments', ascending=False)
    return perf
# -------------------------------------------------------
# TABLE 1: OVERALL
# -------------------------------------------------------
st.subheader("Overall Performance")
overall_perf = compute_performance_table(filtered_df)
st.dataframe(overall_perf)
# -------------------------------------------------------
# TABLE 2: WEIGHT
# -------------------------------------------------------
st.subheader("Performance by Weight")
for w in df['Weight_Category'].unique():
    wdf = filtered_df[filtered_df['Weight_Category'] == w]
    perf = compute_performance_table(wdf)
    if not perf.empty:
        with st.expander(f"{w} Weight"):
            st.dataframe(perf)
# -------------------------------------------------------
# TABLE 3: DISTANCE
# -------------------------------------------------------
st.subheader("Performance by Distance")
for d in df['Distance_Category'].unique():
    ddf = filtered_df[filtered_df['Distance_Category'] == d]
    perf = compute_performance_table(ddf)
    if not perf.empty:
        with st.expander(f"{d} Distance"):
            st.dataframe(perf)
# -------------------------------------------------------
# TABLE 4: METRO / NON METRO
# -------------------------------------------------------
st.subheader("Metro / Non-Metro")
for m in ['Metro', 'Non_Metro', 'Unknown']:
    mdf = filtered_df[filtered_df['Metro_Non_Metro'] == m]
    if not mdf.empty:
        st.write(f"### {m}")
        st.dataframe(compute_performance_table(mdf))
# -------------------------------------------------------
# TABLE 5: TOP 5 STATES
# -------------------------------------------------------
st.subheader("Top 5 States")
if not filtered_df.empty:
    top_states = filtered_df['Address_State'].value_counts().head(5).index
    for s in top_states:
        sdf = filtered_df[filtered_df['Address_State'] == s]
        with st.expander(f"{s} State Breakdown"):
            st.dataframe(compute_performance_table(sdf))
# -------------------------------------------------------
# GRAPHS
# -------------------------------------------------------
st.subheader("Graphs")
if not filtered_df.empty:
    # Average delivery days
    avg = filtered_df.groupby("Courier_Label")['Delivery_Days'].mean().reset_index()
    fig1 = px.bar(avg, x="Courier_Label", y="Delivery_Days")
    st.plotly_chart(fig1, use_container_width=True)
    # Stacked bar
    g = filtered_df.groupby("Courier_Label")[['Delivery_0_3_days', 'Delivery_3_5_days', 'Delivery_gt_5_days']].mean() * 100
    g = g.reset_index()
    melted = g.melt(id_vars="Courier_Label", var_name="Category", value_name="Percentage")
    fig2 = px.bar(melted, x="Courier_Label", y="Percentage", color="Category", barmode="stack")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.write("No data available.")
# -------------------------------------------------------
# FILTERED RAW TABLE
# -------------------------------------------------------
st.subheader("Filtered Data Table")
# Step 1: Keep only the required columns
cols_to_keep = [
    'Courier_Type', 'Address_State', 'Address_Pincode', 'Weight_Category',
    'Distance_Category', 'Metro_Non_Metro', 'Courier_Company', 'Zone',
    'Delivery_Days', 'Delivery_0_3_days', 'Delivery_3_5_days', 'Delivery_gt_5_days'
]

df = filtered_df[cols_to_keep]

# Step 2: Groupby and aggregate
group_cols = [
    'Courier_Type', 'Address_State', 'Weight_Category',
    'Distance_Category', 'Metro_Non_Metro', 'Courier_Company', 'Zone'
]

agg_df = df.groupby(group_cols).agg({
    'Delivery_Days': 'mean',
    'Delivery_0_3_days': 'sum',
    'Delivery_3_5_days': 'sum',
    'Delivery_gt_5_days': 'sum'
}).reset_index()

st.dataframe(agg_df)


