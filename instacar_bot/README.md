# Bot Instacar — Selección de Lotes

Bot que monitorea [Instacar](https://www.instacar.mx) automáticamente y te notifica por **Telegram** cuando aparecen lotes con bajo kilometraje y buen precio.

---

## Instalación

```bash
cd instacar_bot

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar navegador Chromium para Playwright
playwright install chromium

# 3. Copiar y configurar variables de entorno
cp .env.example .env
nano .env   # o usa tu editor favorito
```

---

## Configurar Telegram

1. Abre Telegram y busca **@BotFather**
2. Escribe `/newbot` → elige nombre → copia el **TOKEN**
3. Para obtener tu **CHAT_ID**: busca **@userinfobot** → escribe cualquier mensaje → te responde con tu ID
4. Pega ambos en el archivo `.env`

---

## Uso

```bash
# Probar configuración (un solo ciclo, envía mensaje de prueba)
python main.py --test

# Ver estadísticas de lotes ya vistos
python main.py --stats

# Iniciar el bot en bucle continuo
python main.py
```

---

## Criterios de puntuación (0–100)

| Factor          | Puntos |
|-----------------|--------|
| < 20,000 km     | +25    |
| < 40,000 km     | +18    |
| < 60,000 km     | +10    |
| Año reciente (≤2 años) | +20 |
| Marca de alto valor (Toyota, Honda…) | +15 |
| Precio bajo vs. máximo configurado | +10 |

Solo se notifican lotes con puntuación ≥ `MIN_SCORE` (default: 50).

---

## Ajustar selectores CSS

Si Instacar actualiza su sitio y el bot deja de encontrar lotes, edita las constantes `SEL_*` al inicio de `scraper.py`. Para depurar visualmente, pon `HEADLESS=false` en `.env`.

---

## Ejecutar como servicio (opcional)

```bash
# Con systemd (Linux)
sudo nano /etc/systemd/system/instacar-bot.service
```

```ini
[Unit]
Description=Instacar Bot
After=network.target

[Service]
WorkingDirectory=/ruta/al/instacar_bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable instacar-bot
sudo systemctl start instacar-bot
```
