from datetime import date, datetime
from urllib.parse import quote
import re

from flask import Flask, flash, redirect, render_template, request, url_for

from agenda import buscar_horario_mais_rapido
from supabase_db import (
    listar_pedidos as listar_pedidos_supabase,
    adicionar_pedido,
    buscar_pedido_por_id,
    atualizar_pedido,
    alterar_status_pedido,
    remover_pedido
)
from mensagens import gerar_mensagem_pedido
from pedidos import SERVICOS_VALIDOS, STATUS_VALIDOS, criar_pedido

app = Flask(__name__)
app.secret_key = "controle-tratores-dev"


def chave_ordenacao_pedido(pedido):
    grupos = {"Agendado": 1, "Em andamento": 1, "Pendente": 2, "Concluído": 3}
    grupo = grupos.get(pedido.get("status"), 2)
    try:
        data_hora = datetime.strptime(
            f"{pedido.get('data_marcada')} {pedido.get('hora_inicio')}",
            "%Y-%m-%d %H:%M",
        )
    except (TypeError, ValueError):
        data_hora = datetime.max
    return grupo, data_hora


def formatar_horario(pedido):
    if pedido.get("tempo_indefinido") or not pedido.get("hora_inicio"):
        return "A definir"
    return f"{pedido['hora_inicio']}–{pedido.get('hora_fim', '')}"


def pedidos_ordenados():
    return sorted(listar_pedidos_supabase(), key=chave_ordenacao_pedido)

def calcular_metricas(pedidos):
    from datetime import date

    hoje = date.today().isoformat()

    return {
        "ativos": sum(
            1 for pedido in pedidos
            if pedido.get("status") not in ["Concluído", "Cancelado"]
        ),
        "hoje": sum(
            1 for pedido in pedidos
            if pedido.get("data_marcada") == hoje
        ),
        "concluidos": sum(
            1 for pedido in pedidos
            if pedido.get("status") == "Concluído"
        ),
        "pendentes": sum(
            1 for pedido in pedidos
            if pedido.get("status") == "Pendente"
        )
    }

@app.get("/")
def index():
    pedidos = pedidos_ordenados()
    ativos = [p for p in pedidos if p.get("status") not in ("Concluído", "Cancelado")]
    hoje = date.today().isoformat()
    metricas = {
        "ativos": len(ativos),
        "hoje": sum(p.get("data_marcada") == hoje for p in ativos),
        "concluidos": sum(p.get("status") == "Concluído" for p in pedidos),
        "pendentes": sum(p.get("status") == "Pendente" for p in pedidos),
    }
    return render_template(
        "index.html", pedidos=ativos[:4], metricas=metricas,
        formatar_horario=formatar_horario,
    )


@app.route("/pedidos")
def listar_pedidos_rota():
    status = request.args.get("status", "").strip()
    pedidos = pedidos_ordenados()

    if status:
        pedidos = [
            pedido for pedido in pedidos
            if pedido.get("status") == status
        ]

    metricas = calcular_metricas(pedidos_ordenados())

    return render_template(
        "index.html",
        pedidos=pedidos,
        status=status,
        metricas=metricas,
        formatar_horario=formatar_horario
    )


@app.route("/pedidos/novo", methods=["GET", "POST"])
def novo_pedido():
    if request.method == "POST":
        nome = request.form.get("nome_agricultor")
        telefone = request.form.get("telefone")
        servico = request.form.get("servico")
        local = request.form.get("local")
        duracao = request.form.get("duracao_horas")
        tempo_indefinido = request.form.get("tempo_indefinido") == "on"

        pedidos_existentes = listar_pedidos_supabase()

        if tempo_indefinido:
            pedido = criar_pedido(
                pedidos_existentes=pedidos_existentes,
                nome_agricultor=nome,
                telefone=telefone,
                servico=servico,
                local=local,
                tempo_indefinido=True,
                observacoes="Tempo do serviço precisa ser avaliado."
            )
        else:
            duracao = int(duracao)

            horario = buscar_horario_mais_rapido(
                pedidos_existentes=pedidos_existentes,
                duracao_horas=duracao
            )

            pedido = criar_pedido(
                pedidos_existentes=pedidos_existentes,
                nome_agricultor=nome,
                telefone=telefone,
                servico=servico,
                local=local,
                duracao_horas=duracao,
                tempo_indefinido=False,
                data_marcada=horario["data"],
                hora_inicio=horario["inicio"],
                hora_fim=horario["fim"],
                observacoes=""
            )

        adicionar_pedido(pedido)

        return redirect(url_for("index"))

    return render_template("novo_pedido.html")

@app.route("/pedidos/concluir/<int:id_pedido>", methods=["POST"])
def concluir(id_pedido):
    alterar_status_pedido(id_pedido, "Concluído")
    return redirect(url_for("index"))



@app.get("/pedidos/<int:id_pedido>/mensagem")
def abrir_whatsapp(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)
    if not pedido:
        flash("Pedido não encontrado.", "erro")
        return redirect(url_for("listar_pedidos"))
    telefone = re.sub(r"\D", "", pedido.get("telefone", ""))
    if telefone and not telefone.startswith("55"):
        telefone = "55" + telefone
    texto = quote(gerar_mensagem_pedido(pedido))
    return redirect(f"https://wa.me/{telefone}?text={texto}")


@app.get("/mensagens")
def mensagens():
    return render_template("mensagens.html", pedidos=pedidos_ordenados())

@app.route("/pedidos/remover/<int:id_pedido>", methods=["POST"])
def remover_pedido_rota(id_pedido):
    remover_pedido(id_pedido)
    return redirect(url_for("index"))

@app.route("/pedidos/editar/<int:id_pedido>", methods=["GET", "POST"])
def editar_pedido_rota(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)

    if request.method == "POST":
        dados_atualizados = {
            "nome_agricultor": request.form.get("nome_agricultor"),
            "telefone": request.form.get("telefone"),
            "servico": request.form.get("servico"),
            "local": request.form.get("local"),
            "duracao_horas": int(request.form.get("duracao_horas")),
            "data_marcada": request.form.get("data_marcada"),
            "hora_inicio": request.form.get("hora_inicio"),
            "hora_fim": request.form.get("hora_fim"),
            "status": request.form.get("status"),
            "tempo_indefinido": False
        }

        atualizar_pedido(id_pedido, dados_atualizados)

        return redirect(url_for("index"))

    return render_template("editar.html", pedido=pedido)


if __name__ == "__main__":
    app.run(debug=True)
