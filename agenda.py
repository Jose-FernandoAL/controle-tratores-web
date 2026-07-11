from datetime import datetime, date, time, timedelta


HORA_INICIO_EXPEDIENTE = time(7, 0)
HORA_FIM_EXPEDIENTE = time(17, 0)
INTERVALO_ENTRE_PEDIDOS = timedelta(hours=1)


def eh_domingo(data):
    """
    Retorna True se a data for domingo.
    No Python:
    segunda = 0
    terça = 1
    ...
    domingo = 6
    """
    return data.weekday() == 6


def proximo_dia_util(data):
    """
    Avança para o próximo dia que não seja domingo.
    """
    data += timedelta(days=1)

    while eh_domingo(data):
        data += timedelta(days=1)

    return data


def combinar_data_hora(data, horario):
    """
    Junta uma data com um horário.
    Exemplo:
    data = 2026-07-06
    horario = 07:00
    resultado = 2026-07-06 07:00
    """
    return datetime.combine(data, horario)


def tem_conflito(inicio_novo, fim_novo, pedidos_existentes):
    """
    Verifica se o novo pedido entra em conflito com pedidos já marcados.
    Também considera 1 hora de intervalo depois de cada pedido existente.
    """

    for pedido in pedidos_existentes:
        # Ignora pedidos pendentes ou sem horário definido
        if pedido.get("tempo_indefinido"):
            continue

        if not pedido.get("data_marcada") or not pedido.get("hora_inicio") or not pedido.get("hora_fim"):
            continue

        inicio_existente = datetime.strptime(
            f"{pedido['data_marcada']} {pedido['hora_inicio']}",
            "%Y-%m-%d %H:%M"
        )

        fim_existente = datetime.strptime(
            f"{pedido['data_marcada']} {pedido['hora_fim']}",
            "%Y-%m-%d %H:%M"
        )

        fim_com_intervalo = fim_existente + INTERVALO_ENTRE_PEDIDOS

        conflito = inicio_novo < fim_com_intervalo and fim_novo > inicio_existente

        if conflito:
            return True

    return False


def buscar_horario_mais_rapido(pedidos_existentes, duracao_horas, data_inicial=None):
    """
    Procura o primeiro horário disponível para um novo pedido.

    pedidos_existentes: lista de pedidos já marcados
    duracao_horas: duração do novo serviço
    data_inicial: data para começar a busca
    """

    if data_inicial is None:
        data_atual = date.today()
    else:
        data_atual = data_inicial

    duracao = timedelta(hours=duracao_horas)

    while True:
        if eh_domingo(data_atual):
            data_atual = proximo_dia_util(data_atual)
            continue

        inicio_expediente = combinar_data_hora(
            data_atual,
            HORA_INICIO_EXPEDIENTE
        )

        fim_expediente = combinar_data_hora(
            data_atual,
            HORA_FIM_EXPEDIENTE
        )

        horario_teste = inicio_expediente

        while horario_teste + duracao <= fim_expediente:
            inicio_novo = horario_teste
            fim_novo = inicio_novo + duracao

            if not tem_conflito(inicio_novo, fim_novo, pedidos_existentes):
                return {
                    "data": inicio_novo.strftime("%Y-%m-%d"),
                    "inicio": inicio_novo.strftime("%H:%M"),
                    "fim": fim_novo.strftime("%H:%M"),
                }

            horario_teste += timedelta(hours=1)

        data_atual = proximo_dia_util(data_atual)