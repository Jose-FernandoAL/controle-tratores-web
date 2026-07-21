import json  # Importa a biblioteca para trabalhar com JSON
import os    # Importa a biblioteca para manipular caminhos e arquivos

# Define a pasta do arquivo atual como base para montar o caminho do JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho completo do arquivo pedidos.json dentro da pasta do projeto
ARQUIVO_PEDIDOS = os.path.join(BASE_DIR, "pedidos.json")


def carregar_pedidos():
    """
    Carrega os pedidos salvos no arquivo JSON.
    Se o arquivo não existir, retorna uma lista vazia.
    """

    # Se o arquivo ainda não existir, retorna lista vazia
    if not os.path.exists(ARQUIVO_PEDIDOS):
        return []

    try:
        # Abre o arquivo em modo de leitura com codificação UTF-8
        with open(ARQUIVO_PEDIDOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)  # Converte o conteúdo JSON em Python

            # Se os dados forem uma lista, retorna a lista
            if isinstance(dados, list):
                return dados

            # Se o conteúdo não for uma lista, retorna lista vazia
            return []

    except json.JSONDecodeError:
        # Caso o arquivo esteja vazio ou com JSON inválido
        print("Erro: o arquivo pedidos.json está vazio ou corrompido.")
        return []

    except PermissionError:
        # Caso o sistema não permita leitura do arquivo
        print("Erro: sem permissão para ler o arquivo pedidos.json.")
        return []


def salvar_pedidos(pedidos):
    """
    Salva a lista de pedidos no arquivo JSON.
    """

    try:
        # Abre o arquivo em modo de escrita
        with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as arquivo:
            # Escreve a lista no arquivo JSON com indentação legível
            json.dump(pedidos, arquivo, ensure_ascii=False, indent=4)

    except PermissionError:
        # Caso o sistema não permita gravação no arquivo
        print("Erro: sem permissão para salvar o arquivo pedidos.json.")


def adicionar_pedido(pedido):
    """
    Carrega os pedidos existentes,
    adiciona um novo pedido
    e salva tudo novamente.
    """

    # Busca todos os pedidos já armazenados
    pedidos = carregar_pedidos()

    # Adiciona o novo pedido à lista
    pedidos.append(pedido)

    # Salva a lista atualizada no JSON
    salvar_pedidos(pedidos)

    # Retorna a lista completa com o novo pedido
    return pedidos


def buscar_pedido_por_id(id_pedido):
    """
    Busca um pedido pelo ID.
    Retorna o pedido se encontrar.
    Retorna None se não encontrar.
    """

    # Carrega os pedidos existentes
    pedidos = carregar_pedidos()

    # Percorre cada pedido e compara o campo "id"
    for pedido in pedidos:
        if pedido.get("id") == id_pedido:
            return pedido

    # Se não encontrar, retorna None
    return None


def atualizar_pedido(id_pedido, dados_atualizados):
    """
    Atualiza um pedido existente pelo ID.
    """

    # Carrega a lista de pedidos
    pedidos = carregar_pedidos()

    # Percorre os pedidos para encontrar o ID correspondente
    for indice, pedido in enumerate(pedidos):
        if pedido.get("id") == id_pedido:
            # Atualiza os campos recebidos
            pedidos[indice].update(dados_atualizados)

            # Salva a lista atualizada
            salvar_pedidos(pedidos)

            # Retorna True para indicar sucesso
            return True

    # Se não encontrar o pedido, retorna False
    return False


def alterar_status_pedido(id_pedido, novo_status):
    """
    Altera apenas o status de um pedido.
    """

    # Chama atualizar_pedido com um dicionário contendo apenas o status
    return atualizar_pedido(id_pedido, {"status": novo_status})


def remover_pedido(id_pedido):
    """
    Remove um pedido pelo ID.
    """

    # Carrega os pedidos atuais
    pedidos = carregar_pedidos()

    # Cria uma nova lista sem o pedido removido
    nova_lista = []

    # Variável para controlar se o pedido foi removido
    removido = False

    # Percorre todos os pedidos
    for pedido in pedidos:
        if pedido.get("id") == id_pedido:
            # Se o ID bater, marca como removido
            removido = True
        else:
            # Mantém os demais pedidos na nova lista
            nova_lista.append(pedido)

    # Se algum pedido foi removido, salva a lista atualizada
    if removido:
        salvar_pedidos(nova_lista)

    # Retorna True se removeu, False se não encontrou
    return removido