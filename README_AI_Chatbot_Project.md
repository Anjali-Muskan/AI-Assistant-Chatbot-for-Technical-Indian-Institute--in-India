
# AI-Powered Student Assistance Chatbot for Technical Education Institutes in India

## 📌 Project Overview

This project is an AI-powered chatbot designed to simplify the admission process for technical education institutes in India. It serves as a centralized virtual assistant that answers student queries related to eligibility, entrance exams, scholarships, fee structures, hostel facilities, and placements. The chatbot supports **multilingual** and **voice-based interactions**, aiming to improve accessibility for users from diverse linguistic backgrounds.

---

## 🚀 Features

- 💬 **Text and Voice-Based Query Handling**
- 🌐 **Multilingual Support** (Hindi, Tamil, Telugu, Bengali, etc.)
- 🧠 **Session Memory** for contextual conversations
- 🎯 **Profile-Based Recommendations** for institutes and scholarships
- 🔍 **Real-Time Information Filtering** from verified sources (AICTE, UGC)
- 🌓 **Dark/Light Theme Toggle** in the GUI
- 📊 **Analytics Potential** for educational institutions and policymakers

---

## 🛠️ Tech Stack

| Component | Technologies |
|----------|--------------|
| Frontend (GUI) | Tkinter (Python) |
| Backend | Flask, Gemini API |
| AI/NLP | Google Gemini Pro, gTTS, edge-tts |
| Data Handling | Pandas, CSV |
| Voice Processing | SpeechRecognition, pygame |
| Deployment | Local Machine / Cloud (AWS, GCP Ready) |

---

## 📂 Folder Structure

```
├── chatbot_core.py         # Core logic and API handling
├── gui.py                  # Tkinter-based GUI
├── recommender.py          # Profile-based recommendation logic
├── sample_institutions.csv# Dataset for institute recommendations
├── requirements.txt        # List of dependencies
├── README.md               # Project overview and setup
```

---

## 🧪 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/student-chatbot-ai.git
cd student-chatbot-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Chatbot GUI
```bash
python gui.py
```

---

## 🧠 Functional Highlights

- Enter queries like:  
  > "What are the eligibility criteria for JEE in Maharashtra?"  
  > "मुझे तमिलनाडु में इंजीनियरिंग कॉलेज चाहिए।"

- Supports **voice input/output** via buttons.
- Filters institute data based on:
  - Location
  - Exam (e.g., JEE Main, CET)
  - Category (General/OBC/SC/ST)

---

## 🔒 Data Sources

- [AICTE](https://www.aicte-india.org/)
- [UGC](https://www.ugc.ac.in/)
- Sample datasets based on public educational data

---

## 📈 Future Enhancements

- ✅ API integration with live education portals (AICTE, UGC)
- 📱 Mobile app version (Flutter/React Native)
- 🧬 Deep learning for improved personalization
- 💬 Chatbot feedback and self-learning loop

---

## 👩‍💻 Developers

- **Tanmay Verma** – 21BCT0309  
- **Anjali Muskan** – 21BDS0375  
*VIT, Vellore*

---

## 📄 License

This project is intended for academic use and demonstration only. Contact the developers for any collaboration or deployment.
