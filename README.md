# Controle de Tratores Web

Sistema web para organizar pedidos de serviços com trator, como arar terra, puxar carga e moer silagem.

O sistema permite cadastrar pedidos, listar pedidos, concluir, editar, remover e gerar mensagem para WhatsApp. Os dados são salvos online usando Supabase.

## Tecnologias usadas

- Python
- Flask
- HTML
- CSS
- Supabase
- python-dotenv

## Funcionalidades

- Cadastro de pedidos
- Listagem de pedidos
- Filtro por status
- Edição de pedidos
- Conclusão de pedidos
- Remoção de pedidos
- Geração de mensagem para WhatsApp
- Banco de dados online com Supabase

## Como iniciar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/Jose-FernandoAL/controle-tratores-web.git
cd controle-tratores-web

6. Rodar o sistema
python app.py

Depois acesse no navegador:

http://127.0.0.1:5000
Compartilhar com outras pessoas usando Cloudflared

Com o Flask rodando, abra outro terminal e execute:

cloudflared tunnel --url http://localhost:5000

O Cloudflared vai gerar um link temporário para acesso externo.

Exemplo:

https://exemplo.trycloudflare.com

Esse link só funciona enquanto o Flask e o Cloudflared estiverem rodando.
