def gerar_mensagem_pedido(pedido):
    """
    Gera uma mensagem simples e direta para o agricultor.
    """

    nome = pedido["nome_agricultor"]
    servico = pedido["servico"]
    local = pedido["local"]
    status = pedido["status"]

    if pedido["tempo_indefinido"]:
        mensagem = f"""Olá, {nome}.

Seu pedido para {servico.lower()} foi recebido.

Local: {local}

O tempo do serviço ainda precisa ser avaliado.
O responsável vai entrar em contato para confirmar a data e o horário.

Status: {status}."""

        return mensagem

    mensagem = f"""Olá, {nome}.

Seu pedido para {servico.lower()} foi agendado.

Local: {local}
Data: {pedido["data_marcada"]}
Horário: {pedido["hora_inicio"]} até {pedido["hora_fim"]}

Status: {status}."""

    return mensagem