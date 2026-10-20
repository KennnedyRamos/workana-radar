from radar import score, title_of, usd_range

assert usd_range("USD 500 - 1.000") == (500, 1000)
assert usd_range("Menos de USD 50") == (0, 50)
assert usd_range("Mais de USD 3.000") == (3000, 3000)
assert usd_range("") == (0, 0)

job = {
    "slug": "x", "title": '<a href="/job/x"><span title="Corrigir bug em API Node.js">Corrigir bug...</span></a>',
    "description": "Preciso corrigir um erro simples.<br /><br />Tamanho do projeto: <strong>Pequeño</strong>",
    "budget": "USD 100 - 250", "totalBids": "Propostas: 3", "postedDate": "há 5 minutos",
    "skills": [{"anchorText": "Node.js"}, {"anchorText": "API"}], "isHourly": False,
    "hasVerifiedPaymentMethod": True, "rating": {"value": "5.00"},
}
assert title_of(job) == "Corrigir bug em API Node.js"
pts, why, bids = score(job)
assert bids == 3 and pts >= 100 and "projeto pequeno" in why, (pts, why)

assert score({**job, "budget": "Menos de USD 30"}) is None                        # paga pouco
assert score({**job, "description": "Busco sócio com equity"}) is None           # red flag
assert score({**job, "title": "Logo", "skills": [{"anchorText": "Photoshop"}]}) is None  # fora da stack
assert score({**job, "isHourly": True}) is None                                   # por hora
assert score({**job, "totalBids": "Propostas: 80"})[0] < pts                      # concorrência alta
print("ok")
