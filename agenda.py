from datetime import datetime, date, time, timedelta


# Horário inicial do expediente do trator
HORA_INICIO_EXPEDIENTE = time(7, 0)

# Horário final do expediente do trator
HORA_FIM_EXPEDIENTE = time(17, 0)

# Intervalo obrigatório entre um pedido e outro
# Por enquanto é fixo em 1 hora.
# Futuramente pode ser calculado com Google Maps/deslocamento.
INTERVALO_ENTRE_PEDIDOS = timedelta(hours=1)


def normalizar_hora(hora):
    """
    Normaliza horários vindos de lugares diferentes.

    O formulário HTML geralmente envia:
        08:00

    O Supabase pode devolver:
        08:00:00

    O restante do sistema trabalha com:
        HH:MM

    Então esta função corta o horário para os 5 primeiros caracteres.
    """

    if not hora:
        return None

    hora = str(hora)

    if len(hora) >= 5:
        return hora[:5]

    return hora


def eh_domingo(data):
    """
    Verifica se uma data é domingo.

    No Python:
        segunda = 0
        terça   = 1
        quarta  = 2
        quinta  = 3
        sexta   = 4
        sábado  = 5
        domingo = 6
    """

    return data.weekday() == 6


def proximo_dia_util(data):
    """
    Se a data cair em um domingo, pula para o próximo dia.

    Como o trator não trabalha domingo, essa função garante
    que a agenda sempre comece em um dia permitido.
    """

    while eh_domingo(data):
        data += timedelta(days=1)

    return data


def combinar_data_hora(data, horario):
    """
    Junta uma data e um horário em um único datetime.

    Exemplo:
        data = 2026-07-17
        horario = 08:00

    Resultado:
        2026-07-17 08:00
    """

    return datetime.combine(data, horario)


def tem_conflito(inicio_novo, fim_novo, pedidos_existentes):
    """
    Verifica se um novo horário entra em conflito com pedidos já existentes.

    O conflito acontece quando:
        - o novo pedido começa antes do fim do pedido existente + intervalo
        - e o novo pedido termina depois do início do pedido existente

    Também ignora:
        - pedidos com tempo indefinido
        - pedidos concluídos
        - pedidos cancelados
        - pedidos sem data ou horário
    """

    for pedido in pedidos_existentes:
        # Pedido com tempo indefinido não bloqueia agenda,
        # porque ainda não tem horário definido.
        if pedido.get("tempo_indefinido"):
            continue

        # Pedido concluído ou cancelado não deve impedir novo agendamento.
        if pedido.get("status") in ["Concluído", "Cancelado"]:
            continue

        data_existente = pedido.get("data_marcada")

        # Normaliza para aceitar tanto HH:MM quanto HH:MM:SS
        inicio_existente = normalizar_hora(pedido.get("hora_inicio"))
        fim_existente = normalizar_hora(pedido.get("hora_fim"))

        # Se faltar alguma informação, ignora esse pedido.
        if not data_existente or not inicio_existente or not fim_existente:
            continue

        # Transforma o início do pedido existente em datetime
        inicio_pedido = datetime.strptime(
            f"{data_existente} {inicio_existente}",
            "%Y-%m-%d %H:%M"
        )

        # Transforma o fim do pedido existente em datetime
        fim_pedido = datetime.strptime(
            f"{data_existente} {fim_existente}",
            "%Y-%m-%d %H:%M"
        )

        # Adiciona o intervalo obrigatório depois do pedido existente
        fim_pedido_com_intervalo = fim_pedido + INTERVALO_ENTRE_PEDIDOS

        # Regra de sobreposição:
        # Exemplo:
        # Pedido existente: 08:00 até 11:00
        # Com intervalo:    08:00 até 12:00
        #
        # Novo pedido conflita se:
        # - começa antes de 12:00
        # - e termina depois de 08:00
        existe_conflito = (
            inicio_novo < fim_pedido_com_intervalo
            and fim_novo > inicio_pedido
        )

        if existe_conflito:
            return True

    return False


def buscar_horario_mais_rapido(pedidos_existentes, duracao_horas, data_inicial=None):
    """
    Busca o primeiro horário disponível para um novo pedido.

    Fluxo:
        1. Começa pela data atual, ou pela data_inicial se ela for enviada.
        2. Se cair no domingo, pula para o próximo dia útil.
        3. Começa tentando encaixar no início do expediente.
        4. Testa se há conflito com pedidos existentes.
        5. Se não houver conflito, retorna esse horário.
        6. Se houver conflito, avança 1 hora e tenta de novo.
        7. Se não couber no dia, passa para o próximo dia.
    """

    if data_inicial is None:
        data_atual = date.today()
    else:
        data_atual = data_inicial

    data_atual = proximo_dia_util(data_atual)

    # Converte a duração em horas para timedelta
    duracao = timedelta(hours=duracao_horas)

    while True:
        # Primeiro horário possível do dia
        inicio_novo = combinar_data_hora(data_atual, HORA_INICIO_EXPEDIENTE)

        # Horário final do expediente daquele dia
        fim_expediente = combinar_data_hora(data_atual, HORA_FIM_EXPEDIENTE)

        # Enquanto o pedido ainda couber dentro do expediente
        while inicio_novo + duracao <= fim_expediente:
            fim_novo = inicio_novo + duracao

            # Se não tiver conflito, achamos o horário disponível
            if not tem_conflito(inicio_novo, fim_novo, pedidos_existentes):
                return {
                    "data": data_atual.isoformat(),
                    "inicio": inicio_novo.strftime("%H:%M"),
                    "fim": fim_novo.strftime("%H:%M")
                }

            # Se teve conflito, tenta o próximo horário
            inicio_novo += INTERVALO_ENTRE_PEDIDOS

        # Se não encontrou horário nesse dia, passa para o próximo
        data_atual += timedelta(days=1)
        data_atual = proximo_dia_util(data_atual)


def tem_conflito_na_edicao(
    data_marcada,
    hora_inicio,
    hora_fim,
    pedidos_existentes,
    id_pedido_ignorado
):
    """
    Verifica conflito ao editar um pedido existente.

    Diferença para tem_conflito():
        aqui precisamos ignorar o próprio pedido que está sendo editado.

    Exemplo:
        Pedido 5 já está marcado de 08:00 às 11:00.
        Se eu editar o próprio Pedido 5, ele não pode acusar conflito contra ele mesmo.

    Por isso usamos:
        id_pedido_ignorado
    """

    hora_inicio = normalizar_hora(hora_inicio)
    hora_fim = normalizar_hora(hora_fim)

    inicio_novo = datetime.strptime(
        f"{data_marcada} {hora_inicio}",
        "%Y-%m-%d %H:%M"
    )

    fim_novo = datetime.strptime(
        f"{data_marcada} {hora_fim}",
        "%Y-%m-%d %H:%M"
    )

    if fim_novo <= inicio_novo:
        raise ValueError("A hora final precisa ser depois da hora inicial.")

    for pedido in pedidos_existentes:
        # Ignora o próprio pedido que está sendo editado
        if pedido.get("id") == id_pedido_ignorado:
            continue

        # Tempo indefinido não ocupa horário fixo
        if pedido.get("tempo_indefinido"):
            continue

        # Concluído e cancelado não bloqueiam agenda
        if pedido.get("status") in ["Concluído", "Cancelado"]:
            continue

        data_existente = pedido.get("data_marcada")
        inicio_existente = normalizar_hora(pedido.get("hora_inicio"))
        fim_existente = normalizar_hora(pedido.get("hora_fim"))

        if not data_existente or not inicio_existente or not fim_existente:
            continue

        inicio_pedido = datetime.strptime(
            f"{data_existente} {inicio_existente}",
            "%Y-%m-%d %H:%M"
        )

        fim_pedido = datetime.strptime(
            f"{data_existente} {fim_existente}",
            "%Y-%m-%d %H:%M"
        )

        fim_pedido_com_intervalo = fim_pedido + INTERVALO_ENTRE_PEDIDOS

        existe_conflito = (
            inicio_novo < fim_pedido_com_intervalo
            and fim_novo > inicio_pedido
        )

        if existe_conflito:
            return True

    return False