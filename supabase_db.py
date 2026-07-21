import os  # Importa o módulo os para ler variáveis de ambiente
from dotenv import load_dotenv  # Importa a função para carregar o .env
from supabase import create_client  # Importa a função que cria o cliente do Supabase

# Carrega as variáveis definidas no arquivo .env
load_dotenv()

# Lê as credenciais do Supabase a partir do ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Verifica se as variáveis foram encontradas
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ou SUPABASE_KEY não foram encontrados no .env")

# Cria o cliente do Supabase usando a URL e a chave
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def listar_pedidos():
    """
    Busca todos os pedidos no Supabase.
    Concluídos ficam por último.
    """

    # Faz a consulta na tabela "pedidos"
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .execute()
    )

    # Pega os dados retornados
    pedidos = resposta.data or []

    # Função usada para ordenar a lista
    def ordenar(pedido):
        status = pedido.get("status")

        # Define a ordem de prioridade do status
        if status == "Concluído":
            grupo = 3
        elif status == "Pendente":
            grupo = 2
        else:
            grupo = 1

        # Define a data e a hora para ordenação
        data = pedido.get("data_marcada") or "9999-12-31"
        hora = pedido.get("hora_inicio") or "23:59:59"

        # Retorna a chave de ordenação
        return grupo, data, hora

    # Ordena a lista com a função acima
    return sorted(pedidos, key=ordenar)


def buscar_pedido_por_id(id_pedido):
    """
    Busca um pedido específico pelo ID.
    """

    # Consulta um único pedido com o ID informado
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("id", id_pedido)
        .single()
        .execute()
    )

    # Retorna o pedido encontrado
    return resposta.data


def adicionar_pedido(pedido):
    """
    Insere um novo pedido no Supabase.
    """

    # Monta um dicionário com os campos que devem ser salvos
    dados = {
        "nome_agricultor": pedido["nome_agricultor"],
        "telefone": pedido["telefone"],
        "servico": pedido["servico"],
        "local": pedido["local"],
        "duracao_horas": pedido.get("duracao_horas"),
        "tempo_indefinido": pedido.get("tempo_indefinido", False),
        "data_marcada": pedido.get("data_marcada"),
        "hora_inicio": pedido.get("hora_inicio"),
        "hora_fim": pedido.get("hora_fim"),
        "status": pedido.get("status", "Pendente"),
        "observacoes": pedido.get("observacoes", "")
    }

    # Insere os dados na tabela "pedidos"
    resposta = (
        supabase
        .table("pedidos")
        .insert(dados)
        .execute()
    )

    # Retorna os dados inseridos
    return resposta.data


def atualizar_pedido(id_pedido, dados_atualizados):
    """
    Atualiza um pedido pelo ID.
    """

    # Atualiza os campos informados no pedido com o ID correspondente
    resposta = (
        supabase
        .table("pedidos")
        .update(dados_atualizados)
        .eq("id", id_pedido)
        .execute()
    )

    # Retorna os dados atualizados
    return resposta.data


def alterar_status_pedido(id_pedido, novo_status):
    """
    Altera apenas o status do pedido.
    """

    # Chama atualizar_pedido com um dicionário contendo apenas o status
    return atualizar_pedido(
        id_pedido,
        {"status": novo_status}
    )


def remover_pedido(id_pedido):
    """
    Remove um pedido pelo ID.
    """

    # Remove o pedido com o ID informado
    resposta = (
        supabase
        .table("pedidos")
        .delete()
        .eq("id", id_pedido)
        .execute()
    )

    # Retorna os dados removidos
    return resposta.data