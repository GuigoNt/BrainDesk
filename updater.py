import requests
import subprocess
import sys
import os
import zipfile

REPO = "GuigoNt/BrainDesk"
VERSAO_ATUAL = "v1.0.0"

def verificar_update():
    try:
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return

        data = response.json()
        versao_online = data["tag_name"]

        if versao_online != VERSAO_ATUAL:
            print("🔄 Atualização encontrada!")

            download_url = data["assets"][0]["browser_download_url"]
            baixar_e_atualizar(download_url)

    except Exception as e:
        print("Erro ao verificar update:", e)

def baixar_e_atualizar(url):
    try:
        print("⬇️ Baixando atualização...")

        r = requests.get(url)
        with open("update.zip", "wb") as f:
            f.write(r.content)

        print("✅ Download concluído")

        with zipfile.ZipFile("update.zip", 'r') as zip_ref:
            zip_ref.extractall("nova_versao")

        executar_updater()

    except Exception as e:
        print("Erro ao baixar update:", e)

def executar_updater():
    try:
        bat = """
        @echo off
        timeout /t 2 > nul
        xcopy nova_versao\\* . /E /H /C /I /Y
        start BrainDesk.exe
        exit
        """

        with open("update.bat", "w") as f:
            f.write(bat)

        subprocess.Popen("update.bat", shell=True)
        sys.exit()

    except Exception as e:
        print("Erro no updater:", e)