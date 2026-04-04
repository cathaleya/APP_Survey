import streamlit as st
import json
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Set Page Config
st.set_page_config(page_title="SJT Adaptive Thinking English - PGSD", layout="centered")

import os

# Get absolute path of the current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(CURRENT_DIR, "questions.json")

# Load Questions
if not os.path.exists(QUESTIONS_PATH):
    st.error(f"File '{QUESTIONS_PATH}' tidak ditemukan. Pastikan file pertanyaan sudah diunggah.")
    st.stop()

with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    questions = json.load(f)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "biodata"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Custom Styles
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Function to Save to GSheets
def save_to_gsheets(data):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Read existing data
        existing_data = conn.read(ttl=0)
        
        # Create a new dataframe for the new entry
        new_row = pd.DataFrame([data])
        
        # Append to existing
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # Write back (Note: requires 'Edit' permission and proper setup in Streamlit Secrets)
        conn.update(data=updated_df)
        return True
    except Exception as e:
        st.error(f"Gagal mengirim data ke Google Sheets: {e}")
        return False

# --- PAGE: BIODATA ---
if st.session_state.page == "biodata":
    st.title("📋 Biodata Peserta")
    st.info("Silakan lengkapi data diri Anda sebelum memulai kuisioner Situational Judgement Test (SJT).")
    
    with st.form("form_biodata"):
        nama = st.text_input("Nama Lengkap")
        nim = st.text_input("NIM / ID Mahasiswa")
        univ = st.text_input("Universitas")
        semester = st.selectbox("Semester", ["1", "2", "3", "4", "5", "6", "7", "8", ">8"])
        
        submit_bio = st.form_submit_button("Mulai Kuisioner")
        
        if submit_bio:
            if nama and nim and univ:
                st.session_state.user_data = {
                    "Nama": nama,
                    "NIM": nim,
                    "Universitas": univ,
                    "Semester": semester,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.page = 1
                st.rerun()
            else:
                st.warning("Mohon lengkapi semua field biodata.")

# --- PAGE: QUESTIONNAIRE ---
elif isinstance(st.session_state.page, int):
    q_idx = st.session_state.page - 1
    q = questions[q_idx]
    
    st.title(f"Situasi {st.session_state.page} dari {len(questions)}")
    st.progress(st.session_state.page / len(questions))
    
    st.subheader("Skenario:")
    st.write(q["scenario"])
    
    st.markdown("---")
    st.subheader("Pilihan Tindakan:")
    
    # Selection
    current_ans = st.session_state.answers.get(str(q["id"]), None)
    choice = st.radio(
        "Pilih tindakan yang menurut Anda paling tepat:",
        options=[opt["text"] for opt in q["options"]],
        index=None if current_ans is None else [opt["text"] for opt in q["options"]].index(current_ans["text"])
    )
    
    col1, col2 = st.columns([1,1])
    
    with col1:
        if st.session_state.page > 1:
            if st.button("⬅️ Kembali"):
                st.session_state.page -= 1
                st.rerun()
                
    with col2:
        if st.button("Selesai & Lanjut ➡️" if st.session_state.page < len(questions) else "Lihat Ringkasan 🏁"):
            if choice:
                # Find score for selected choice
                selected_opt = next(opt for opt in q["options"] if opt["text"] == choice)
                st.session_state.answers[str(q["id"])] = {
                    "text": choice,
                    "score": selected_opt["score"]
                }
                
                if st.session_state.page < len(questions):
                    st.session_state.page += 1
                else:
                    st.session_state.page = "summary"
                st.rerun()
            else:
                st.warning("Mohon pilih salah satu jawaban.")

# --- PAGE: SUMMARY & SUBMIT ---
elif st.session_state.page == "summary":
    st.title("✅ Ringkasan Jawaban")
    st.write(f"Terima kasih, **{st.session_state.user_data['Nama']}**!")
    st.write("Silakan periksa kembali ringkasan jawaban Anda sebelum dikirim.")
    
    # Prepare data for summary table
    summary_data = []
    total_score = 0
    final_responses = {}
    
    # Merge basic data
    for k, v in st.session_state.user_data.items():
        final_responses[k] = v
        
    for q in questions:
        ans = st.session_state.answers.get(str(q["id"]))
        summary_data.append({
            "No": q["id"],
            "Jawaban": ans["text"][:50] + "..." if ans else "Belum diisi",
            "Skor": ans["score"] if ans else 0
        })
        if ans:
            total_score += ans["score"]
            final_responses[f"Q{q['id']}_Score"] = ans["score"]
            final_responses[f"Q{q['id']}_Text"] = ans["text"]

    final_responses["Total_Score"] = total_score
    
    st.table(pd.DataFrame(summary_data))
    st.metric("Total Skor Adaptive Thinking", f"{total_score} / 80")
    
    if st.button("🚀 Kirim Data Ke Peneliti"):
        with st.spinner("Mengirim data..."):
            success = save_to_gsheets(final_responses)
            if success:
                st.success("Data berhasil terkirim ke Google Sheets Peneliti!")
                st.balloons()
                st.session_state.page = "finish"
                # st.rerun()
            else:
                st.error("Gagal mengirim ke Google Sheets secara otomatis.")
                st.info("Silakan unduh CSV hasil di bawah dan kirimkan manual ke Dosen/Peneliti.")
                csv = pd.DataFrame([final_responses]).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Hasil (CSV)",
                    data=csv,
                    file_name=f"Hasil_SJT_{st.session_state.user_data['NIM']}.csv",
                    mime='text/csv',
                )

# --- PAGE: FINISH ---
elif st.session_state.page == "finish":
    st.title("🏁 Selesai")
    st.success("Terima kasih telah berpartisipasi dalam penelitian ini.")
    st.write("Jawaban Anda telah tersimpan. Anda dapat menutup tab ini sekarang.")
    if st.button("Mulai Baru (Reset)"):
        st.session_state.clear()
        st.rerun()
