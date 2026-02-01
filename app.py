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

# 1. Try to fetch from Environment (Codespaces Secrets)
openai_api_key = os.environ.get("OPENAI_API_KEY")
serper_api_key = os.environ.get("SERPER_API_KEY")

# 2. If not found in Environment, ask in Sidebar
if not openai_api_key:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
else:
    st.sidebar.success("✅ OpenAI Key Loaded from Environment")

if not serper_api_key:
    serper_api_key = st.sidebar.text_input("Serper (Google) API Key", type="password")
else:
    st.sidebar.success("✅ Serper Key Loaded from Environment")

# 3. Stop if we still don't have keys
if not openai_api_key or not serper_api_key:
    st.warning("⚠️ Please enter your API keys to activate the Agents.")
    st.stop()

# Set environment variables for CrewAI
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["SERPER_API_KEY"] = serper_api_key

# Initialize Tools & LLM
search_tool = SerperDevTool()
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# ==============================================================================
# 2. THE SOUL (KNOWLEDGE BASE)
# ==============================================================================

@st.cache_data
def load_manual():
    """
    Loads the Quality Manual from a text file. 
    Cached to prevent re-reading on every interaction.
    """
    try:
        with open("Ekta_Quality_Manual.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

EKTA_QUALITY_MANUAL = load_manual()

if EKTA_QUALITY_MANUAL is None:
    st.error("🚨 CRITICAL ERROR: 'Ekta_Quality_Manual.txt' not found.")
    st.info("Please create this text file in your project folder.")
    st.stop()

# ==============================================================================
# 3. MEMORY SYSTEM (THE BLACK BOX)
# ==============================================================================

LOG_FILE = "mission_logs.csv"

def save_to_history(agent_role, input_text, output_text):
    """
    Appends the agent's action to a local CSV file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_data = pd.DataFrame([{
        "Timestamp": timestamp,
        "Agent": agent_role,
        "Input": input_text,
        "Output": output_text
    }])
    
    if not os.path.exists(LOG_FILE):
        new_data.to_csv(LOG_FILE, index=False)
    else:
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

def load_history():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["Timestamp", "Agent", "Input", "Output"])

# Sidebar: History Viewer
st.sidebar.markdown("---")
st.sidebar.subheader("📜 Mission Logs")
if st.sidebar.checkbox("Show History"):
    history_df = load_history()
    st.sidebar.dataframe(history_df)
    
    # Download Button
    csv = history_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Logs (CSV)",
        data=csv,
        file_name="ekta_mission_logs.csv",
        mime="text/csv",
    )

# ==============================================================================
# 4. AGENT DEFINITIONS
# ==============================================================================

def get_editorial_agent():
    return Agent(
        role='Editorial Director',
        goal='Create educational content for Pure Rooted foods.',
        backstory='You are a veteran content strategist knowledgeable about Ayurveda.',
        verbose=True, allow_delegation=False, llm=llm
    )

def get_sentinel_agent():
    return Agent(
        role='Supply Chain Sentinel',
        goal='Scan news for adulteration scandals.',
        backstory='You are a vigilant risk analyst.',
        tools=[search_tool], verbose=True, allow_delegation=False, llm=llm
    )

def get_sales_agent():
    return Agent(
        role='B2B Sales Liaison',
        goal='Draft empathetic introduction emails.',
        backstory='You are a sales expert who values "Vishwas" (Trust).',
        tools=[search_tool], verbose=True, allow_delegation=False, llm=llm
    )

def get_faq_agent():
    return Agent(
        role='Customer Success Trainer',
        goal='Provide accurate answers to team queries.',
        backstory='You are the Head of Training.',
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
            {"type": "text", "text": f"You are the 'Vision Analyst' for Ekta Foods. {prompt_context}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    response = llm.invoke([message])
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
    st.header("Editorial Director")
    st.info("Generates content calendars and captions based on the Quality Manual.")
    topic = st.text_input("Enter Content Topic/Event", value="Upcoming Mustard Harvest")
    content_type = st.selectbox("Format", ["Instagram Caption", "Blog Post", "Weekly Calendar"])
    
    if st.button("Generate Content"):
        with st.spinner("Drafting..."):
            task = Task(
                description=f"Read the MANUAL below. Draft a {content_type} about: {topic}. Tone: Warm/Elder. MANUAL: {EKTA_QUALITY_MANUAL}",
                expected_output=f"A {content_type}.",
                agent=get_editorial_agent()
            )
            crew = Crew(agents=[get_editorial_agent()], tasks=[task])
            result = crew.kickoff()
            
            st.markdown("### 📝 Generated Content")
            st.markdown(result.raw)
            save_to_history("Editorial Director", f"{topic} ({content_type})", result.raw)
            st.success("✅ Saved to Mission Logs")

# --- TAB 2: MARKET INTEL ---
with tab2:
    st.header("Supply Chain Sentinel")
    st.info("Scans the web for food safety news.")
    query = st.text_input("Search Query", value="Mustard oil adulteration news India 2024")
    
    if st.button("Scan Market"):
        with st.spinner("Scanning..."):
            task = Task(
                description=f"Search news for: {query}. Summarize 3 stories with 'Counter-Narratives' based on MANUAL: {EKTA_QUALITY_MANUAL}",
                expected_output="Summaries and counter-narratives.",
                agent=get_sentinel_agent()
            )
            crew = Crew(agents=[get_sentinel_agent()], tasks=[task])
            result = crew.kickoff()
            
            st.markdown("### 📡 Intelligence Report")
            st.markdown(result.raw)
            save_to_history("Sentinel", query, result.raw)
            st.success("✅ Saved to Mission Logs")

# --- TAB 3: SALES ---
with tab3:
    st.header("Sales Liaison")
    st.info("Researches leads and drafts B2B pitches.")
    target_name = st.text_input("Target Name", value="Organic Soul Boutique, Mumbai")
    
    if st.button("Draft Pitch"):
        with st.spinner("Drafting..."):
            task = Task(
                description=f"Research '{target_name}'. Draft cold email based on Fair Trade in MANUAL: {EKTA_QUALITY_MANUAL}",
                expected_output="Email draft.",
                agent=get_sales_agent()
            )
            crew = Crew(agents=[get_sales_agent()], tasks=[task])
            result = crew.kickoff()
            
            st.markdown("### ✉️ Email Draft")
            st.markdown(result.raw)
            save_to_history("Sales Liaison", target_name, result.raw)
            st.success("✅ Saved to Mission Logs")

# --- TAB 4: VISION ---
with tab4:
    st.header("Vision Lab")
    st.info("Analyze photos of harvest or packaging.")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    analysis_type = st.selectbox("Analysis Goal", ["Quality Check", "Social Caption", "Compliance"])

    if uploaded_file is not None and st.button("Analyze Image"):
        with st.spinner("Analyzing..."):
            vision_prompt = f"Analyze image. Context: Ekta Foods. Goal: {analysis_type}. Manual: {EKTA_QUALITY_MANUAL}"
            result = analyze_image(uploaded_file, vision_prompt)
            
            st.markdown("### 👁️ Vision Report")
            st.markdown(result)
            save_to_history("Vision Lab", f"Image Analysis: {analysis_type}", result)
            st.success("✅ Saved to Mission Logs")

# --- TAB 5: FAQ BOT ---
with tab5:
    st.header("Internal FAQ Bot")
    st.info("Ask difficult customer questions here.")
    user_question = st.text_input("Question", value="Why is ghee expensive?")
    
    if st.button("Get Answer"):
        with st.spinner("Consulting..."):
            task = Task(
                description=f"Answer '{user_question}' for a junior employee using MANUAL: {EKTA_QUALITY_MANUAL}",
                expected_output="Scripted answer.",
                agent=get_faq_agent()
            )
            crew = Crew(agents=[get_faq_agent()], tasks=[task])
            result = crew.kickoff()
            
            st.markdown("### 🗣️ Response")
            st.markdown(result.raw)
            save_to_history("FAQ Bot", user_question, result.raw)
            st.success("✅ Saved to Mission Logs")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.caption("Powered by CrewAI & GPT-4o | Project Ekta Foods")