import streamlit as st
import requests
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="ALGOPLASTS", page_icon="🧬", layout="centered")

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64("background.jpg")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
    .stApp {{
        background-image: linear-gradient(rgba(5, 15, 10, 0.82), rgba(5, 15, 10, 0.88)),
                           url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .big-title {{
        font-size: 48px; font-weight: 800; color: #7CFC7C;
        text-align: center; margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(124, 252, 124, 0.4);
    }}
    .subtitle {{ font-size: 18px; color: #d0d0d0; text-align: center; margin-bottom: 30px; }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(10px);
        border-radius: 18px; padding: 20px;
        border: 1px solid rgba(124, 252, 124, 0.15); margin-bottom: 15px;
    }}
    .result-box {{
        padding: 24px; border-radius: 15px; text-align: center;
        font-size: 20px; font-weight: 700; margin-top: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .suggestion-box {{
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #7CFC7C;
        border-radius: 8px;
        padding: 15px 20px;
        margin-top: 15px;
        color: #e0e0e0;
        font-size: 15px;
        line-height: 1.6;
    }}
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.05); border-radius: 12px;
        padding: 10px; border: 1px solid rgba(124, 252, 124, 0.15);
    }}
    .stButton button {{
        background: linear-gradient(90deg, #2e7d32, #66bb6a);
        color: white; font-weight: 700; border-radius: 12px;
        border: none; padding: 10px 25px; transition: 0.3s;
    }}
    .stButton button:hover {{
        transform: scale(1.03); box-shadow: 0px 0px 15px rgba(124, 252, 124, 0.5);
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🧬 ALGOPLASTS</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Degradation Condition Checker</p>', unsafe_allow_html=True)

API_KEY = "cfe7d16a33b6fcbe79d1495dd9e4562a"

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
city = st.text_input("🌍 Enter any city in the world:", value="Gwalior", key="city_input")
humidity_weight = st.slider("💧 How much should humidity affect the result?", 0, 100, 50, key="humidity_slider")
check = st.button("🔍 Check Conditions")
st.markdown('</div>', unsafe_allow_html=True)

if check:
    with st.spinner("Fetching live climate data..."):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        resolved_name = data.get("name", city)

        temp_score = min(max((temp - 15) / 20, 0), 1) * 100
        humidity_score = min(max((humidity - 40) / 50, 0), 1) * 100
        final_score = (temp_score * (100 - humidity_weight) + humidity_score * humidity_weight) / 100

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("🌡️ Temperature", f"{temp}°C")
        m2.metric("💧 Humidity", f"{humidity}%")
        m3.metric("⚗️ Score", f"{final_score:.0f}/100")
        st.markdown('</div>', unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            title={'text': f"Degradation Favorability — {resolved_name}", 'font': {'color': 'white', 'size': 16}},
            number={'font': {'color': '#7CFC7C'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': "#7CFC7C"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 40], 'color': "#4a1e1e"},
                    {'range': [40, 70], 'color': "#4a3c14"},
                    {'range': [70, 100], 'color': "#1e4620"}
                ],
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # Result box
        if final_score >= 70:
            st.markdown('<div class="result-box" style="background-color:rgba(30,70,32,0.7); color:#7CFC7C;">✅ Favorable — supports faster hydrolysis and degradation.</div>', unsafe_allow_html=True)
        elif final_score >= 40:
            st.markdown('<div class="result-box" style="background-color:rgba(74,60,20,0.7); color:#FFD966;">⚠️ Partially Favorable — degradation occurs, but more slowly.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="result-box" style="background-color:rgba(74,30,30,0.7); color:#FF7C7C;">❌ Less Favorable — current conditions slow the process.</div>', unsafe_allow_html=True)

       API_KEY = st.secrets["API_KEY"]
        suggestions = []
        if temp_score < 60:
            suggestions.append("🌡️ **Raise the temperature** — hydrolysis accelerates significantly above 25°C. Composting facilities or controlled warm storage could close this gap artificially.")
        if humidity_score < 60:
            suggestions.append("💧 **Increase moisture exposure** — ester bond hydrolysis needs water contact. Higher humidity or direct soil/water burial would speed degradation.")
        if temp_score >= 60 and humidity_score >= 60:
            suggestions.append("✅ **Conditions are already near-optimal** — this location could realistically support natural degradation with minimal intervention.")
        if not suggestions:
            suggestions.append("Consider industrial composting facilities, which artificially maintain optimal temperature and humidity year-round regardless of local climate.")

        st.markdown('<div class="suggestion-box"><b>🧠 AI Suggestions to Improve Favorability:</b><br><br>' + "<br><br>".join(suggestions) + '</div>', unsafe_allow_html=True)

        st.caption("Illustrative model combining live weather data with published PLA/PHA degradation research — not a substitute for lab testing.")
    else:
        st.error(f"Couldn't find '{city}'. Check the spelling and try again.")
