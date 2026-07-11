from datetime import datetime


SERVICOS_VALIDOS = [
    "Arar terra",
    "Puxar carga",
    "Moer silagem"
]


STATUS_VALIDOS = [
    "Pendente",
    "Agendado",
    "Em andamento",
    "Concluído",
    "Cancelado"
]


def gerar_id(pedidos_existentes):
    """
    Gera um ID simples baseado no maior ID existente.
    """
    if not pedidos_existentes:
        return 1

    maior_id = max(pedido["id"] for pedido in pedidos_existentes)
    return maior_id + 1


def validar_texto_obrigatorio(valor, nome_campo):
    """
    Verifica se um campo obrigatório foi preenchido.
    """
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"O campo '{nome_campo}' é obrigatório.")


def validar_servico(servico):
    """
    Verifica se o serviço escolhido é válido.
    """
    if servico not in SERVICOS_VALIDOS:
        raise ValueError(
            f"Serviço inválido. Escolha entre: {', '.join(SERVICOS_VALIDOS)}"
        )


def validar_duracao(duracao_horas, tempo_indefinido):
    """
    Regra:
    - Se tempo indefinido for True, não precisa duração.
    - Se tempo indefinido for False, duração é obrigatória e deve ser maior que zero.
    """
    if tempo_indefinido:
        return

    if duracao_horas is None:
        raise ValueError("A duração é obrigatória para agendar o pedido.")

    if duracao_horas <= 0:
        raise ValueError("A duração precisa ser maior que zero.")


def definir_status(data_marcada, hora_inicio, hora_fim, tempo_indefinido):
    """
    Define o status inicial do pedido.

    Se o tempo for indefinido, o pedido fica pendente.
    Se já tiver data e horário, fica agendado.
    Caso contrário, fica pendente.
    """
    if tempo_indefinido:
        return "Pendente"

    if data_marcada and hora_inicio and hora_fim:
        return "Agendado"

    return "Pendente"


def criar_pedido(
    pedidos_existentes,
    nome_agricultor,
    telefone,
    servico,
    local,
    duracao_horas=None,
    tempo_indefinido=False,
    data_marcada=None,
    hora_inicio=None,
    hora_fim=None,
    observacoes=""
):
    """
    Cria um pedido validado e organizado.
    """

    validar_texto_obrigatorio(nome_agricultor, "nome do agricultor")
    validar_texto_obrigatorio(telefone, "telefone")
    validar_texto_obrigatorio(servico, "serviço")
    validar_texto_obrigatorio(local, "local/sítio")

    validar_servico(servico)
    validar_duracao(duracao_horas, tempo_indefinido)

    status = definir_status(
        data_marcada=data_marcada,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        tempo_indefinido=tempo_indefinido
    )

    pedido = {
        "id": gerar_id(pedidos_existentes),
        "nome_agricultor": nome_agricultor.strip(),
        "telefone": telefone.strip(),
        "servico": servico,
        "local": local.strip(),
        "duracao_horas": None if tempo_indefinido else duracao_horas,
        "tempo_indefinido": tempo_indefinido,
        "data_marcada": data_marcada,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "status": status,
        "observacoes": observacoes.strip(),
        "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return pedido