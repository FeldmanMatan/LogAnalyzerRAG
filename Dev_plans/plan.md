# 📋 מעקב פרויקט ניתוח לוגים | Log Analyzer RAG Project Tracker

## אבן דרך 1: תשתית ומעטפת (Milestone 1: Infrastructure & AI Wrapper)
- [x] 1.1 הגדרת משתני סביבה (Environment Variables Setup - `.env`)
- [x] 1.2 ניהול תלויות (Dependency Management - `requirements.txt` & `truststore`)
- [x] 1.3 יצירת מעטפת AI (AI Service Wrapper Creation - `ai_service.py`)
- [x] 1.4 סקריפט בדיקה ראשי וחיבור ל-API (Main Entry Point & Connection Test - `main.py`)

## אבן דרך 2 (שלב א'): קליטת נתונים (Milestone 2 - Stage A: Ingestion Pipeline)
- [x] 2.1 קריאת קובץ הלוג (Log File Loading)
- [x] 2.2 פיצול טקסט (Text Chunking with Langchain-text-splitters)
- [x] 2.3 יצירת וקטורים ושמירה במסד נתונים (Embedding & Insertion to VectorDB/ChromaDB)

## אבן דרך 3 (שלב ב'): שליפה (Milestone 3 - Stage B: Retrieval)
- [x] 3.1 יצירת וקטור לשאילתת המשתמש (User Query Embedding)
- [x] 3.2 חיפוש דמיון (Similarity Search in VectorDB)
- [x] 3.3 איסוף ובניית ההקשר (Context Building)

## אבן דרך 4 (שלב ג'): יצירת תגובה (Milestone 4 - Stage C: Generation - RAG)
- [x] 4.1 בניית הפרומפט (Prompt Construction: Instructions + Context + Question)
- [x] 4.2 קריאה למודל השפה (LLM Call)
- [x] 4.3 הצגת התשובה הסופית (Final Answer Presentation)

---

## 📂 מבנה הפרויקט ותפקיד הקבצים (Project Structure & File Roles)

### תיקיית השורש (Root Directory)
* **`.env`**: קובץ הגדרות סביבה. מכיל נתונים רגישים כמו מפתח ה-API של גוגל.  
  *Environment variables file. Contains sensitive data like the Google API key.*
* **`requirements.txt`**: רשימת הספריות והחבילות החיצוניות הנדרשות לפרויקט.  
  *List of required external libraries and packages for the project.*
* **`ai_service.py`**: מעטפת ה-AI. מרכז את כל ההגדרות והאתחול של מודלי השפה וה-Embeddings. מאפשר החלפה קלה של תשתית בעתיד (למשל ל-Ollama).  
  *The AI Wrapper. Centralizes LLM and Embeddings initialization. Allows easy swapping of AI providers in the future.*
* **`main.py`**: סקריפט הבדיקה הראשוני שכתבנו כדי לוודא חיבור תקין ל-API דרך חומת האש.  
  *Initial test script used to verify API connectivity through the firewall.*

### תיקיית `data/`
* **מטרה:** אחסון קבצי הלוג הגולמיים לפני העיבוד.  
  *Purpose: Storage for raw log files before processing.*
* **`sample.log`**: קובץ לוג קטן שנוצר לצורכי פיתוח ובדיקות.  
  *A small log file created for development and testing purposes.*

### תיקיית `chroma_db/`
* **מטרה:** מסד הנתונים הוקטורי המקומי של Chroma. נוצר אוטומטית ומכיל את הלוגים המקודדים למספרים.  
  *Purpose: The local Chroma vector database. Auto-generated, containing the numerically encoded logs.*

### תיקיית `ingestion/` (שלב א')
* **`log_processor.py`**: קורא את קובץ הלוג הגולמי ומפצל אותו לחתיכות קטנות (Chunks) שמתאימות למודל השפה.  
  *Reads the raw log file and splits it into small chunks suitable for the language model.*
* **`db_builder.py`**: לוקח את החתיכות, ממיר אותן לוקטורים דרך ה-AI, ושומר אותן בתוך מסד הנתונים (`chroma_db`).  
  *Takes chunks, converts them to vectors via AI, and saves them into the vector database.*

### תיקיית `retrieval/` (שלב ב')
* **`retriever.py`**: מקבל שאלת משתמש, מחפש במסד הנתונים (חיפוש סמנטי), ושולף את שורות הלוג הרלוונטיות ביותר.  
  *Takes a user query, searches the database (semantic search), and retrieves the most relevant log lines.*

### תיקיית `generation/` (שלב ג')
* **`rag.py`**: ה"מוח" המחבר. לוקח את שורות הלוג שנשלפו יחד עם השאלה, מרכיב פרומפט מקצועי, ושולח למודל השפה (LLM) כדי לקבל תשובה סופית.  
  *The connecting "brain". Takes retrieved log lines and the query, builds a professional prompt, and sends it to the LLM for a final answer.*