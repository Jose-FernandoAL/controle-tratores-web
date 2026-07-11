import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PEDIDOS = os.path.join(BASE_DIR, "pedidos.json")


def carregar_pedidos():
    """
    Carrega os pedidos salvos no arquivo JSON.
    Se o arquivo não existir, retorna uma lista vazia.
    """

    if not os.path.exists(ARQUIVO_PEDIDOS):
        return []

    try:
        with open(ARQUIVO_PEDIDOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

            return []

    except json.JSONDecodeError:
        print("Erro: o arquivo pedidos.json está vazio ou corrompido.")
        return []

    except PermissionError:
        print("Erro: sem permissão para ler o arquivo pedidos.json.")
        return []


def salvar_pedidos(pedidos):
    """
    Salva a lista de pedidos no arquivo JSON.
    """

    try:
        with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as arquivo:
            json.dump(pedidos, arquivo, ensure_ascii=False, indent=4)

    except PermissionError:
        print("Erro: sem permissão para salvar o arquivo pedidos.json.")


def adicionar_pedido(pedido):
    """
    Carrega os pedidos existentes,
    adiciona um novo pedido
    e salva tudo novamente.
    """

    pedidos = carregar_pedidos()
    pedidos.append(pedido)
    salvar_pedidos(pedidos)

    return pedidos


def buscar_pedido_por_id(id_pedido):
    """
    Busca um pedido pelo ID.
    Retorna o pedido se encontrar.
    Retorna None se não encontrar.
    """

    pedidos = carregar_pedidos()

    for pedido in pedidos:
        if pedido.get("id") == id_pedido:
            return pedido

    return None


def atualizar_pedido(id_pedido, dados_atualizados):
    """
    Atualiza um pedido existente pelo ID.
    """

    pedidos = carregar_pedidos()

    for indice, pedido in enumerate(pedidos):
        if pedido.get("id") == id_pedido:
            pedidos[indice].update(dados_atualizados)
            salvar_pedidos(pedidos)
            return True

    return False


def alterar_status_pedido(id_pedido, novo_status):
    """
    Altera apenas o status de um pedido.
    """

    return atualizar_pedido(id_pedido, {"status": novo_status})


def remover_pedido(id_pedido):
    """
    Remove um pedido pelo ID.
    """

    pedidos = carregar_pedidos()
    nova_lista = []

    removido = False

    for pedido in pedidos:
        if pedido.get("id") == id_pedido:
            removido = True
        else:
            nova_lista.append(pedido)

    if removido:
        salvar_pedidos(nova_lista)

    return removido
