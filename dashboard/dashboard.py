import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Membaca data bersih secara aman (berfungsi di lokal maupun Streamlit Cloud)
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data()

# Agregasi ke level harian untuk metrik & visualisasi harian
daily_df = df.groupby(by=["dteday", "season", "workingday", "weathersit"], as_index=False).agg({
    "temp": "mean",
    "casual": "sum",
    "registered": "sum",
    "cnt": "sum"
})

# Sidebar: Filter Interaktif Rentang Tanggal
min_date = daily_df["dteday"].min()
max_date = daily_df["dteday"].max()

with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.markdown("Filter Data Berdasarkan Rentang Waktu:")
    
    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menangani kondisi jika pengguna baru memilih 1 tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Filter dataframe harian & per jam berdasarkan tanggal yang dipilih
main_daily_df = daily_df[
    (daily_df["dteday"] >= pd.to_datetime(start_date)) & 
    (daily_df["dteday"] <= pd.to_datetime(end_date))
]

main_hourly_df = df[
    (df["dteday"] >= pd.to_datetime(start_date)) & 
    (df["dteday"] <= pd.to_datetime(end_date))
]

# Header Utama Dashboard
st.header("📊 Dashboard Analisis Penyewaan Sepeda (2011–2012)")
st.markdown(
    "Dashboard interaktif ini menyajikan eksplorasi pola peminjaman sepeda berdasarkan "
    "kondisi cuaca, musim, suhu udara, serta analisis lanjutan jam sibuk (*peak hours*)."
)

# Metrik / KPI Ringkasan
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = int(main_daily_df["cnt"].sum())
    st.metric("Total Peminjaman", value=f"{total_rentals:,}")
with col2:
    total_registered = int(main_daily_df["registered"].sum())
    st.metric("Penyewa Terdaftar (Registered)", value=f"{total_registered:,}")
with col3:
    total_casual = int(main_daily_df["casual"].sum())
    st.metric("Penyewa Biasa (Casual)", value=f"{total_casual:,}")

st.divider()

# Visualisasi Pertanyaan 1: Rata-rata Peminjaman Berdasarkan Cuaca & Hari Kerja
st.subheader("1. Rata-rata Peminjaman Harian Berdasarkan Kondisi Cuaca & Status Hari")
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="weathersit",
    y="cnt",
    hue="workingday",
    data=main_daily_df,
    estimator="mean",
    palette="Set2",
    errorbar=None,
    ax=ax1
)
ax1.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Cuaca dan Status Hari", fontsize=12, fontweight="bold")
ax1.set_xlabel("Kondisi Cuaca (1: Cerah, 2: Berawan/Mendung, 3: Hujan/Salju Ringan)")
ax1.set_ylabel("Rata-rata Jumlah Peminjaman per Hari")
ax1.set_xticks([0, 1, 2])
ax1.set_xticklabels(["Cerah (Clear)", "Berawan (Mist)", "Hujan (Light Snow)"])
ax1.legend(title="Status Hari", labels=["Libur / Weekend (0)", "Hari Kerja (1)"])
st.pyplot(fig1)

st.divider()

# Visualisasi Pertanyaan 2: Pola Musim dan Korelasi Suhu
st.subheader("2. Pola Peminjaman Berdasarkan Musim dan Korelasi Suhu Udara")
col_left, col_right = st.columns(2)

with col_left:
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    sns.barplot(
        x="season",
        y="cnt",
        data=main_daily_df,
        estimator="sum",
        palette="viridis",
        errorbar=None,
        ax=ax2
    )
    ax2.set_title("Total Akumulasi Peminjaman Berdasarkan Musim", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Musim")
    ax2.set_ylabel("Total Akumulasi Peminjaman")
    ax2.set_xticks([0, 1, 2, 3])
    ax2.set_xticklabels(["Spring", "Summer", "Fall", "Winter"])
    st.pyplot(fig2)

with col_right:
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        x="temp",
        y="registered",
        data=main_daily_df,
        alpha=0.6,
        color="steelblue",
        ax=ax3
    )
    sns.regplot(
        x="temp",
        y="registered",
        data=main_daily_df,
        scatter=False,
        color="crimson",
        ax=ax3
    )
    ax3.set_title("Korelasi Suhu (Temp) vs Penyewa Terdaftar", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Suhu Dinormalisasi (Temp)")
    ax3.set_ylabel("Penyewa Terdaftar (Registered)")
    st.pyplot(fig3)

st.divider()

# Visualisasi Analisis Lanjutan: Jam Sibuk (Peak Hours)
st.subheader("3. Analisis Lanjutan: Tren Peminjaman Berdasarkan Jam (Peak Hours)")
hourly_trend = main_hourly_df.groupby(by=["hr", "workingday"])["cnt"].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(12, 5))
sns.lineplot(
    x="hr",
    y="cnt",
    hue="workingday",
    data=hourly_trend,
    marker="o",
    palette="tab10",
    linewidth=2.5,
    ax=ax4
)
ax4.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Jam dalam Sehari", fontsize=12, fontweight="bold")
ax4.set_xlabel("Jam (0 - 23)")
ax4.set_ylabel("Rata-rata Jumlah Peminjaman")
ax4.set_xticks(range(0, 24))
ax4.legend(title="Status Hari", labels=["Libur / Weekend (0)", "Hari Kerja (1)"])
ax4.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig4)