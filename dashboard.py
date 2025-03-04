import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
from babel.numbers import format_currency
sns.set(style = "white")

# Load data
all_df = pd.read_csv("all_data.csv")

## Kode di bawah ini digunakan untuk analisis RFM
# Pastikan kolom tanggal dalam format datetime
if 'order_purchase_timestamp' in all_df.columns:
    all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'], errors='coerce')
    all_df = all_df.dropna(subset=['order_purchase_timestamp'])  # Hapus baris dengan tanggal NaT
else:
    st.error("Kolom order_purchase_timestamp tidak ditemukan dalam dataset.")
    st.stop()

# Tentukan tanggal referensi
latest_date = all_df['order_purchase_timestamp'].max()

# Gunakan kolom alternatif jika 'payment_value' tidak ada
monetary_column = "price" if "price" in all_df.columns else None

if monetary_column is None:
    st.error("Tidak ditemukan kolom yang bisa digunakan untuk perhitungan Monetary (contoh: 'payment_value' atau 'price').")
    st.stop()

# Fungsi perhitungan RFM
def calculate_rfm(data, latest_date, monetary_col):
    if not {'customer_unique_id', 'order_purchase_timestamp', 'order_id'}.issubset(data.columns):
        st.error("Kolom yang dibutuhkan untuk analisis RFM tidak ditemukan.")
        st.stop()
    
    # Hapus NaN pada kolom yang digunakan
    data = data.dropna(subset=['customer_unique_id', 'order_id', monetary_col])
    
    rfm_df = data.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
        'order_id': 'nunique',
        monetary_col: 'sum'
    }).reset_index()
    
    rfm_df.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        monetary_col: 'Monetary'
    }, inplace=True)
    
    return rfm_df

# Fungsi untuk visualisasi histogram dan boxplot
def plot_hist_box(data, column, color, x_label, y_label):
    if column not in data.columns:
        st.error(f"Kolom {column} tidak ditemukan dalam dataset RFM.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Distribusi {column}")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(data[column], bins=30, kde=True, color=color, edgecolor="black", ax=ax)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        st.pyplot(fig)
    
    with col2:
        st.subheader(f"Boxplot {column}")
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.boxplot(y=data[column], color=color, ax=ax)
        ax.set_ylabel(x_label)
        st.pyplot(fig)

# Membuat sidebar
with st.sidebar:
    # Menambahkan logo  
    st.image("Assets/logo.png")

# Membuat Dashboard Visualisasi Data 
st.header("Brazilian E-Commerce Public Dataset by Olist")

# Membuat tab untuk masing-masing pertanyaan dan analisis RFM
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Pertanyaan 1", 
    "Pertanyaan 2", 
    "Pertanyaan 3", 
    "Pertanyaan 4", 
    "Analisis RFM"
])

# Tab 1: Kota dengan Order Terbanyak
with tab1:
    st.header("Kota dengan Order Terbanyak dan Terdikit")

    # Menghitung jumlah order per kota pelanggan
    city_order_counts = all_df.groupby("customer_city")["order_id"].nunique()

    # Mengambil 5 kota dengan order terbanyak dan 5 kota dengan order tersedikit
    top_5_cities = city_order_counts.nlargest(5)
    bottom_5_cities = city_order_counts.nsmallest(5)
    # Membuat dua kolom (kiri dan kanan)
    col1, col2 = st.columns(2)

    # Visualisasi 5 kota dengan order terbanyak (di kiri)
    with col1:
        st.subheader("5 Kota dengan Order Terbanyak")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.bar(top_5_cities.index, top_5_cities.values, color="blue")
        ax1.set_xlabel("Kota")
        ax1.set_ylabel("Jumlah Order")
        ax1.set_title("Order Terbanyak")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # Visualisasi 5 kota dengan order tersedikit (di kanan)
    with col2:
        st.subheader("5 Kota dengan Order Terdikit")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(bottom_5_cities.index, bottom_5_cities.values, color="red")
        ax2.set_xlabel("Kota")
        ax2.set_ylabel("Jumlah Order")
        ax2.set_title("Order Tersedikit")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    # Membuat Expander Penjelasan
    with st.expander("Lihat Penjelasan"):
        st.write("Kota dengan jumlah transaksi terbanyak mencerminkan area dengan tingkat belanja online yang tinggi, biasanya dipengaruhi oleh faktor seperti jumlah penduduk, aksesibilitas e-commerce, dan daya beli masyarakat. Sebaliknya, kota dengan jumlah transaksi terendah bisa jadi memiliki keterbatasan dalam infrastruktur digital, preferensi belanja konvensional, atau daya beli yang lebih rendah. Kota dengan order terbanyak menunjukkan peluang pasar yang besar, sedangkan kota dengan order terendah dapat menjadi target pemasaran strategis untuk meningkatkan penetrasi e-commerce.")

# Tab 2: Kategori Produk Paling Banyak Dibeli
with tab2:
    st.header("Kategori Produk Paling Banyak Dibeli")
    # Menghitung jumlah produk yang terjual berdasarkan kategori
    category_counts = all_df.groupby("product_category_name")["order_id"].nunique()

    # Mengambil 5 kategori dengan jumlah produk terbanyak
    top_5_categories = category_counts.nlargest(5)

    # Membuat figure untuk visualisasi
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(top_5_categories.index, top_5_categories.values, color="green")
    ax.set_xlabel("Kategori Produk")
    ax.set_ylabel("Jumlah Order")
    ax.set_title("Top 5 Kategori Produk Paling Banyak Dibeli")
    plt.xticks(rotation=45)

    # Menampilkan plot di Streamlit
    st.pyplot(fig)

    # Membuat Expander Penjelasan
    with st.expander("Lihat Penjelasan"):
        st.write("Kategori produk dengan jumlah transaksi tertinggi mencerminkan kebutuhan utama pelanggan di marketplace ini, yang dapat dipengaruhi oleh tren pasar, preferensi konsumen, serta faktor musiman. Produk dengan permintaan tinggi ini menunjukkan kategori yang paling diminati dan memiliki potensi keuntungan besar bagi penjual. Di sisi lain, kategori dengan jumlah transaksi rendah bisa menjadi peluang pasar yang belum tergarap secara optimal. Faktor seperti kurangnya eksposur, harga yang kurang kompetitif, atau keterbatasan pasokan dapat memengaruhi rendahnya transaksi pada kategori ini. Dengan strategi pemasaran yang tepat, seperti peningkatan promosi, penyesuaian harga, atau edukasi pelanggan, kategori ini berpotensi untuk berkembang dan menarik lebih banyak pembeli.")

# Tab 3: Kategori dengan Omset Terbesar
with tab3:
    st.header("Produk dengan Omset Terbesar dan Terkecil")

    # Menghitung total omset berdasarkan produk
    product_revenue = all_df.groupby("product_category_name")["price"].sum()

    # Mengambil 5 produk dengan omset terbesar
    top_5_products = product_revenue.nlargest(5)

    # Mengambil 5 produk dengan omset terkecil
    bottom_5_products = product_revenue.nsmallest(5)

    # Membuat layout 2 kolom
    col1, col2 = st.columns(2)

    # Visualisasi Produk dengan Omset Terbesar
    with col1:
        st.subheader("Top 5 Produk dengan Omset Terbesar")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.barh(top_5_products.index, top_5_products.values, color="green")
        ax1.set_xlabel("Total Omset (BRL)")
        ax1.set_ylabel("Kategori Produk")
        ax1.set_title("Top 5 Omset Terbesar")
        ax1.invert_yaxis()  # Membalik sumbu Y agar omset terbesar ada di atas
        st.pyplot(fig1)

    # Visualisasi Produk dengan Omset Terkecil
    with col2:
        st.subheader("Top 5 Produk dengan Omset Terkecil")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(bottom_5_products.index, bottom_5_products.values, color="red")
        ax2.set_xlabel("Total Omset (BRL)")
        ax2.set_ylabel("Kategori Produk")
        ax2.set_title("Top 5 Omset Terkecil")
        st.pyplot(fig2)

    # Membuat Expander Penjelasan
    with st.expander("Lihat Penjelasan"):
        st.write("Kategori dengan omzet tertinggi tidak selalu berasal dari kategori dengan jumlah transaksi terbanyak, karena beberapa produk memiliki harga rata-rata yang lebih tinggi sehingga menghasilkan omzet besar meskipun jumlah transaksinya lebih sedikit. Sebaliknya, kategori dengan transaksi tertinggi biasanya terdiri dari produk dengan harga lebih terjangkau yang dibeli dalam jumlah besar. Pemahaman ini penting bagi penjual untuk menentukan strategi, apakah fokus pada volume penjualan tinggi dengan margin kecil atau produk premium dengan margin lebih besar.")

# Tab 4: Penjual dengan Order Terbanyak (Pareto Chart)
with tab4:
    st.header("Penjual dengan Order Terbanyak (Pareto Chart)")

    # Menghitung jumlah order berdasarkan seller
    seller_order_counts = all_df.groupby("seller_id")["order_id"].nunique().sort_values(ascending=False)

    # Mengambil 10 penjual dengan order terbanyak
    top_10_sellers = seller_order_counts[:10]

    # Menghitung persentase kumulatif
    cumulative_percentage = top_10_sellers.cumsum() / top_10_sellers.sum() * 100

    # Membuat figure dan axes
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Membuat bar chart (jumlah order per seller)
    ax1.bar(top_10_sellers.index, top_10_sellers.values, color="blue", alpha=0.6, label="Jumlah Order")
    ax1.set_xlabel("Seller ID")
    ax1.set_ylabel("Jumlah Order", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Memutar label sumbu X sebesar 45 derajat
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')

    # Membuat line chart (persentase kumulatif)
    ax2 = ax1.twinx()
    ax2.plot(top_10_sellers.index, cumulative_percentage, color="red", marker="o", linestyle="-", label="Persentase Kumulatif")
    ax2.set_ylabel("Persentase Kumulatif (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Menambahkan grid dan legenda
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # Menampilkan chart di Streamlit
    st.pyplot(fig)

    # Membuat Expander Penjelasan
    with st.expander("Lihat Penjelasan"):
        st.write("Sebanyak 20% penjual teratas berkontribusi terhadap hampir 80% dari total order, sesuai dengan Prinsip Pareto yang menunjukkan bahwa sebagian besar transaksi berasal dari sejumlah kecil penjual. Hal ini mengindikasikan bahwa penjual dengan strategi pemasaran yang kuat, produk berkualitas, dan layanan pelanggan yang baik cenderung mendominasi pasar. Sementara itu, penjual dengan kontribusi kecil dapat meningkatkan daya saingnya dengan mengoptimalkan strategi pemasaran, memperluas jangkauan produk, serta meningkatkan kualitas layanan untuk menarik lebih banyak pelanggan.")
# Tab 5: Analisis RFM
with tab5:
    st.header("Analisis RFM (Recency, Frequency, Monetary)")

    # Hitung RFM dengan validasi
    rfm_df = calculate_rfm(all_df, latest_date, monetary_column)
    if rfm_df.empty:
        st.error("Tidak ada data yang tersedia untuk analisis RFM.")
        st.stop()

    # Validasi apakah kolom RFM ada sebelum visualisasi
    required_columns = ["Recency", "Frequency", "Monetary"]
    if not all(col in rfm_df.columns for col in required_columns):
        st.error("Beberapa kolom RFM tidak ditemukan. Cek kembali proses perhitungan RFM.")
        st.stop()

    # Visualisasi RFM
    st.markdown("""<h3 style='color: cyan;'>Analisis Recency</h3>""", unsafe_allow_html=True)
    plot_hist_box(rfm_df, "Recency", "skyblue", "Hari Sejak Pembelian Terakhir", "Jumlah Pelanggan")
    # Untuk membuat expander
    with st.expander("Lihat Penjelasan"):
        st.write("Sebagian besar pelanggan baru saja melakukan pembelian, yang berarti mereka lebih mungkin untuk kembali berbelanja jika diberikan rekomendasi produk yang relevan atau penawaran khusus. Di sisi lain, ada juga pelanggan yang sudah lama tidak bertransaksi, sehingga diperlukan strategi retensi seperti email pengingat, diskon eksklusif, atau program loyalitas untuk menarik mereka kembali. Dengan segmentasi pelanggan yang tepat, perusahaan dapat mengoptimalkan strategi pemasaran guna meningkatkan repeat order serta mempertahankan pelanggan dalam jangka panjang.")

    st.markdown("""<h3 style='color: cyan;'>Analisis Frequency</h3>""", unsafe_allow_html=True)
    plot_hist_box(rfm_df, "Frequency", "lightgreen", "Jumlah Transaksi", "Jumlah Pelanggan")
    # Untuk membuat expander
    with st.expander("Lihat Penjelasan"):
        st.write("Sebagian besar pelanggan hanya berbelanja sekali dalam setahun, sehingga diperlukan strategi untuk meningkatkan frekuensi transaksi. Pelanggan yang sering berbelanja dapat diberikan program keanggotaan eksklusif atau poin reward agar semakin loyal dan terus melakukan pembelian. Sementara itu, pelanggan yang jarang bertransaksi bisa didorong untuk berbelanja lebih sering melalui penawaran menarik seperti diskon khusus untuk pembelian berikutnya atau promo beli 2 gratis 1. Dengan pendekatan yang tepat, perusahaan dapat meningkatkan retensi pelanggan serta mendorong pertumbuhan transaksi secara berkelanjutan.")

    st.markdown("""<h3 style='color: cyan;'>Analisis Monetary</h3>""", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(rfm_df['Monetary'], bins=30, kde=True, color="blue", edgecolor="black", ax=ax)
    ax.set_xlabel("Total Pengeluaran (R$)")
    ax.set_ylabel("Jumlah Pelanggan")
    st.pyplot(fig)
    # Untuk membuat expander
    with st.expander("Lihat Penjelasan"):
        st.write("Pelanggan memiliki pola belanja yang beragam, dengan sebagian berbelanja dalam jumlah kecil dan sebagian lainnya melakukan pembelian dalam jumlah besar. Untuk pelanggan dengan transaksi besar, perusahaan dapat memberikan layanan spesial seperti diskon eksklusif, akses prioritas ke produk baru, atau program loyalitas premium guna mempertahankan mereka. Sementara itu, pelanggan dengan transaksi kecil dapat didorong untuk meningkatkan pembelian melalui penawaran bundling, diskon untuk pembelian dalam jumlah lebih banyak, atau promo spesial yang mendorong repeat order. Dengan strategi ini, perusahaan dapat mengoptimalkan pendapatan sekaligus meningkatkan loyalitas pelanggan.")