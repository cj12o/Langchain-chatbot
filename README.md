# 🚀 Langchain Chatbot

A **personal chatbot project** built to learn and apply practical concepts in conversational AI, LangChain, vector stores, and modern backend/frontend development.

---

## 📁 **Project Structure**
<pre>
Langchain_chatbot/
├── backend/ # FastAPI or server-side code
│ ├── main.py # Example backend entry point
│ └── ...
├── frontend/ # Frontend UI (Streamlit / Gradio / React)
│ ├── Home.py # Example UI entry point
│ └── ...
├── chroma_db_dir/ # Local vector DB storage (ignored in Git)
├── requirements.txt # Python dependencies
├── .gitignore # Ignored files and folders
└── README.md # This file
</pre>


---

## 🎯 **Project Objective**

The goal of this project is to:
- 🧠 Learn how to build production-style chatbot apps using **LangChain**
- ⚙️ Integrate **sessional context** and **RAG (Retrieval-Augmented Generation)**
- 🗂️ Use a **Chroma vector database** to store embeddings for context retrieval
- 💻 Create a **frontend UI** for smooth user interaction
- 🔄 Maintain conversation context across sessions

---

🔑 Key Features:
• Session-based context memory – maintains conversational flow within and across sessions
• Previous session RAG toggle – reuse knowledge from past chats efficiently
• Automated summarization – at session end, summarises chats to build an optimized vector DB for future sessions
• Real-time token streaming – significantly reduces Time To First Token (TTFT) and improves user experience
• Detailed metrics logging – TTFT, input/output tokens per response to analyze performance
• Clean UI – view chat history session-wise, date-wise, or in entirety, and export in JSON format
• Reset session context on-demand – no need to restart sessions manually

🛠️ Tech Stack:
• LangChain – prompt templates and plug-and-play model integration
• FastAPI – backend APIs
• Streamlit – intuitive frontend UI
• MongoDB – chat and metrics storage
• LLMs – locally run via Ollama & LM Studio:
→ nomic-embed-text:v1.5 for embeddings
→ hermes-3-llama-3.2-3b as the main chat completion model


## ⚙️ **Setup Guide**

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Langchain_chatbot.git
cd Langchain_chatbot
```
2️⃣ Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```
3️⃣ Install Python dependencies
```bash
pip install -r requirements.txt
```


4️⃣ Run the backend
```bash
cd backend
uvicorn main:app --reload
```

5️⃣ Run the frontend
```bash
streamlit run Home.py
```

👤 Author
Chitransh Jain (cj12o)
🔗 LinkedIn <https://www.linkedin.com/in/chitransh-jain-71bbb3336/>
📧jchitransh@gmail.com

📄 License
This project is licensed under the MIT License — free to use and modify.

⭐ Support
If you like this project, feel free to ⭐ star the repo and connect on LinkedIn!
