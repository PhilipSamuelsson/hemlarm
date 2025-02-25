```mermaid
graph TD;
    PIR["Rörelsesensor"] -->|"Upptäcker rörelse"| Pico["Raspberry Pi Pico W"];
    Pico -->|"Skickar data via HTTP/WebSocket"| Flask["Flask Backend Server"];
    Flask -->|"Skickar uppdatering i realtid"| Frontend["Frontend"];
```
