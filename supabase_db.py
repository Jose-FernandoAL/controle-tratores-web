import os
from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ou SUPABASE_KEY não foram encontrados no .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def listar_pedidos():
    """
    Busca todos os pedidos no Supabase.
    Concluídos ficam por último.
    """

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .execute()
    )

    pedidos = resposta.data or []

    def ordenar(pedido):
        status = pedido.get("status")

        if status == "Concluído":
            grupo = 3
        elif status == "Pendente":
            grupo = 2
        else:
            grupo = 1

        data = pedido.get("data_marcada") or "9999-12-31"
        hora = pedido.get("hora_inicio") or "23:59:59"

        return grupo, data, hora

    return sorted(pedidos, key=ordenar)


def buscar_pedido_por_id(id_pedido):
    """
    Busca um pedido específico pelo ID.
    """

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("id", id_pedido)
        .single()
        .execute()
    )

    return resposta.data


def adicionar_pedido(pedido):
    """
    Insere um novo pedido no Supabase.
    """

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

    resposta = (
        supabase
        .table("pedidos")
        .insert(dados)
        .execute()
    )

    return resposta.data


def atualizar_pedido(id_pedido, dados_atualizados):
    """
    Atualiza um pedido pelo ID.
    """

    resposta = (
        supabase
        .table("pedidos")
        .update(dados_atualizados)
        .eq("id", id_pedido)
        .execute()
    )

    return resposta.data


def alterar_status_pedido(id_pedido, novo_status):
    """
    Altera apenas o status do pedido.
    """

    return atualizar_pedido(
        id_pedido,
        {"status": novo_status}
    )


def remover_pedido(id_pedido):
    """
    Remove um pedido pelo ID.
    """

    resposta = (
        supabase
        .table("pedidos")
        .delete()
        .eq("id", id_pedido)
        .execute()
    )

    return resposta.data