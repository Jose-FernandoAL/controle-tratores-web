# Controle de Pedidos do Trator - Versão Web

Sistema web feito com Flask para cadastrar, listar, editar, concluir, remover e gerar mensagens de pedidos de serviço com trator.

## Como executar

1. Abra o terminal dentro da pasta do projeto.
2. Crie o ambiente virtual:

```bash
python -m venv venv
```

3. Ative o ambiente virtual no Windows:

```bash
venv\Scripts\activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Execute o sistema:

```bash
python app.py
```

6. Abra no navegador:

```txt
http://127.0.0.1:5000
```

## Estrutura

```txt
app.py              # Rotas web e comunicação com a interface
agenda.py           # Regras de agenda e conflito de horário
database.py         # Leitura e gravação no JSON
pedidos.py          # Validação e criação de pedidos
mensagens.py        # Mensagens para o agricultor
pedidos.json        # Banco de dados simples
templates/          # Páginas HTML
static/             # CSS
```

## Observação importante

A interface web não guarda a lógica principal. Ela apenas envia os dados para o Flask. As regras continuam separadas nos módulos `agenda.py`, `pedidos.py`, `database.py` e `mensagens.py`.
