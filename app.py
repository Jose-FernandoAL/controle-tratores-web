from datetime import date, datetime
from urllib.parse import quote
import re

from flask import Flask, flash, redirect, render_template, request, url_for

from agenda import buscar_horario_mais_rapido
from database import (
    adicionar_pedido, alterar_status_pedido, atualizar_pedido,
    buscar_pedido_por_id, carregar_pedidos, remover_pedido,
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
    return sorted(carregar_pedidos(), key=chave_ordenacao_pedido)


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


@app.get("/pedidos")
def listar_pedidos():
    status = request.args.get("status", "").strip()
    pedidos = pedidos_ordenados()
    if status:
        pedidos = [p for p in pedidos if p.get("status") == status]
    return render_template(
        "pedidos.html", pedidos=pedidos, status_selecionado=status,
        status_validos=STATUS_VALIDOS, formatar_horario=formatar_horario,
    )


@app.route("/pedidos/novo", methods=["GET", "POST"])
def novo_pedido():
    if request.method == "GET":
        return render_template("novo_pedido.html", servicos=SERVICOS_VALIDOS)
    try:
        existentes = carregar_pedidos()
        tempo_indefinido = request.form.get("tempo_indefinido") == "on"
        dados = {
            "pedidos_existentes": existentes,
            "nome_agricultor": request.form.get("nome_agricultor", "").strip(),
            "telefone": request.form.get("telefone", "").strip(),
            "servico": request.form.get("servico", "").strip(),
            "local": request.form.get("local", "").strip(),
            "tempo_indefinido": tempo_indefinido,
            "observacoes": request.form.get("observacoes", "").strip(),
        }
        if tempo_indefinido:
            dados["observacoes"] = dados["observacoes"] or "Tempo do serviço precisa ser avaliado."
        else:
            duracao_texto = request.form.get("duracao_horas", "").strip()
            if not duracao_texto:
                raise ValueError("Informe a duração do serviço em horas.")
            duracao = int(duracao_texto)
            horario = buscar_horario_mais_rapido(existentes, duracao, date.today())
            dados.update(
                duracao_horas=duracao, data_marcada=horario["data"],
                hora_inicio=horario["inicio"], hora_fim=horario["fim"],
            )
        pedido = criar_pedido(**dados)
        adicionar_pedido(pedido)
        flash("Pedido cadastrado no primeiro horário disponível.", "sucesso")
        return redirect(url_for("listar_pedidos"))
    except (ValueError, TypeError) as erro:
        flash(str(erro), "erro")
        return redirect(url_for("novo_pedido"))


@app.post("/pedidos/<int:id_pedido>/concluir")
def concluir_pedido(id_pedido):
    flash(
        "Pedido marcado como concluído." if alterar_status_pedido(id_pedido, "Concluído")
        else "Pedido não encontrado.",
        "sucesso" if buscar_pedido_por_id(id_pedido) else "erro",
    )
    return redirect(url_for("listar_pedidos"))


@app.post("/pedidos/<int:id_pedido>/remover")
def remover_pedido_web(id_pedido):
    if remover_pedido(id_pedido):
        flash("Pedido removido com sucesso.", "sucesso")
    else:
        flash("Pedido não encontrado.", "erro")
    return redirect(url_for("listar_pedidos"))


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


@app.route("/pedidos/<int:id_pedido>/editar", methods=["GET", "POST"])
def editar_pedido(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)
    if not pedido:
        flash("Pedido não encontrado.", "erro")
        return redirect(url_for("listar_pedidos"))
    if request.method == "GET":
        return render_template(
            "editar.html", pedido=pedido, servicos=SERVICOS_VALIDOS,
            status_validos=STATUS_VALIDOS,
        )
    try:
        dados = {
            "nome_agricultor": request.form.get("nome_agricultor", "").strip(),
            "telefone": request.form.get("telefone", "").strip(),
            "servico": request.form.get("servico", "").strip(),
            "local": request.form.get("local", "").strip(),
            "status": request.form.get("status", "").strip(),
            "observacoes": request.form.get("observacoes", "").strip(),
        }
        if not all(dados[k] for k in ("nome_agricultor", "telefone", "servico", "local")):
            raise ValueError("Preencha todos os campos obrigatórios.")
        if dados["servico"] not in SERVICOS_VALIDOS or dados["status"] not in STATUS_VALIDOS:
            raise ValueError("Serviço ou status inválido.")
        atualizar_pedido(id_pedido, dados)
        flash("Pedido editado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedidos"))
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("editar_pedido", id_pedido=id_pedido))


if __name__ == "__main__":
    app.run(debug=True)
