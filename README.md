# Agentic-Energy-AI
Built an agentic AI pipeline to process Duke Energy bills using a multi-cloud setup: Oracle object storage for raw data ingestion, Oracle-hosted Milvus for vector storage, Ollama LLM for RAG-based insights, and Databricks for analytics dashboards. The system updates automatically with each new bill.

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

