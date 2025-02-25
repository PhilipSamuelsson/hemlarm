sequenceDiagram
    participant PIR as Rörelsesensor (PIR)
    participant Pico as Raspberry Pi Pico W
    participant Flask as Flask Backend Server
    participant Frontend as Frontend

    PIR ->> Pico: Upptäcker rörelse
    Pico ->> Flask: Skickar data via HTTP/WebSocket
    Flask ->> Frontend: Skickar uppdatering i realtid
```
