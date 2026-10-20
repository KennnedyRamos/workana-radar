"""Radar Workana: busca vagas novas, pontua pelas suas skills e manda as que compensam no Telegram."""
import html
import json
import os
import re
import sys
from pathlib import Path

from curl_cffi import requests

# ===================== AJUSTE AQUI =====================
SKILLS = ["python", "fastapi", "node", "node.js", "nodejs", "javascript", "typescript", "flutter", "dart",
          "postgresql", "postgres", "sql", "supabase", "api", "rest", "webhook", "chatbot", "bot",
          "whatsapp", "telegram", "web scraping", "scraping", "automação", "html", "css"]
MIN_USD = 50      # teto do orçamento abaixo disso = ignora
MIN_SCORE = 60    # nota mínima para te avisar (0-100+)
QUICK = ["ajuste", "ajustes", "correção", "corrigir", "bug", "bugs", "erro", "erros", "simples", "script",
         "landing page", "configurar", "atualizar", "atualização", "pequena alteração"]
LONG = ["do zero", "sistema completo", "plataforma completa", "marketplace", "longo prazo", "mensal",
        "equipe", "clt", "tempo integral", "manutenção contínua"]
RED_FLAGS = ["equity", "sócio", "sócios", "porcentagem", "voluntário", "voluntária", "sem remuneração",
             "não remunerado", "teste gratuito", "permuta"]
# =======================================================

URL = "https://www.workana.com/jobs?category=it-programming&language=pt&page={}"
SEEN = Path(__file__).with_name("seen.json")


def clean(raw):
    raw = re.sub(r"<br\s*/?>", "\n", raw or "")
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


def title_of(job):
    # o texto do link vem truncado; o título completo fica no atributo title do <span>
    m = re.search(r'<span title="([^"]+)"', job["title"])
    return html.unescape(m.group(1)) if m else clean(job["title"])


def has(term, text):
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def usd_range(budget):
    nums = [int(n.replace(".", "")) for n in re.findall(r"\d[\d.]*", budget or "")]
    if not nums:
        return 0, 0
    if budget.lower().startswith(("menos", "less")):
        nums = [0] + nums
    lo, hi = nums[0], nums[-1]
    if "R$" in budget:
        lo, hi = lo / 5.5, hi / 5.5  # shortcut: câmbio fixo, atualize se o dólar mudar muito
    return lo, hi


def score(job):
    """Devolve (pontos, motivos) ou None se a vaga não serve."""
    title = title_of(job)
    text = f"{title}\n{clean(job['description'])}".lower()
    if job.get("isHourly") or any(has(f, text) for f in RED_FLAGS):  # por hora = longo e sem valor fechado
        return None
    lo, hi = usd_range(job["budget"])
    if hi < MIN_USD:
        return None
    tags = [s["anchorText"].lower() for s in job.get("skills") or []]
    my_tags = [t for t in tags if any(has(s, t) for s in SKILLS)]
    in_title = [s for s in SKILLS if has(s, title.lower())]
    if not my_tags and not in_title:
        return None

    pts, why = 0, []
    fit = round(30 * len(my_tags) / max(len(tags), 1))
    pts += fit + (10 if in_title else 0)
    why.append(f"skills {', '.join(my_tags or in_title)}")

    m = re.search(r"\d+", job.get("totalBids") or "")
    bids = int(m.group()) if m else 0
    pts += 25 if bids <= 5 else 18 if bids <= 10 else 10 if bids <= 20 else 0 if bids <= 40 else -15

    size = re.search(r"tamanho do projeto:\s*(\w+)", text)
    size = size.group(1) if size else ""
    if size.startswith("peque"):
        pts += 15; why.append("projeto pequeno")
    elif size.startswith("médio"):
        pts += 5
    elif size.startswith("grande"):
        pts -= 15

    mid = (lo + hi) / 2
    pts += 15 if 100 <= mid <= 500 else 10 if 500 < mid <= 1500 else 8 if mid >= 50 else 0

    if any(has(k, text) for k in QUICK):
        pts += 10; why.append("parece rápido")
    if any(has(k, text) for k in LONG):
        pts -= 15; why.append("⚠️ parece longo")

    if job.get("hasVerifiedPaymentMethod"):
        pts += 10; why.append("pagamento verificado")
    if float((job.get("rating") or {}).get("value") or 0) >= 4.5:
        pts += 5; why.append("cliente bem avaliado")

    posted = (job.get("postedDate") or "").lower()
    if "minuto" in posted or "agora" in posted:
        pts += 10; why.append("recém-publicado")
    elif re.search(r"quase uma hora|há [123] hora", posted):
        pts += 5
    return pts, why, bids


def message(job, pts, why, bids):
    e = html.escape
    desc = clean(job["description"]).split("\n\nCategoria:")[0]
    return (f"🎯 <b>{pts} pts</b> · {e(title_of(job))}\n"
            f"💰 {e(job['budget'])} · 📨 {bids} propostas · 🕒 {e(job.get('postedDate') or '')}\n"
            f"✅ {e(' · '.join(why))}\n\n"
            f"{e(desc[:350])}{'…' if len(desc) > 350 else ''}\n\n"
            f"https://www.workana.com/job/{job['slug']}")


def send(text):
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        print(text, "\n")
        return
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", timeout=30,
                      json={"chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})
    r.raise_for_status()


def main():
    if sys.stdout:  # pythonw (Agendador de Tarefas) não tem console
        sys.stdout.reconfigure(encoding="utf-8")
    env = Path(__file__).with_name(".env")
    if env.exists():  # no PC o token vem do .env
        for line in env.read_text(encoding="utf-8-sig").splitlines():
            k, _, v = line.partition("=")
            if v.strip() and not k.startswith("#"):
                os.environ.setdefault(k.strip(), v.strip())
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else []
    known = set(seen)
    hits = []
    for page in (1, 2):
        r = requests.get(URL.format(page), impersonate="chrome", timeout=30,
                         headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
        r.raise_for_status()  # 403 = Cloudflare bloqueou; o GitHub te manda e-mail da falha
        for job in r.json()["results"]["results"]:
            if job["slug"] in known:
                continue
            known.add(job["slug"]); seen.append(job["slug"])
            s = score(job)
            if s and s[0] >= MIN_SCORE:
                hits.append((s[0], message(job, *s)))
    for _, text in sorted(hits, reverse=True):
        send(text)
    print(f"{len(hits)} oportunidade(s) enviada(s)")
    if os.environ.get("TELEGRAM_TOKEN"):  # teste local sem token não marca como visto
        SEEN.write_text(json.dumps(seen[-1000:]))


if __name__ == "__main__":
    erro = Path(__file__).with_name("erro.txt")
    try:
        main()
        erro.unlink(missing_ok=True)
    except Exception as e:
        if not erro.exists():  # avisa uma vez só, até voltar a funcionar
            msg = re.sub(r"bot[^/\s]+/", "bot***/", str(e))[:300]  # não vaza o token
            send(f"⚠️ Radar Workana parou: {html.escape(msg)}")
            erro.write_text(msg, encoding="utf-8")
        raise
