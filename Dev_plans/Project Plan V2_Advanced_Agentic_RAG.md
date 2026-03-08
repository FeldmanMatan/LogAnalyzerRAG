# 🗺️ תכנון פרויקט גרסה 2 | Project Plan V2: Advanced Agentic RAG

## 🎯 המטרה הסופית | The Grand Vision
**HE:** מערכת AI אינטראקטיבית לניתוח לוגים, המבוססת על ארכיטקטורת Agentic RAG. המערכת קולטת נתונים במקביליות (Threads), מסווגת אותם אוטומטית ללוגים תקינים (Golden) ולוגים שוטפים, ומשתמשת בסוכני AI הפועלים בזמן אמת כדי לחקור, להשוות, ולענות על שאלות מורכבות תוך שמירה על הקשר השיחה.
**EN:** An interactive AI log analysis system based on Agentic RAG architecture. The system ingests data concurrently (Threads), automatically classifies it into normal (Golden) and standard logs, and uses real-time AI agents to investigate, compare, and answer complex questions while maintaining conversational context.

---

## 🧱 אבן בניין 5: קליטה מקבילית ותיוג | Building Block 5: Concurrent Ingestion & Metadata
**מטרה (Goal):** ייעול שלב בניית מסד הנתונים בעזרת תהליכונים והוספת תגיות זיהוי לכל שורת לוג. / Optimize the DB build phase using threads and add identification tags to each log line.

- [x] 5.1 שילוב `ThreadPoolExecutor` בקובץ `log_processor.py` לעיבוד קבצים במקביל. / Integrate `ThreadPoolExecutor` for concurrent file processing.
- [x] 5.2 הוספת לוגיקת תיוג (Metadata): זיהוי המילה "golden" בשם הקובץ ותיוג בהתאם (`status: golden` / `status: standard`). / Add Metadata tagging logic based on filename.
- [x] 5.3 שדרוג `db_builder.py` לשמירת החתיכות המתוייגות במסד הנתונים `chroma_db`. / Update `db_builder.py` to save tagged chunks in ChromaDB.
- [x] **בדיקת סיום (Acceptance Test):** שליפת וקטור בודד מה-DB ווידוא שהשדות `status` ו-`source` קיימים ומדויקים. / Retrieve a single vector and verify `status` and `source` metadata.

---

## 🧱 אבן בניין 6: ארגז הכלים של הסוכן | Building Block 6: The Agent's Toolset
**מטרה (Goal):** יצירת פונקציות עצמאיות (Tools) שהסוכן יוכל להפעיל בעצמו לסינון מידע. / Create independent functions (Tools) the agent can trigger to filter information.

- [x] 6.1 כתיבת כלי `get_standard_logs` לחיפוש עם פילטר `status: standard`. / Create `get_standard_logs` tool with standard filter.
- [x] 6.2 כתיבת כלי `get_golden_logs` לחיפוש עם פילטר `status: golden`. / Create `get_golden_logs` tool with golden filter.
- [x] **בדיקת סיום (Acceptance Test):** קריאה ידנית לפונקציות בקוד ומוודאים שחיפוש ה-Golden מחזיר רק שורות מקובץ ה-Baseline. / Manually call functions to ensure Golden search only returns Baseline logs.

---

## 🧱 אבן בניין 7: ליבת הסוכן והראוטר | Building Block 7: Agent Core & Prompt Engineering
**מטרה (Goal):** בניית ה"מוח" שמקבל החלטות ובוחר אילו כלים להפעיל. / Build the "brain" that makes decisions and selects tools.

- [x] 7.1 אתחול אובייקט Agent של LangChain עם מודל Gemini. / Initialize LangChain Agent with Gemini model.
- [x] 7.2 חיבור (Binding) הכלים מאבן בניין 6 לסוכן. / Bind tools from block 6 to the agent.
- [x] 7.3 כתיבת System Prompt מתקדם המחייב השוואה ל-Baseline בעת חיפוש חריגות. / Write an advanced System Prompt enforcing baseline comparison for anomalies.
- [x] **בדיקת סיום (Acceptance Test):** הדפסת מהלך המחשבה של הסוכן (Scratchpad) כדי לוודא הפעלה רציפה של שני הכלים (Golden + Standard) להשוואה. / Print agent's scratchpad to verify sequential tool execution for comparison.

---

## 🧱 אבן בניין 8: ממשק צ'אט וזיכרון | Building Block 8: Interactive CLI & Memory
**מטרה (Goal):** עטיפת המערכת באפליקציית טרמינל נוחה עם זיכרון שיחה. / Wrap the system in a user-friendly terminal app with conversational memory.

- [x] 8.1 יצירת לולאת `while True` לקבלת קלט רציף (קובץ `app.py`). / Create a `while True` loop for continuous input.
- [x] 8.2 שילוב Conversation Memory בתוך הסוכן. / Integrate Conversation Memory into the agent.
- [x] **בדיקת סיום (Acceptance Test):** ניהול שיחה רציפה ושאלת שאלות המשך ללא ציון הנושא מחדש. / Conduct a continuous conversation with follow-up questions without restating the context.

---

## 🚀 שלב עתידי (Phase 3): ארכיטקטורת מרובת סוכנים | Multi-Agent Architecture
**HE:** כאשר המערכת תגדל, נשדרג אותה בעזרת LangGraph לעבודה עם צוות סוכנים מבוזר.
**EN:** As the system scales, we will upgrade it using LangGraph to work with a distributed team of agents.

* **Baseline Specialist Agent:** מומחה ל-Golden Logs בלבד. / Expert in Golden Logs only.
* **Investigator Agent:** חוקר לוגים שוטפים לאיתור שגיאות. / Investigates standard logs for errors.
* **Supervisor Agent:** מנהל את התהליך, מקבל מידע משני הסוכנים במקביל, ומפיק דוח השוואה סופי. / Orchestrates the process, receives data from both agents concurrently, and generates a final comparison report.