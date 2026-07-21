def gerar_mensagem_pedido(pedido):
    """
    Gera uma mensagem simples e direta para o agricultor.
    """

    # Extrai os dados do pedido para montar a mensagem
    nome = pedido["nome_agricultor"]
    servico = pedido["servico"]
    local = pedido["local"]
    status = pedido["status"]

    # Verifica se o tempo do serviço é indefinido
    if pedido["tempo_indefinido"]:
        # Cria uma mensagem para o caso em que o serviço ainda não tem data/hora definida
        mensagem = f"""Olá, {nome}.

Seu pedido para {servico.lower()} foi recebido.

Local: {local}

O tempo do serviço ainda precisa ser avaliado.
O responsável vai entrar em contato para confirmar a data e o horário.

Status: {status}."""

        return mensagem

    # Cria uma mensagem para o caso em que o serviço já foi agendado
    mensagem = f"""Olá, {nome}.

Seu pedido para {servico.lower()} foi agendado.

Local: {local}
Data: {pedido["data_marcada"]}
Horário: {pedido["hora_inicio"]} até {pedido["hora_fim"]}

Status: {status}."""

    return mensagem