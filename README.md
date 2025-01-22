# Diagram

```mermaid

graph TD
    subgraph Edge Devices
        P1[Raspberry Pi Pico W #1]
        P2[Raspberry Pi Pico W #2]
        Pn[Raspberry Pi Pico W #N]
    end
    
    subgraph Gateway
        RP[Raspberry Pi (Central Enhet)]
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
