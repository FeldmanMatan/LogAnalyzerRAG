# 🗺️ תכנון פרויקט גרסה 3 | Project Plan V3: Advanced Teaching, Hybrid RAG & Multi-Agent System

## 🎯 המטרה הסופית | The Grand Vision
**HE:** שדרוג המערכת למוצר Enterprise: ארכיטקטורת LangGraph מרובת-סוכנים עם זיכרון תמידי (SQLite). המערכת תכלול מנוע למידה (Teaching Engine) לקליטת הקשר אנושי, ארגז כלים היברידי (סמנטי + סטטיסטי), יכולת ניתוח אצווה רוחבית (Batch Analysis), ושכבת הפשטה להחלפת מנועי AI (לסביבות רשת סגורות).
**EN:** Upgrading the system to an Enterprise product: A Multi-Agent LangGraph architecture with persistent memory (SQLite). Featuring a Teaching Engine for human context, a Hybrid Toolset (semantic + statistical), Batch Analysis capabilities, and an AI Abstraction layer for closed-network environments.

---

## 🧱 אבן בניין 9: זיכרון תמידי | Building Block 9: Persistent Memory (SQLite)
**מטרה (Goal):** שמירת היסטוריית השיחות והקשר ניתוח הלוגים גם לאחר סגירת התוכנה. / Save conversation history across sessions.
- [ ] 9.1 הטמעת `SqliteSaver` מתוך LangGraph.
- [ ] 9.2 הגדרת State Schema שיכיל את נתוני השיחה והסטטוס הנוכחי.

---

## 🧱 אבן בניין 10: מנוע הלמידה וההקשר האנושי | Building Block 10: The Teaching Engine
**מטרה (Goal):** יכולת "ללמד" את המערכת מה תקין ומה לא (הזנת לוגים נומינליים ואנומליות מוכרות + הסבר אנושי). / Ability to teach the system using nominal logs, known anomalies, and human explanations.
- [ ] 10.1 בניית סקריפט אוטומטי (Bulk Mode) שקורא קובץ `teaching_config.json` ומזריק ל-ChromaDB.
- [ ] 10.2 הוספת פקודת `teach` ל-CLI להזנה אינטראקטיבית.

---

## 🧱 אבן בניין 11: ארגז כלים היברידי | Building Block 11: Hybrid Toolset
**מטרה (Goal):** שילוב כלים סטטיסטיים מדויקים לצד החיפוש הסמנטי. / Integrate exact statistical tools alongside semantic search.
- [ ] 11.1 יצירת `statistical_analysis_tool` מבוסס Pandas לניתוח חותמות זמן, ממוצעים וספירות.
- [ ] 11.2 שדרוג כלי ה-RAG הקיימים כך שידעו לשלוף את ה"הסבר האנושי" מה-Metadata שנוצר באבן בניין 10.

---
# 🗺️ תכנון פרויקט גרסה 3 | Project Plan V3: Advanced Teaching, Hybrid RAG & Multi-Agent System (Updated)

## 🎯 המטרה הסופית | The Grand Vision
**HE:** שדרוג המערכת למוצר Enterprise: ארכיטקטורת LangGraph מרובת-סוכנים עם זיכרון תמידי (SQLite). המערכת תכלול מנוע למידה (Teaching Engine) לקליטת הקשר אנושי, ארגז כלים היברידי (סמנטי + סטטיסטי), יכולת ניתוח אצווה רוחבית (Batch Analysis), ושכבת הפשטה להחלפת מנועי AI (לסביבות רשת סגורות).
**EN:** Upgrading the system to an Enterprise product: A Multi-Agent LangGraph architecture with persistent memory (SQLite). Featuring a Teaching Engine for human context, a Hybrid Toolset (semantic + statistical), Batch Analysis capabilities, and an AI Abstraction layer for closed-network environments.

---

## 🧱 אבן בניין 9: זיכרון תמידי | Building Block 9: Persistent Memory (SQLite)
**מטרה (Goal):** שמירת היסטוריית השיחות והקשר ניתוח הלוגים גם לאחר סגירת התוכנה. / Save conversation history across sessions.
- [x] 9.1 הטמעת `SqliteSaver` מתוך LangGraph.
- [x] 9.2 הגדרת State Schema שיכיל את נתוני השיחה והסטטוס הנוכחי.

---

## 🧱 אבן בניין 10: מנוע הלמידה וההקשר האנושי | Building Block 10: The Teaching Engine
**מטרה (Goal):** יכולת "ללמד" את המערכת מה תקין ומה לא (הזנת לוגים נומינליים ואנומליות מוכרות + הסבר אנושי). / Ability to teach the system using nominal logs, known anomalies, and human explanations.
- [x] 10.1 בניית סקריפט אוטומטי (Bulk Mode) שקורא קובץ `teaching_config.json` ומזריק ל-ChromaDB.
- [x] 10.2 הוספת פקודת `teach` ל-CLI להזנה אינטראקטיבית.
- [x] **10.3 [התווסף בביצוע]:** הרחבת פקודת ה-`teach` לתמיכה בשמירה כפולה (Dual-Save) - הזרקת המידע גם ל-VectorDB (הקשר אנושי) וגם ל-SQLite (לניתוח סטטיסטי).

---

## 🧱 אבן בניין 11: ארגז כלים היברידי | Building Block 11: Hybrid Toolset
**מטרה (Goal):** שילוב כלים סטטיסטיים מדויקים לצד החיפוש הסמנטי. / Integrate exact statistical tools alongside semantic search.
- [x] 11.1 יצירת `statistical_analysis_tool` מבוסס Pandas לניתוח חותמות זמן, ממוצעים וספירות.
- [x] 11.2 שדרוג כלי ה-RAG הקיימים כך שידעו לשלוף את ה"הסבר האנושי" מה-Metadata שנוצר באבן בניין 10.
- [x] **11.3 [התווסף בביצוע]:** הפשטת סכמת הלוגים (Dynamic Schema). יצירת `log_format.json` המאפשר תמיכה בסוגי לוגים מרובים (`app_logs`, `network_logs`) ללא שינוי קוד פייתון.
- [x] **11.4 [התווסף בביצוע]:** הפרדת DDL מ-DML. יצירת סקריפט `init_stats_db.py` לאתחול חד-פעמי של הטבלאות והורדת עומס ממנוע ה-Ingestion.
- [x] **11.5 [התווסף בביצוע]:** הוספת יכולת סינון טווח זמנים (`start_time`, `end_time`) בכלי הסטטיסטי, כדי שהסוכן יוכל לתחקר חלונות זמן ספציפיים.

---

## 🧱 אבן בניין 12: צוות הסוכנים (LangGraph) | Building Block 12: Multi-Agent Architecture
**מטרה (Goal):** הקמת צוות המומחים (Map-Reduce). / Establish the expert team (Map-Reduce).
- [x] 12.1 צומת `Baseline Specialist`: מומחה לייצור "ספר חוקים" (Profile) מתוך לוגי ה-Golden.
- [x] 12.2 צומת `Investigator Agent`: סוכן שמשתמש בכלים (RAG + Stats) כדי לחקור שגיאות מול ה-Baseline. *כולל מנגנון חילוץ טקסט נקי מ-Content Blocks.*
- [x] 12.3 צומת `Supervisor`: מנהל העבודה שמנתב משימות ומרכז את התוצרים הסופיים לגרף זרימה.

---

## 🧱 אבן בניין 13: ניתוח באצווה | Building Block 13: Batch Analysis Mode
**מטרה (Goal):** היכולת לזרוק כמות גדולה של לוגים ולנתח אותם במקביל מול ה-Baseline. / Analyze massive amounts of logs concurrently against the baseline.
- [x] 13.1 הוספת פקודת CLI מרכזית `analyze all`.
- [x] 13.2 הזרמת הלוגים החדשים ל-Investigator בחלקים (Chunks/Batches) באמצעות עיבוד מקבילי (ThreadPoolExecutor), וסיכום (Synthesis) לדוח מנהלים נקי.

---

## 🧱 אבן בניין 14: הפשטת שירות ה-AI (Pluggability) | Building Block 14: AI Service Abstraction
**מטרה (Goal):** תמיכה בהחלפה קלה של מודל ה-AI לעבודה בארגונים (Closed Networks). / Easy swapping of AI models via config.
- [x] 14.1 עדכון `ai_service.py` לשימוש ב-Factory Pattern. תמיכה מובנית ב-Gemini (ענן) וב-Ollama (מקומי) הנשלטת דרך קובץ `.env`.