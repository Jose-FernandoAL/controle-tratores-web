# Aqui inicia o CloudFlared pra gerar o link aleatoirio para uso externo






import re
import socket
import subprocess
import sys
import time

HOST = "127.0.0.1"
PORTA = 5000
URL_LOCAL = f"http://{HOST}:{PORTA}"


def porta_esta_disponivel() -> bool:
    """Verifica se o servidor Flask já está aceitando conexões."""
    try:
        # Tenta abrir uma conexão TCP com o Flask na porta 5000.
        # Se existir resposta, significa que o servidor já está no ar.
        with socket.create_connection((HOST, PORTA), timeout=1):
            return True
    except OSError:
        # Se houver erro, o Flask ainda não está pronto.
        return False


def esperar_flask(timeout: int = 20) -> bool:
    """Espera o Flask ficar disponível antes de iniciar o túnel."""
    inicio = time.time()

    # Faz tentativas repetidas durante o tempo limite.
    while time.time() - inicio < timeout:
        if porta_esta_disponivel():
            return True

        time.sleep(0.5)

    return False


def encerrar_processo(processo: subprocess.Popen | None) -> None:
    """Encerra um processo somente se ele ainda estiver executando."""
    # Se o processo não existe ou já terminou, não faz nada.
    if processo is None or processo.poll() is not None:
        return

    # Tenta encerrar de forma limpa.
    processo.terminate()

    try:
        processo.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # Se não responder, força a parada.
        processo.kill()


def main() -> None:
    # Guarda referências aos processos que serão iniciados.
    flask = None
    cloudflared = None

    try:
        print("Iniciando o servidor Flask...")

        # Inicia o arquivo app.py usando o mesmo interpretador Python.
        flask = subprocess.Popen(
            [sys.executable, "app.py"]
        )

        # Aguarda até que o Flask realmente esteja respondendo.
        if not esperar_flask():
            raise RuntimeError(
                f"O Flask não respondeu em {URL_LOCAL} dentro do tempo esperado."
            )

        print(f"Flask disponível em {URL_LOCAL}")
        print("Iniciando o Cloudflared...")

        # Inicia o Cloudflared com um túnel para a URL local do Flask.
        cloudflared = subprocess.Popen(
            [
                "cloudflared",
                "tunnel",
                "--url",
                URL_LOCAL,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Se a saída do Cloudflared não puder ser lida, aborta.
        if cloudflared.stdout is None:
            raise RuntimeError("Não foi possível ler a saída do Cloudflared.")

        # lê linha por linha a resposta do processo.
        # Na saída, o Cloudflared mostra o link externo quando o túnel for criado.
        for linha in cloudflared.stdout:
            print(linha, end="")

            # Tenta extrair uma URL do formato trycloudflare.
            resultado = re.search(
                r"https://[a-zA-Z0-9-]+\.trycloudflare\.com",
                linha,
            )

            if resultado:
                print("\n" + "=" * 60)
                print(f"LINK EXTERNO: {resultado.group(0)}")
                print("=" * 60 + "\n")

        # Espera o Cloudflared terminar sua execução.
        codigo_saida = cloudflared.wait()

        # Se o retorno não for 0, o túnel terminou com erro.
        if codigo_saida != 0:
            raise RuntimeError(
                f"O Cloudflared foi encerrado com o código {codigo_saida}."
            )

    except KeyboardInterrupt:
        # Se o usuário apertar Ctrl+C, trata como parada normal.
        print("\nEncerrando o sistema...")

    except FileNotFoundError:
        # Se o cloudflared não estiver instalado ou não estiver no PATH.
        print(
            "\nO comando 'cloudflared' não foi encontrado. "
            "Confirme se ele está instalado e disponível no PATH."
        )

    except RuntimeError as erro:
        # Mostra qualquer erro de inicialização do fluxo.
        print(f"\nErro: {erro}")

    finally:
        # Mesmo com erro, tenta fechar os processos iniciados.
        encerrar_processo(cloudflared)
        encerrar_processo(flask)
        print("Flask e Cloudflared encerrados.")


if __name__ == "__main__":
    # Permite rodar o script diretamente como programa principal.
    main()