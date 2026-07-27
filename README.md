                  ┌────────────────────────────────────────┐
                  │          Admin Panel Client            │
                  │  (UI for Config, Logs, Status, Curds)  │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │          Data Sync Engine              │
  ┌──────────────►│   (Core Application Logic & Routing)   │◄──────────────┐
  │               └───────────────────┬────────────────────┘               │
  │                                   │                                    │
  │                                   ▼                                    │
┌─┴──────────────────────┐ ┌──────────┴─────────────┐ ┌────────────────────┴───┐
│     Cron Scheduler     │ │    Database Layer      │ │    Webhook Listener    │
│  (Polling/Freshness)   │ │ (Persistent Storage)   │ │  (Real-Time Ingestion) │
└────────────────────────┘ └────────────────────────┘ └────────────────────────┘
