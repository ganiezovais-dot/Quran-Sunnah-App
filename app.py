import streamlit as st
import asyncio
import os
import re
import requests
from groq import Groq

# 1. Stability Fix for Python 3.13
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# 2. Page Configuration & Design
st.set_page_config(page_title="Bayyinah", page_icon="📖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #1e5631 !important; 
        color: white !important; 
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #a47c48 !important; }
    h1 { color: #1e5631; text-align: center; border-bottom: 2px solid #1e5631; padding-bottom: 10px; }
    .stChatMessage { border: 1px solid #1e5631; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Permanent History Storage
HISTORY_FILE = "chat_history.txt"

def save_to_file(user_q, ai_a):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"USER: {user_q}\nAI: {ai_a}\n---\n")

def load_from_file():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "No history found yet."

# --- DATA: 114 SURAHS ---
SURAHS = [
    "1. الفاتحة (Al-Fatihah)", "2. البقرة (Al-Baqarah)", "3. آل عمران (Ali 'Imran)", "4. النساء (An-Nisa)", "5. المائدة (Al-Ma'idah)",
    "6. الأنعام (Al-An'am)", "7. الأعراف (Al-A'raf)", "8. الأنفال (Al-Anfal)", "9. التوبة (At-Tawbah)", "10. يونس (Yunus)",
    "11. هود (Hud)", "12. يوسف (Yusuf)", "13. الرعد (Ar-Ra'd)", "14. إبراهيم (Ibrahim)", "15. الحجر (Al-Hijr)",
    "16. النحل (An-Nahl)", "17. الإسراء (Al-Isra)", "18. الكهف (Al-Kahf)", "19. مريم (Maryam)", "20. طه (Taha)",
    "21. الأنبياء (Al-Anbya)", "22. الحج (Al-Hajj)", "23. المؤمنون (Al-Mu'minun)", "24. النور (An-Nur)", "25. الفرقان (Al-Furqan)",
    "26. الشعراء (Ash-Shu'ara)", "27. النمل (An-Naml)", "28. القصص (Al-Qasas)", "29. العنكبوت (Al-'Ankabut)", "30. الروم (Ar-Rum)",
    "31. لقمان (Luqman)", "32. السجدة (As-Sajdah)", "33. الأحزاب (Al-Ahzab)", "34. سبأ (Saba)", "35. فاطر (Fatir)",
    "36. يس (Ya-Sin)", "37. الصافات (As-Saffat)", "38. ص (Sad)", "39. الزمر (Az-Zumar)", "40. غافر (Ghafir)",
    "41. فصلت (Fussilat)", "42. الشورى (Ash-Shura)", "43. الزخرف (Az-Zukhruf)", "44. الدخان (Ad-Dukhan)", "45. الجاثية (Al-Jathiyah)",
    "46. الأحقاف (Al-Ahqaf)", "47. محمد (Muhammad)", "48. الفتح (Al-Fath)", "49. الحجرات (Al-Hujurat)", "50. ق (Qaf)",
    "51. الذاريات (Adh-Dhariyat)", "52. الطور (At-Tur)", "53. النجم (An-Najm)", "54. القمر (Al-Qamar)", "55. الرحمن (Ar-Rahman)",
    "56. الواقعة (Al-Waqi'ah)", "57. الحديد (Al-Hadid)", "58. المجادلة (Al-Mujadila)", "59. الحشر (Al-Hashr)", "60. الممتحنة (Al-Mumtahanah)",
    "61. الصف (As-Saff)", "62. الجمعة (Al-Jumu'ah)", "63. المنافقون (Al-Munafiqun)", "64. التغابن (At-Taghabun)", "65. الطلاق (At-Talaq)",
    "66. التحريم (At-Tahrim)", "67. الملك (Al-Mulk)", "68. القلم (Al-Qalam)", "69. الحاقة (Al-Haqqah)", "70. المعارج (Al-Ma'arij)",
    "71. نوح (Nuh)", "72. الجن (Al-Jinn)", "73. المزمل (Al-Muzzammil)", "74. المدثر (Al-Muddaththir)", "75. القيامة (Al-Qiyamah)",
    "76. الإنسان (Al-Insan)", "77. المرسلات (Al-Mursalat)", "78. النبأ (An-Naba)", "79. النازعات (An-Nazi'at)", "80. عبس ('Abasa)",
    "81. التكوير (At-Takwir)", "82. الانفطار (Al-Infitar)", "83. المطففين (Al-Mutaffifin)", "84. الانشقاق (Al-Inshiqaq)", "85. البروج (Al-Buruj)",
    "86. الطارق (At-Tariq)", "87. الأعلى (Al-A'la)", "88. الغاشية (Al-Ghashiyah)", "89. الفجر (Al-Fajr)", "90. البلد (Al-Balad)",
    "91. الشمس (Ash-Shams)", "92. الليل (Al-Layl)", "93. الضحى (Ad-Duha)", "94. الشرح (Ash-Sharh)", "95. التين (At-Tin)",
    "96. العلق (Al-'Alaq)", "97. القدر (Al-Qadr)", "98. البينة (Al-Bayyinah)", "99. الزلزلة (Az-Zalzalah)", "100. العاديات (Al-'Adiyat)",
    "101. القارعة (Al-Qari'ah)", "102. التكاثر (At-Takathur)", "103. العصر (Al-'Asr)", "104. الهمزة (Al-Humazah)", "105. الفيل (Al-Fil)",
    "106. قريش (Quraysh)", "107. الماعون (Al-Ma'un)", "108. الكوثر (Al-Kawthar)", "109. الكافرون (Al-Kafirun)", "110. النصر (An-Nasr)",
    "111. المسد (Al-Masad)", "112. الإخلاص (Al-Ikhlas)", "113. الفلق (Al-Falaq)", "114. الناس (An-Nas)"
]

# --- AI AGENT LOGIC ---
def ask_ai(query, key, is_scholar=True):
    try:
        client = Groq(api_key=key)
        sys_msg = "You are a scholar. Answer ONLY using Quran and Sahih Bukhari/Muslim. Cite references." if is_scholar else ""
        chat = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": query}],
            model="llama-3.1-8b-instant"
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

# --- APP LAYOUT ---
st.markdown("<h1>🌙 NOBLE QURAN & SUNNAH HUB</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Settings")
    # THE SECRET FIX: Pulls key from the dashboard automatically
    try:
        user_api_key = st.secrets["GROQ_KEY"]
        st.success("✅ Scholar Brain Connected")
    except:
        st.error("❌ Key not found in Secrets Dashboard")
        user_api_key = None

    if "history" not in st.session_state: st.session_state.history = []
    
    st.divider()
    if st.button("🗑️ Clear History"):
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        st.rerun()

option = st.sidebar.radio("Navigation:", ["1. Quran Reader", "2. Hadith Sources", "3. AI Scholar Agent", "4. My Research Log"])

if option == "1. Quran Reader":
    st.subheader("Explore the 114 Surahs")
    selected = st.selectbox("Choose a Surah:", options=SURAHS)
    if st.button("✨ Load Holy Verses"):
        if not user_api_key: st.error("Key error in Settings")
        else:
            with st.spinner("Fetching..."):
                ans = ask_ai(f"Provide English translation for Surah {selected} via Quran.com.", user_api_key, False)
                st.info(ans)

elif option == "2. Hadith Sources":
    st.subheader("The Authenticated Sunnah")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Sahih al-Bukhari")
        st.link_button("📚 Read Bukhari", "https://sunnah.com")
    with c2:
        st.markdown("### Sahih Muslim")
        st.link_button("📚 Read Muslim", "https://sunnah.com")

elif option == "3. AI Scholar Agent":
    st.subheader("Interactive AI Scholar")
    q = st.chat_input("Ask about a verse or hadith...")
    if q and user_api_key:
        with st.spinner("Searching Sahih sources..."):
            ans = ask_ai(q, user_api_key)
            save_to_file(q, ans)
            st.chat_message("user").write(q)
            with st.chat_message("assistant"):
                st.write(ans)
                st.code(ans, language="markdown")

elif option == "4. My Research Log":
    st.subheader("Your Saved Research")
    content = load_from_file()
    st.text_area("Permanent History (Saved on PC):", content, height=400)
