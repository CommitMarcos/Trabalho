"""
AgroNexus - Bridge Python  (versão corrigida)
Lê JSON do Arduino via USB e gera index.html em tempo real.

Correções aplicadas:
  1. Escrita atômica do HTML (evita leitura de arquivo vazio/corrompido
     pelo browser durante a sobrescrita) — substitui open() direto.
  2. Separação do 'except' genérico: erros de JSON são silenciados,
     mas erros de I/O são exibidos para facilitar debug.
"""

import json
import os
import serial
import serial.tools.list_ports
import tempfile
import time

BAUDRATE     = 9600
ARQUIVO_HTML = "index.html"

print("=== Sistema AgroNexus Inicializado ===")
print("Certifique-se de fechar o Monitor Serial da IDE Arduino antes de rodar!\n")

# ------------------------------------------------------------------
# Detecção automática do Arduino — procura por Arduino Mega nas
# portas disponíveis. Se não achar pelo nome, tenta todas as COMs.
# ------------------------------------------------------------------
def encontrar_arduino():
    portas = list(serial.tools.list_ports.comports())
    
    # Primeira tentativa: procura pelo nome "Arduino" ou "CH340" (chip USB genérico)
    for p in portas:
        desc = (p.description or "").lower()
        if "arduino" in desc or "ch340" in desc or "mega" in desc:
            print(f"✅ Arduino encontrado automaticamente: {p.device} ({p.description})")
            return p.device

    # Segunda tentativa: lista todas as portas disponíveis e tenta conectar
    if portas:
        print("⚠️  Arduino não identificado pelo nome. Portas disponíveis:")
        for p in portas:
            print(f"   {p.device} — {p.description}")
        # Tenta a primeira disponível
        print(f"\n🔄 Tentando conectar em {portas[0].device}...")
        return portas[0].device

    return None

PORTA_ARDUINO = encontrar_arduino()

if not PORTA_ARDUINO:
    print("❌ Nenhuma porta COM encontrada.")
    print("   Verifique se o Arduino está conectado no USB e tente novamente.")
    exit(1)

try:
    arduino = serial.Serial(PORTA_ARDUINO, BAUDRATE, timeout=1)
    time.sleep(2)  # Aguarda o Arduino resetar e estabilizar
    print(f"✅ AgroNexus conectado na porta {PORTA_ARDUINO}!")
except Exception as e:
    print(f"❌ Erro de conexão na porta {PORTA_ARDUINO}.")
    print(f"   Dica: feche o Monitor Serial da IDE Arduino se estiver aberto.")
    print(f"   Detalhe técnico: {e}")
    exit(1)


# ------------------------------------------------------------------
# Escrita atômica: grava num arquivo temporário e depois renomeia.
# Isso garante que o browser nunca leia um arquivo pela metade.
# ------------------------------------------------------------------
def salvar_html_atomico(conteudo: str, destino: str) -> None:
    dir_destino = os.path.dirname(os.path.abspath(destino))
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8",
        dir=dir_destino, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(conteudo)
        nome_tmp = tmp.name
    os.replace(nome_tmp, destino)  # Operação atômica no SO


def gerar_html(solo: int, temp: float, umid: float) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgroNexus - Monitoramento Inteligente</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #f0f4f1;
            color: #2c3e50;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        nav {{
            background-color: #1e3f20;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        }}

        .logo {{
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .logo span {{ color: #2ecc71; }}

        .nav-status {{
            font-size: 13px;
            color: #a8d5b5;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .dot-live {{
            width: 8px; height: 8px;
            background: #2ecc71;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50%        {{ opacity: 0.5; transform: scale(1.3); }}
        }}

        .main-container {{
            max-width: 1000px;
            width: 100%;
            margin: 40px auto;
            padding: 0 20px;
            flex: 1;
        }}

        .welcome-section {{
            margin-bottom: 30px;
        }}

        .welcome-section h1 {{
            font-size: 26px;
            color: #1a331e;
            margin-bottom: 5px;
        }}

        .welcome-section p {{
            color: #7f8c8d;
            font-size: 14px;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }}

        .card {{
            background: #ffffff;
            border-radius: 16px;
            padding: 30px 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.04);
            border: 1px solid rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 6px; height: 100%;
        }}

        .card.solo::before {{ background-color: #6d4c41; }}
        .card.temp::before {{ background-color: #e67e22; }}
        .card.ar::before   {{ background-color: #2980b9; }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .card-icon {{
            font-size: 22px;
            width: 44px; height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .card.solo .card-icon {{ background-color: #f3ede8; }}
        .card.temp .card-icon {{ background-color: #fef3e8; }}
        .card.ar   .card-icon {{ background-color: #e8f4fc; }}

        .card-title {{
            font-size: 13px;
            text-transform: uppercase;
            color: #95a5a6;
            font-weight: 700;
            letter-spacing: 0.6px;
        }}

        .card-value {{
            font-size: 52px;
            font-weight: 700;
            color: #1a252f;
            line-height: 1;
        }}

        .card-unit {{
            font-size: 22px;
            color: #95a5a6;
            font-weight: 400;
            margin-left: 3px;
        }}

        /* Barra de progresso visual abaixo do valor */
        .progress-bar-bg {{
            margin-top: 18px;
            background: #ecf0f1;
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
        }}

        .progress-bar-fill {{
            height: 100%;
            border-radius: 6px;
            transition: width 0.6s ease;
        }}

        .card.solo .progress-bar-fill {{ background: #6d4c41; }}
        .card.temp .progress-bar-fill {{ background: #e67e22; }}
        .card.ar   .progress-bar-fill {{ background: #2980b9; }}

        footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #bdc3c7;
            background-color: #ffffff;
            border-top: 1px solid rgba(0,0,0,0.05);
            margin-top: auto;
        }}
    </style>
</head>
<body>

    <nav>
        <div class="logo">🌱 Agro<span>Nexus</span></div>
        <div class="nav-status">
            <div class="dot-live"></div>
            Monitoramento ao vivo — USB
        </div>
    </nav>

    <div class="main-container">
        <div class="welcome-section">
            <h1>Monitoramento em Tempo Real</h1>
            <p>Dados recebidos diretamente do Arduino Mega via conexão USB</p>
        </div>

        <div class="dashboard-grid">

            <div class="card solo">
                <div class="card-header">
                    <div class="card-icon">🌱</div>
                    <div class="card-title">Umidade do Solo</div>
                </div>
                <div class="card-value">{solo}<span class="card-unit">%</span></div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{solo}%"></div>
                </div>
            </div>

            <div class="card temp">
                <div class="card-header">
                    <div class="card-icon">🌡️</div>
                    <div class="card-title">Temperatura do Ar</div>
                </div>
                <div class="card-value">{temp}<span class="card-unit">°C</span></div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{min(temp, 50) / 50 * 100:.0f}%"></div>
                </div>
            </div>

            <div class="card ar">
                <div class="card-header">
                    <div class="card-icon">💧</div>
                    <div class="card-title">Umidade do Ar</div>
                </div>
                <div class="card-value">{umid}<span class="card-unit">%</span></div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{umid}%"></div>
                </div>
            </div>

        </div>
    </div>

    <footer>
        AgroNexus &copy; 2026 — Atualiza a cada 2 segundos via Python Bridge
    </footer>

</body>
</html>"""


# ------------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------------
try:
    print("\n📡 Aguardando dados do Arduino... (Ctrl+C para encerrar)\n")
    while True:
        if arduino.in_waiting > 0:
            try:
                linha = arduino.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue  # Ignora lixo de caracteres na abertura da porta

            if linha.startswith('{') and linha.endswith('}'):
                try:
                    dados = json.loads(linha)

                    solo = int(dados.get("solo", 0))
                    temp = float(dados.get("temp", 0.0))
                    umid = float(dados.get("umid", 0.0))

                    print(f"[AgroNexus] Solo: {solo}% | Temp: {temp}°C | Ar: {umid}%")

                    html = gerar_html(solo, temp, umid)
                    salvar_html_atomico(html, ARQUIVO_HTML)   # ✅ Escrita atômica

                except json.JSONDecodeError:
                    pass  # Linha incompleta ou corrompida — ignora silenciosamente
                except IOError as e:
                    print(f"[ERRO] Não foi possível salvar o HTML: {e}")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[AgroNexus] Monitoramento encerrado pelo usuário.")
    arduino.close()
