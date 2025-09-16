# AI Agent Expense Tracker

> A beautiful, AI-powered expense tracking application built with Streamlit and a modular multi-agent architecture.

---

## 🚀 Overview

The **AI Agent Expense Tracker** combines OCR, intelligent categorization, personalized budgeting, and predictive insights into a single, user-friendly Streamlit app. Specialized AI agents collaborate to automate receipt processing, classify expenses, suggest budgets, and provide actionable financial insights.

Key agents:

- **Receipt Scanner Agent** — OCR and AI-enhanced data extraction
- **Categorization Agent** — Learns to classify expenses and returns confidence scores
- **Budget Advisor Agent** — Generates personalized budgets (50/30/20) and recommendations
- **Insights Agent** — Produces trend analysis, forecasts, and a spending health score

---

## 🏗 System Architecture

### Frontend

- **Streamlit** single-page responsive app
- Componentized UI with `styles.py` for custom CSS and Google Fonts
- **Plotly** visualizations for interactive analytics
- File upload interface for receipt scanning (image uploads)

### Backend

- Modular Python design with clear separation of concerns:
  - `OCRProcessor` — image preprocessing and text extraction using Tesseract (pytesseract)
  - `AICategorizer` — expense categorization using Groq/LLM with rule-based fallback
  - `DataManager` — CRUD operations and persistent storage (JSON)
  - `visualizations` — interactive chart creation (Plotly)
  - `AIAgentOrchestrator` — coordinates all specialized agents and manages memory

### Data Storage

- **JSON file storage** (`expenses.json`) for simple persistence
- **Pandas DataFrames** for in-memory manipulation and analytics
- Expense schema: `date, merchant, amount, category, confidence, description`

---

## 🧠 AI Agent System

- **Multi-Agent Orchestrator**: Routes tasks and composes agent outputs into unified results
- **Agent Memory**: Contextual memory to improve personalization and categorization over time
- **LLM Integration**: Groq models (e.g., `llama-3.3-70b-versatile`) via `langchain-groq` for reasoning, extraction, and recommendations

---

## 🔐 Authentication & Security

- **API keys** are managed via environment variables (e.g., `GROQ_API_KEY`, `OPENAI_API_KEY`)
- This repository currently targets a single-user setup (no user accounts or login). Consider adding authentication for multi-user deployments.

---

## 📦 Requirements

A `requirements.txt` should include at least:

```
streamlit
groq
langchain-groq
pytesseract
pillow
pandas
plotly
numpy
```

Plus development utilities: `datetime`, `re`, and `io` (standard library).

> Note: Tesseract OCR must be installed on the host machine for `pytesseract` to work.

---

## 📁 Project Structure

```
Expense-Tracking-Agent/
├─ app.py                 # Streamlit app entrypoint
├─ ai_agent_orchestrator.py  # AIAgentOrchestrator and coordination logic
├─ utils 
  ├─ data_manager.py
  ├─ ocer_processor.py
  ├─ visualizations.py
  └─ styles.py
├─ expenses.json          # Persistent expense storage
├─ requirements.txt
└─ README.md
```

---

## 🛠 Installation & Quick Start

1. **Clone the repo**

```bash
git clone https://github.com/Bilal-Ahmad-5/Expense-Tracking-Agent.git
cd Expense-Tracking-Agent
```

2. **Create a virtual environment & install**

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

3. **Set environment variables**

```bash
export GROQ_API_KEY="your_groq_api_key"
```

4. **Run the app**

```bash
streamlit run app.py
```

---

## 🎯 Features

- OCR-based receipt scanning with AI-enhanced structure extraction
- Intelligent expense categorization with confidence scoring
- Personalized budgets and practical budgeting tips following the 50/30/20 principle
- Interactive spending analytics and predictive forecasts
- Simple file-based persistence for easy setup and portability

---

## 🔮 Roadmap & Future Enhancements

- Add multi-user authentication and role-based access
- Move storage to a cloud database (Postgres / MongoDB) for scalability
- Bank integration (Plaid-like) to import transactions automatically
- Mobile-friendly UI and native mobile app wrapper
- Extend agent plugin system for third-party integrations

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request. When contributing, include tests and clear documentation for any new features.

---

## 📜 License

This project is released under the **MIT License**. See the `LICENSE` file for details.

---

## 🙋‍♀️ Contact

For support or questions, open an issue on the repository or contact the maintainer at `your.email@example.com`.

---

*Made with care — built to help people manage money confidently.*

