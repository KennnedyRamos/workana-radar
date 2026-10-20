"""Roda a cada 30 min no PC: quando a conta do GitHub destravar, liga o radar lá e desliga o do PC."""
import json
import subprocess
import time

import radar

GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = ["-R", "KennnedyRamos/workana-radar"]


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout


def bye():
    sh("schtasks", "/delete", "/tn", "workana-radar-github", "/f")


ok = False
sh(GH, "workflow", "enable", "radar.yml", *REPO)
try:
    run_id = sh(GH, "workflow", "run", "radar.yml", *REPO).strip().rsplit("/", 1)[-1]
    for _ in range(30):
        time.sleep(10)
        r = json.loads(sh(GH, "run", "view", run_id, "--json", "status,conclusion,jobs", *REPO))
        if r["status"] == "completed":
            break
    radar.load_env()
    if r["status"] != "completed":
        print("demorou demais, tenta de novo na próxima")
    elif r["conclusion"] == "success":
        ok = True
        sh("schtasks", "/change", "/tn", "workana-radar", "/disable")
        radar.send("✅ GitHub desbloqueado! O radar agora roda 24h lá, sem precisar do PC.")
        bye()
        print("github ok: radar do PC desligado")
    elif any(j["steps"] for j in r["jobs"]):  # rodou e falhou (ex.: Workana bloqueou o GitHub)
        radar.send("⚠️ GitHub desbloqueado, mas o radar falhou lá. Ele continua rodando no seu PC.")
        bye()
        print("github falhou: segue no PC")
    else:  # job nem começou = conta ainda bloqueada
        print("conta ainda bloqueada")
finally:
    if not ok:
        sh(GH, "workflow", "disable", "radar.yml", *REPO)
