# Agentic-Energy-AI
Built an agentic AI pipeline to process Duke Energy bills using a multi-cloud setup: Oracle object storage for raw data ingestion, Oracle-hosted Milvus for vector storage, Ollama LLM for RAG-based insights, and Databricks for analytics dashboards. The system updates automatically with each new bill.

---

                        ┌───────────────────────────────────────┐
                        │ Oracle Object Storage (Always Free)   │
                        │ - Stores raw Duke Energy bills (PDFs) │
                        │ - Acts as long-term archive           │
                        └───────────────────────────────────────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │ Polling Service (Python, runs on server / cron job)        │
        │ - Detects new files in Oracle bucket                       │
        │ - Downloads raw bill                                       │
        │ - Sends bill to Ollama LLM for parsing                     │
        └────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │ Ollama LLM (Local CPU)                                     │
        │ - Model: Phi-3-mini or LLaMA 3.1 8B quant                  │
        │ - Prompts: "Extract fields: {Bill Date, Period, kWh,       │
        │    Total Amount, Fixed Charges, Taxes, Surcharges}"        │
        │ - Output: Structured JSON                                  │
        │   e.g. {                                                   │
        │     "bill_date": "2024-07-01",                             │
        │     "usage_kWh": 845,                                      │
        │     "total_amount": 210.50,                                │
        │     "tax": 15.30,                                          │
        │     "surcharge": 25.00                                     │
        │   }                                                        │
        └────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │ Databricks CE (Free SQL Catalog + Delta Tables)            │
        │ - Store structured records as Delta table:                 │
        │   bills_delta(                                             │
        │     bill_date DATE,                                        │
        │     billing_period STRING,                                 │
        │     usage_kWh FLOAT,                                       │
        │     total_amount FLOAT,                                    │
        │     tax FLOAT,                                             │
        │     surcharge FLOAT                                        │
        │   )                                                        │
        │ - Supports SQL queries + dashboards                       │
        │ - Example queries:                                         │
        │   "SELECT AVG(total_amount) WHERE year=2024"               │
        │   "SELECT SUM(usage_kWh) GROUP BY year"                    │
        └────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │ User-Facing LLM (Ollama Agent)                             │
        │ - Accepts natural language queries:                        │
        │   e.g. "Compare my summer bills in 2023 vs 2024"           │
        │ - Translates query → SQL                                   │
        │ - Executes SQL on Databricks SQL Catalog                   │
        │ - Returns final answer (text + charts)                     │
        └────────────────────────────────────────────────────────────┘



---

                ┌────────────────────────────────────┐
                │   Oracle Object Storage (Always Free) │
                │   - Duke bills PDFs/CSVs (raw)        │
                │   - 10GB forever free                 │
                └────────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │   Polling Script (Python, cron job on server)│
        │   - Check new files in Oracle bucket          │
        │   - Parse bills (usage, charges, date)        │
        │   - Extract text chunks for embeddings        │
        │   - Generate embeddings (MiniLM on CPU)       │
        │   - Upsert into Milvus                        │
        │   - Save structured CSV/Parquet locally       │
        └──────────────────────────────────────────────┘
                               │
                               ▼
     ┌────────────────────┐         ┌─────────────────────────┐
     │  Milvus Standalone │         │  Databricks CE (Free)   │
     │  - Vector DB       │         │  - Load structured CSV  │
     │  - Semantic memory │◄────────│  - Create Delta Tables  │
     └────────────────────┘         │  - SQL Dashboards       │
                               ▲    └─────────────────────────┘
                               │
        ┌──────────────────────────────────────────────┐
        │   Ollama Agent (Local, CPU only)             │
        │   - Retrieve context from Milvus             │
        │   - Reason over bills (trend, compare)       │
        │   - Call Python funcs for math/plots         │
        │   - Optionally call Databricks for charts    │
        │   - Output: Answer + Viz (matplotlib or link)│
        └──────────────────────────────────────────────┘

