# workana-radar

A cada 10 min busca vagas novas de TI no Workana, dá uma nota (stack, nº de propostas, tamanho, orçamento,
cliente verificado, quão recente) e manda no Telegram só as que passam de `MIN_SCORE`. Custo: zero.

## 1. Bot do Telegram
1. No Telegram, fale com **@BotFather** → `/newbot` → copie o token.
2. Mande qualquer mensagem pro seu bot novo.
3. Abra `https://api.telegram.org/bot<TOKEN>/getUpdates` e copie o número em `"chat":{"id":...}`.

## 2. Testar no PC
```powershell
pip install -r requirements.txt
python test_radar.py
python radar.py                       # sem token: só imprime na tela
$env:TELEGRAM_TOKEN="..."; $env:TELEGRAM_CHAT_ID="..."; python radar.py   # manda no Telegram
```

## 3. Rodar 24h grátis no GitHub Actions
1. Crie um repositório **público** `workana-radar` no GitHub (público = minutos ilimitados; privado estoura os
   2.000 min/mês grátis rodando a cada 10 min). Os tokens ficam nos Secrets, não no código.
2. `git init && git add . && git commit -m "radar" && git branch -M main && git remote add origin https://github.com/<voce>/workana-radar.git && git push -u origin main`
3. Settings → Secrets and variables → Actions → crie `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID`.
4. Aba Actions → `radar` → **Run workflow** para testar na hora.

## Ajustar
Tudo no topo do `radar.py`: `SKILLS` (sua stack), `MIN_SCORE`, `MIN_USD` e as listas de palavras.
