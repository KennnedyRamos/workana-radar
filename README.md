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

## 3. Rodar sozinho no PC (Agendador de Tarefas)
Coloque `TELEGRAM_TOKEN=` e `TELEGRAM_CHAT_ID=` no `.env` (não vai pro Git) e registre a tarefa `workana-radar`
(roda `pythonw radar.py` a cada 10 min, sem janela). Só funciona com o PC ligado.
Se der erro (ex.: Cloudflare bloqueou), chega um único "⚠️ Radar Workana parou" no Telegram.

## 4. (Opcional) Rodar 24h no GitHub Actions
Precisa de conta GitHub sem bloqueio de cobrança. Secrets `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID` já criados;
reative com `gh workflow enable radar.yml` e **desative a tarefa do PC** pra não receber vaga duplicada.

## Ajustar
Tudo no topo do `radar.py`: `SKILLS` (sua stack), `MIN_SCORE`, `MIN_USD` e as listas de palavras.
