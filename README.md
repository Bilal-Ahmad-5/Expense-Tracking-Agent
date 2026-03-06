# 💸 AI Agent Expense Tracker

> *Stop guessing where your money goes. Let AI figure it out for you.*

An intelligent expense tracking app that scans receipts, categorizes spending, builds personalized budgets, and predicts your financial future — all in one clean Streamlit interface.

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Bilal-Ahmad-5/Expense-Tracking-System.git
cd Expense-Tracking-Agent

# Set up environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key
export GOOGLE_API_KEY="your_api_key_here"

# Launch the app
streamlit run app.py
```

Open the printed URL in your browser — you're ready to go.

---

## ✨ What It Does

| Feature | Description |
|---------|-------------|
| 🧾 **Receipt Scanner** | Upload a photo — AI extracts merchant, amount, and date automatically |
| 🏷️ **Smart Categorization** | Learns to classify your expenses with confidence scoring |
| 📊 **Budget Advisor** | Builds a personalized 50/30/20 budget with actionable tips |
| 🔮 **Spending Insights** | Trend analysis, forecasts, and a spending health score |

---

## 🧠 How It Works

Four specialized AI agents collaborate behind every interaction:

| Agent | Job |
|-------|-----|
| 📷 **Receipt Scanner Agent** | OCR + AI extraction from uploaded images |
| 🏷️ **Categorization Agent** | Classifies expenses, improves with use |
| 💡 **Budget Advisor Agent** | Generates personalized budget recommendations |
| 📈 **Insights Agent** | Forecasts trends and scores your financial health |

An **orchestrator** coordinates all agents and maintains memory across sessions.

---

## ⚙️ Requirements

- Python 3.8+
- **Tesseract OCR** installed on your machine → [Install here](https://github.com/tesseract-ocr/tesseract)
- A **Google Gemini API key** → [Get one here](https://makersuite.google.com/app/apikey)

---

## 🗂️ Project Structure

```
Expense-Tracking-Agent/
├── app.py                      # App entrypoint
├── ai_agent_orchestrator.py    # Agent coordination logic
├── utils/
│   ├── data_manager.py         # Storage & CRUD
│   ├── ocr_processor.py        # Receipt scanning
│   ├── visualizations.py       # Charts & graphs
│   └── styles.py               # UI styling
├── expenses.json               # Local expense storage
└── requirements.txt
```

---

## 🔮 What's Coming Next

- Multi-user login and role-based access
- Cloud database support (PostgreSQL / MongoDB)
- Automatic bank transaction imports
- Mobile-friendly UI

---

## 🤝 Contributing

Got an improvement in mind? Fork it, build it, and open a pull request. Issues and feature requests are welcome too.

---

## 📄 License

MIT — free to use and build upon.
**Contact:** hey.bilalahmad@gmail.com

---
