# 🌱 AgroNexus — Sistema de Monitoramento Agrícola

Projeto desenvolvido para monitoramento em tempo real de umidade do solo, temperatura e umidade do ar usando Arduino Mega conectado via USB ao computador.

---

## 📋 Descrição

O AgroNexus é um sistema embarcado que coleta dados de sensores agrícolas e exibe as informações em um painel web moderno, acessível diretamente pelo Google Chrome via conexão USB — sem necessidade de internet ou módulos Wi-Fi.

---

## 🛠️ Hardware Utilizado

| Componente | Descrição |
|---|---|
| Arduino Mega 2560 | Microcontrolador principal |
| DHT11 | Sensor de temperatura e umidade do ar |
| Sensor Capacitivo I2C | Sensor de umidade do solo |
| Protoboard | Placa de ensaio para conexões |
| Cabo USB | Comunicação com o computador |

---

## 🔌 Esquema de Conexões

### DHT11
| Pino DHT11 | Pino Arduino Mega |
|---|---|
| VCC | 5V |
| GND | GND |
| DATA | Pino 2 |

### Sensor de Umidade do Solo (I2C)
| Pino Sensor | Pino Arduino Mega |
|---|---|
| VCC | 3.3V ou 5V |
| GND | GND |
| SDA | Pino 20 |
| SCL | Pino 21 |

---

## 📁 Estrutura do Projeto

```
agronexus/
├── agronexus.ino         # Firmware do Arduino Mega
├── agronexus_bridge.py   # Script Python (alternativa ao HTML)
├── agronexus_chrome.html # Painel web (interface principal)
└── README.md             # Este arquivo
```

---

## 🚀 Como Usar

### Pré-requisitos
- Google Chrome instalado
- IDE Arduino instalada
- Biblioteca **DHT sensor library** (Adafruit) instalada na IDE

### Passo 1 — Gravar o firmware no Arduino
1. Abra `agronexus.ino` na IDE Arduino
2. Selecione: **Ferramentas → Placa → Arduino Mega 2560**
3. Selecione: **Ferramentas → Porta → COM6** (ou a porta do seu Arduino)
4. Clique na seta **→** para gravar
5. Aguarde **"Gravação concluída"**
6. Feche a IDE Arduino

### Passo 2 — Abrir o painel web
1. Abra o arquivo `agronexus_chrome.html` no **Google Chrome**
2. Clique em **"Conectar Arduino"**
3. Selecione a porta **Dispositivo Serial USB** na lista
4. Clique em **Conectar**

Os dados de umidade do solo, temperatura e umidade do ar aparecerão em tempo real! ✅

---

## ⚙️ Como Funciona

```
Arduino Mega → (USB) → Google Chrome → Painel Web
     ↑
  DHT11 + Sensor de Solo
```

1. O Arduino lê os sensores a cada 2 segundos
2. Envia os dados em formato JSON pela porta USB:
   ```json
   {"solo":45,"temp":24.5,"umid":60.0}
   ```
3. O Chrome recebe os dados via **Web Serial API**
4. O painel atualiza os valores em tempo real

---

## 📚 Bibliotecas Arduino

Instale pela IDE em **Ferramentas → Gerenciar Bibliotecas**:
- `DHT sensor library` — Adafruit
- `Adafruit Unified Sensor` — Adafruit
- `Wire` — já incluída na IDE

---

## ⚠️ Observações

- O painel web funciona **apenas no Google Chrome**
- A IDE Arduino e o painel web **não podem usar a porta ao mesmo tempo**
- Se o solo mostrar 0%, calibre os valores `SECO` e `MOLHADO` no `agronexus.ino`

---
