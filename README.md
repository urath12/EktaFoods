# EktaFoods# 🌱 Ekta Foods: Command Deck (Protocol: Pure Rooted)

**Status:** `ONLINE` (v3.2) | **Target Market:** `Uttar Pradesh / Pan-India`

## 📖 Overview
The **Ekta Foods Command Deck** is an AI-powered operating system for **Pure Rooted**, an organic farm-to-table venture. It serves as a "Senior Advisor" for the business, automating content strategy, market intelligence, and B2B communication while strictly adhering to a "Swadeshi" and "Ayurvedic" quality standard.

The system is designed for **mobile-first use in the field**, optimizing output for WhatsApp communication and high-context Indian business norms (e.g., "Hinglish," relationship-first sales).

## 🏗 System Architecture (The "Agni Protocol")

The system is governed by a central **Quality Manual** (`Ekta_Quality_Manual.txt`) which acts as the "Soul," ensuring all AI agents speak with one consistent voice regarding pricing, purity tests, and fair trade promises.

### 🤖 The Agent Crew
| Module | Agent Name | Function |
| :--- | :--- | :--- |
| **🧠 The Brain** | Editorial Director | Generates Instagram captions/blogs about organic farming without "hallucinating" unrelated topics. |
| **👂 The Ears** | Supply Chain Sentinel | Scans Google for recent food adulteration news to generate "Counter-Narratives" for the brand. |
| **🤝 The Handshake** | B2B Relations (India) | Drafts short, respectful **WhatsApp messages** optimized for Indian vendors to secure phone calls/visits. |
| **👁️ The Eyes** | Vision Analyst | Uses GPT-4o Vision to analyze photos of harvest/packaging for quality control and social proof. |
| **🗣️ The Mouth** | FAQ Bot | A training tool for employees to answer difficult customer questions (e.g., "Why is it expensive?"). |

### 💾 Memory System (The Black Box)
* All agent outputs are automatically logged to `mission_logs.csv`.
* Users can view history and download logs directly from the sidebar.

## 🛠 Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Orchestration:** [CrewAI](https://crewai.com/)
* **LLM:** GPT-4o (via `langchain_openai`)
* **Search:** Google Serper API
* **Deployment:** Streamlit Community Cloud

## 🚀 Quick Start (Local / Codespaces)

### 1. Prerequisites
* Python 3.10+
* OpenAI API Key
* Serper (Google Search) API Key

### 2. Installation
```bash
pip install -r requirements.txt