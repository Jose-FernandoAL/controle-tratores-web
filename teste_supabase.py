from supabase_db import adicionar_pedido, listar_pedidos


pedido_teste = {
    "nome_agricultor": "João Teste",
    "telefone": "87999990000",
    "servico": "Arar terra",
    "local": "Sítio Teste",
    "duracao_horas": 3,
    "tempo_indefinido": False,
    "data_marcada": "2026-07-20",
    "hora_inicio": "08:00",
    "hora_fim": "11:00",
    "status": "Agendado",
    "observacoes": "Pedido de teste"
}

adicionar_pedido(pedido_teste)

pedidos = listar_pedidos()

for pedido in pedidos:
    print(pedido)