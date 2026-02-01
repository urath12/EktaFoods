import streamlit as st
import os
import base64
import pandas as pd
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from crewai_tools import SerperDevTool

# ==============================================================================
# 1. APP CONFIGURATION & CREDENTIALS
# ==============================================================================

st.set_page_config(page_title="Ekta Foods Command Deck", layout="wide")

st.sidebar.title("⚙️ Command Deck Settings")
st.sidebar.markdown("### Credentials")

def get_secret(key_name):
    """
    Robustly fetches secrets from Streamlit Cloud OR Environment.
    """
    # 1. Check Streamlit Cloud Secrets
    if key_name in st.secrets:
        return st.secrets[key_name]
    # 2. Check System Environment
    if key_name in os.environ:
        return os.environ[key_name]
    return None

# Fetch Keys
openai_api_key = get_secret("OPENAI_API_KEY")
serper_api_key = get_secret("SERPER_API_KEY")

# Fallback: Ask in Sidebar
if not openai_api_key:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not serper_api_key:
    serper_api_key = st.sidebar.text_input("Serper (Google) API Key", type="password")

# --- DIAGNOSTIC TOOL (THE SNIFFER) ---
if openai_api_key:
    masked_key = f"{openai_api_key[:8]}..."
    st.sidebar.caption(f"🔑 OpenAI Key Detected: `{masked_key}`")
else:
    st.sidebar.error("❌ OpenAI Key Missing")

if serper_api_key:
    st.sidebar.caption("🔑 Serper Key Detected")
else:
    st.sidebar.error("❌ Serper Key Missing")
# -------------------------------------

# Critical Stop
if not openai_api_key or not serper_api_key:
    st.warning("⚠️ Waiting for API keys...")
    st.stop()

# FORCE SET ENVIRONMENT VARIABLES
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["SERPER_API_KEY"] = serper_api_key
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"

# Initialize Tools
search_tool = SerperDevTool()

# DIRECT INJECTION (The Fix)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=openai_api_key 
)

# ==============================================================================
# 2. THE SOUL (KNOWLEDGE BASE)
# ==============================================================================

@st.cache_data
def load_manual():
    try:
        if os.path.exists("Ekta_Quality_Manual.txt"):
            with open("Ekta_Quality_Manual.txt", "r") as f:
                return f.read()
        else:
            return None
    except Exception:
        return None

EKTA_QUALITY_MANUAL = load_manual()

if EKTA_QUALITY_MANUAL is None:
    st.warning("⚠️ 'Ekta_Quality_Manual.txt' not found. Using Default Backup.")
    EKTA_QUALITY_MANUAL = """
    [MISSION] Pure Rooted stands for Zero Adulteration.
    [PRODUCTS] Mustard Oil (Kacchi Ghani), A2 Ghee (Bilona).
    [VALUES] Fair Trade, Swadeshi.
    """

# ==============================================================================
# 3. MEMORY SYSTEM
# ==============================================================================

LOG_FILE = "mission_logs.csv"

def save_to_history(agent_role, input_text, output_text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([{
        "Timestamp": timestamp, "Agent": agent_role, "Input": input_text, "Output": output_text
    }])
    if not os.path.exists(LOG_FILE):
        new_data.to_csv(LOG_FILE, index=False)
    else:
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

def load_history():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["Timestamp", "Agent", "Input", "Output"])

st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Mission Logs"):
    st.sidebar.dataframe(load_history())

# ==============================================================================
# 4. AGENT DEFINITIONS
# ==============================================================================

def get_editorial_agent():
    return Agent(
        role='Editorial Director (Auntiji Persona)',
        goal='Create warm, wise content from the perspective of "Auntiji".',
        backstory="""
        You are "Auntiji", the wise grandmother of the Pure Rooted family. 
        You speak with warmth and authority about health, Ayurveda, and the "old ways" of farming. 
        You treat followers like family members.
        You NEVER talk about martial arts. 
        You ONLY talk about Organic Farming, Ayurveda, and Food.
        """,
        verbose=True, allow_delegation=False, llm=llm
    )

def get_sentinel_agent():
    return Agent(
        role='Supply Chain Sentinel',
        goal='Scan news for adulteration scandals.',
        backstory='Vigilant risk analyst.',
        tools=[search_tool], verbose=True, allow_delegation=False, llm=llm
    )

def get_sales_agent():
    return Agent(
        role='B2B Relations (India)',
        goal='Start conversations via WhatsApp or Phone.',
        backstory="""
        You are a business relationship manager in Uttar Pradesh. 
        You know that in India, business happens on WhatsApp and Phone calls.
        Your English is simple, respectful, and direct (Indian Business English).
        You NEVER write long paragraphs. 
        Your ONLY goal is to get a 'Phone Call' or 'Shop Visit'.
        """,
        tools=[search_tool], verbose=True, allow_delegation=False, llm=llm
    )

def get_faq_agent():
    return Agent(
        role='Customer Success Trainer',
        goal='Provide accurate answers to team queries.',
        backstory='Head of Training.',
        verbose=True, allow_delegation=False, llm=llm
    )

# ==============================================================================
# 5. VISION LOGIC
# ==============================================================================

def analyze_image(uploaded_file, prompt_context):
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')
    message = HumanMessage(
        content=[
            {"type": "text", "text": f"Vision Analyst Context: {prompt_context}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    # Direct injection for Vision as well
    vision_llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
    response = vision_llm.invoke([message])
    return response.content

# ==============================================================================
# 6. MAIN INTERFACE
# ==============================================================================

st.title("🌱 Ekta Foods: Command Deck")
st.markdown(f"**Status:** `ONLINE` | **Protocol:** `PURE ROOTED` | **Target:** `UTTAR PRADESH`")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 THE BRAIN", "👂 THE EARS", "🤝 THE HANDSHAKE", "👁️ THE EYES", "🗣️ THE MOUTH"
])

# --- TAB 1: CONTENT ---
with tab1:
    st.header("Editorial Director (Auntiji)")
    st.info("Generates content in the voice of the wise grandmother.")
    topic = st.text_input("Enter Content Topic", value="Mustard Harvest")
    content_type = st.selectbox("Format", ["Instagram Caption", "Blog Post", "Weekly Calendar"])
    if st.button("Generate Content"):
        with st.spinner("Auntiji is thinking..."):
            task = Task(
                description=f"Draft {content_type} about {topic}. Manual: {EKTA_QUALITY_MANUAL}",
                expected_output=f"A {content_type}", agent=get_editorial_agent()
            )
            res = Crew(agents=[get_editorial_agent()], tasks=[task]).kickoff()
            st.markdown(res.raw)
            st.caption("Copy the text below:")
            st.code(res.raw, language='markdown')
            save_to_history("Editorial", f"{topic} ({content_type})", res.raw)

# --- TAB 2: SENTINEL ---
with tab2:
    st.header("Supply Chain Sentinel")
    query = st.text_input("Search Query", value="Ghee adulteration news India")
    if st.button("Scan Market"):
        with st.spinner("Scanning..."):
            task = Task(
                description=f"Search news for {query}. Summarize with counter-narratives. Manual: {EKTA_QUALITY_MANUAL}",
                expected_output="Summaries", agent=get_sentinel_agent()
            )
            res = Crew(agents=[get_sentinel_agent()], tasks=[task]).kickoff()
            st.markdown(res.raw)
            save_to_history("Sentinel", query, res.raw)

# --- TAB 3: SALES (WHATSAPP MODE) ---
with tab3:
    st.header("Sales Liaison (WhatsApp Mode)")
    st.info("Generates short, respectful messages optimized for WhatsApp/SMS to set up a call.")
    target_name = st.text_input("Target Vendor/Shop", value="Kirana Store Owner, Lucknow")
    
    if st.button("Draft Message"):
        with st.spinner("Drafting WhatsApp Message..."):
            task = Task(
                description=f"""
                1. Context: We want to supply Pure Rooted products to '{target_name}'.
                2. Goal: Write a SHORT WhatsApp message (max 3-4 sentences).
                3. Key Points: We do 'Farm-to-Table' and 'Fair Trade'. 
                4. Call to Action: Ask for a 5-minute phone call or a time to visit their shop.
                5. Tone: Respectful, Indian Business English (Simple).
                MANUAL: {EKTA_QUALITY_MANUAL}
                """,
                expected_output="A short WhatsApp message draft.",
                agent=get_sales_agent()
            )
            res = Crew(agents=[get_sales_agent()], tasks=[task]).kickoff()
            st.success("✅ Message Ready")
            st.markdown("### 📱 WhatsApp Draft")
            st.markdown(res.raw)
            st.caption("📋 One-Click Copy:")
            st.code(res.raw, language='text')
            save_to_history("Sales", target_name, res.raw)

# --- TAB 4: VISION ---
with tab4:
    st.header("Vision Lab")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    if uploaded_file and st.button("Analyze"):
        with st.spinner("Analyzing..."):
            res = analyze_image(uploaded_file, f"Quality Check. Manual: {EKTA_QUALITY_MANUAL}")
            st.markdown(res)
            save_to_history("Vision", "Image Analysis", res)

# --- TAB 5: FAQ ---
with tab5:
    st.header("FAQ Bot")
    q = st.text_input("Question", value="Why is it expensive?")
    if st.button("Answer"):
        with st.spinner("Consulting..."):
            task = Task(description=f"Answer '{q}' using {EKTA_QUALITY_MANUAL}", expected_output="Script", agent=get_faq_agent())
            res = Crew(agents=[get_faq_agent()], tasks=[task]).kickoff()
            st.markdown(res.raw)
            st.code(res.raw, language='text')
            save_to_history("FAQ", q, res.raw)