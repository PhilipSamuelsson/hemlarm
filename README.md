# Diagram

```mermaid
graph TD
    subgraph Edge Devices
        P1[Raspberry Pi Pico W #1]
        P2[Raspberry Pi Pico W #2]
        Pn[Raspberry Pi Pico W #3]
    end
    
    subgraph Gateway
        RP["Raspberry Pi (Central Enhet)"]
    end
    
    subgraph Backend
        Server[Webbserver]
        DB[Databas]
    end
    
    subgraph Notifications
        Phone[Telefon/Pushnotiser]
        Email[E-post]
    end

    %% Connections
    P1 -->|MQTT/HTTP| RP
    P2 -->|MQTT/HTTP| RP
    Pn -->|MQTT/HTTP| RP
    RP -->|Samlar in data| Server
    Server -->|Lagrar data| DB
    Server -->|Skickar notifiering| Phone
    Server -->|Skickar notifiering| Email
```
## Tech stack

✅ Frontend – React (med Next.js) eller Vue (med Nuxt.js)
✅ Backend – Python (FastAPI eller Flask) för API & datahantering
✅ Mikrokontroller – Python (MicroPython) på Raspberry Pi Pico W
✅ Gateway & Server – Python (Raspberry Pi 3) med MQTT eller WebSockets
✅ Databas – SQLite, PostgreSQL eller Firebase (beroende på behov)
