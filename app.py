import streamlit as st
import pandas as pd
import datetime

# ================= CONFIG =================
st.set_page_config(page_title="AyamKu 2026", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#fff6dc,#ffe8c2);
}
.title {
    font-size:30px;
    font-weight:700;
}
.box {
    background:white;
    padding:18px;
    border-radius:14px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ================= USERS =================
USERS = {
    "admin": {"password": "4dm1n", "role": "admin"},
    "krwn": {"password": "k4ry4w4n", "role": "karyawan"}
}

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.data = []

# ================= LOGIN =================
def login():
    st.markdown("<div class='title'>🐔 AyamKu 2026</div>", unsafe_allow_html=True)
    st.caption("Sistem Peternakan Modern")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.login = True
            st.session_state.user = u
            st.session_state.role = USERS[u]["role"]
            st.rerun()
        else:
            st.error("Login gagal")

# ================= PASSWORD CHANGE (BARU) =================
def change_password():
    st.markdown("### 🔐 Ganti Password")

    old = st.text_input("Password lama", type="password")
    new = st.text_input("Password baru", type="password")
    confirm = st.text_input("Konfirmasi password baru", type="password")

    if st.button("Update Password"):
        user = st.session_state.user

        if USERS[user]["password"] != old:
            st.error("Password lama salah")
        elif new != confirm:
            st.error("Konfirmasi tidak cocok")
        else:
            USERS[user]["password"] = new
            st.success("Password berhasil diubah")

# ================= SIDEBAR =================
def sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.caption(st.session_state.role.upper())

        st.markdown("---")

        # ===== TAMBAHAN FITUR =====
        change_password()

        st.markdown("---")

        if st.button("Logout"):
            st.session_state.login = False
            st.rerun()

# ================= AI =================
def ai_analysis(df):
    if df.empty or len(df) < 2:
        st.info("📊 Data belum cukup untuk analisis AI")
        return

    df = df.sort_values("tgl")

    last = df.iloc[-1]
    prev = df.iloc[-2]

    trend = last["mati"] - prev["mati"]

    if trend > 5:
        st.error("🚨 Lonjakan kematian! Periksa kandang")
    elif trend > 0:
        st.warning("⚠️ Kematian meningkat")
    elif trend < 0:
        st.success("✅ Kondisi membaik")
    else:
        st.info("📊 Stabil")

# ================= ADMIN =================
def admin_dashboard():
    st.markdown("<div class='title'>📊 Dashboard Admin</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.data)

    kandang = df[df["type"] == "kandang"] if not df.empty else pd.DataFrame()
    pengiriman = df[df["type"] == "pengiriman"] if not df.empty else pd.DataFrame()

    hidup = kandang["hidup"].iloc[-1] if not kandang.empty else 0
    mati = kandang["mati"].sum() if not kandang.empty else 0
    kirim = pengiriman["jumlah"].sum() if not pengiriman.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("🐔 Hidup", hidup)
    c2.metric("💀 Mati", mati)
    c3.metric("🚚 Dikirim", kirim)

    st.divider()

    # ===== AI =====
    st.subheader("🧠 Analisis AI")
    ai_analysis(kandang)

    st.divider()

    # ===== GRAFIK (TETAP ADA MESKI KOSONG) =====
    st.subheader("📊 Distribusi Ayam")

    chart_data = pd.DataFrame({
        "Status": ["Hidup", "Mati"],
        "Jumlah": [hidup, mati]
    })

    st.bar_chart(chart_data.set_index("Status"))

    if hidup + mati == 0:
        st.caption("Data masih kosong — grafik default ditampilkan")

    st.divider()

    # ===== TREND =====
    st.subheader("📈 Tren Ayam")

    if not kandang.empty:
        kandang["tgl"] = pd.to_datetime(kandang["tgl"])
        kandang = kandang.sort_values("tgl")
        st.line_chart(kandang.set_index("tgl")[["hidup"]])
    else:
        dummy = pd.DataFrame({
            "tgl": pd.date_range(start="2026-01-01", periods=3),
            "hidup": [0,0,0]
        })
        st.line_chart(dummy.set_index("tgl"))

        st.caption("Grafik default (belum ada data)")

    st.divider()

    # ===== DATA CONTROL =====
    st.subheader("🛠️ Kelola Data")

    if not df.empty:
        for i in range(len(st.session_state.data)-1, -1, -1):
            d = st.session_state.data[i]

            with st.expander(f"{d['type']} | {d['tgl']}"):

                if d["type"] == "kandang":
                    h = st.number_input("Hidup", value=d["hidup"], key=f"h{i}")
                    m = st.number_input("Mati", value=d["mati"], key=f"m{i}")

                    if st.button("Update", key=f"u{i}"):
                        st.session_state.data[i]["hidup"] = h
                        st.session_state.data[i]["mati"] = m
                        st.rerun()

                if st.button("Hapus", key=f"d{i}"):
                    st.session_state.data.pop(i)
                    st.rerun()
    else:
        st.info("Belum ada data")

# ================= KARYAWAN =================
def input_data():
    st.markdown("<div class='title'>🧑‍🌾 Input Laporan</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 Kandang", "🚚 Pengiriman"])

    # ===== KANDANG =====
    with tab1:
        tgl = st.date_input("Tanggal")
        hidup = st.number_input("Ternak Hidup", 0)
        mati = st.number_input("Ternak Mati", 0)
        sakit = st.number_input("Ternak Sakit", 0)
        pakan = st.number_input("Pakan (kg)", 0.0)
        stok = st.number_input("Stok (kg)", 0.0)
        kondisi = st.selectbox("Kondisi", ["Baik","Cukup","Buruk"])
        catatan = st.text_area("Catatan")

        if st.button("Simpan Kandang"):
            st.session_state.data.append({
                "type":"kandang",
                "tgl":str(tgl),
                "hidup":hidup,
                "mati":mati,
                "sakit":sakit,
                "pakan":pakan,
                "stok":stok,
                "kondisi":kondisi,
                "catatan":catatan
            })
            st.success("Data kandang tersimpan")

    # ===== PENGIRIMAN =====
    with tab2:
        tgl = st.date_input("Tanggal Kirim")
        tujuan = st.text_input("Tujuan")
        jumlah = st.number_input("Jumlah Ayam", 0)
        berat = st.number_input("Berat (kg)", 0.0)
        status = st.selectbox("Status", ["Selesai","Dalam Perjalanan","Pending"])
        catatan = st.text_area("Catatan Kirim")

        if st.button("Simpan Pengiriman"):
            st.session_state.data.append({
                "type":"pengiriman",
                "tgl":str(tgl),
                "tujuan":tujuan,
                "jumlah":jumlah,
                "berat":berat,
                "status":status,
                "catatan":catatan
            })
            st.success("Data pengiriman tersimpan")

# ================= MAIN =================
if not st.session_state.login:
    login()
else:
    sidebar()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        input_data()
