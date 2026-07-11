from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for, flash

from agenda import buscar_horario_mais_rapido
from database import (
    adicionar_pedido,
    alterar_status_pedido,
    atualizar_pedido,
    buscar_pedido_por_id,
    carregar_pedidos,
    remover_pedido,
)
from mensagens import gerar_mensagem_pedido
from pedidos import SERVICOS_VALIDOS, STATUS_VALIDOS, criar_pedido

app = Flask(__name__)
app.secret_key = "controle-tratores-dev"


def chave_ordenacao_pedido(pedido):
    """
    Ordena os pedidos:
    1. Agendados / Em andamento primeiro
    2. Pendentes depois
    3. Concluídos por último
    """
    status = pedido.get("status", "")

    if status == "Concluído":
        grupo = 3
    elif status == "Pendente":
        grupo = 2
    else:
        grupo = 1

    data_marcada = pedido.get("data_marcada")
    hora_inicio = pedido.get("hora_inicio")

    if data_marcada and hora_inicio:
        try:
            data_hora = datetime.strptime(
                f"{data_marcada} {hora_inicio}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            data_hora = datetime.max
    else:
        data_hora = datetime.max

    return grupo, data_hora


def formatar_horario(pedido):
    if pedido.get("tempo_indefinido"):
        return "A definir"

    inicio = pedido.get("hora_inicio") or ""
    fim = pedido.get("hora_fim") or ""

    if not inicio and not fim:
        return "A definir"

    return f"{inicio} até {fim}"


@app.route("/", methods=["GET"])
def index():
    pedidos = sorted(carregar_pedidos(), key=chave_ordenacao_pedido)
    mensagem = request.args.get("mensagem", "")

    return render_template(
        "index.html",
        pedidos=pedidos,
        servicos=SERVICOS_VALIDOS,
        status_validos=STATUS_VALIDOS,
        mensagem=mensagem,
        formatar_horario=formatar_horario,
    )


@app.route("/pedidos", methods=["POST"])
def cadastrar_pedido():
    try:
        pedidos_existentes = carregar_pedidos()

        nome = request.form.get("nome_agricultor", "").strip()
        telefone = request.form.get("telefone", "").strip()
        servico = request.form.get("servico", "").strip()
        local = request.form.get("local", "").strip()
        tempo_indefinido = request.form.get("tempo_indefinido") == "on"
        observacoes = request.form.get("observacoes", "").strip()

        if tempo_indefinido:
            pedido = criar_pedido(
                pedidos_existentes=pedidos_existentes,
                nome_agricultor=nome,
                telefone=telefone,
                servico=servico,
                local=local,
                tempo_indefinido=True,
                observacoes=observacoes or "Tempo do serviço precisa ser avaliado.",
            )
        else:
            duracao_texto = request.form.get("duracao_horas", "").strip()

            if duracao_texto == "":
                raise ValueError("Informe a duração do serviço em horas.")

            duracao = int(duracao_texto)

            horario = buscar_horario_mais_rapido(
                pedidos_existentes=pedidos_existentes,
                duracao_horas=duracao,
                data_inicial=date.today(),
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
                observacoes=observacoes,
            )

        adicionar_pedido(pedido)
        flash("Pedido cadastrado com sucesso.", "sucesso")
        return redirect(url_for("index", mensagem=gerar_mensagem_pedido(pedido)))

    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))

    except Exception as erro:
        flash(f"Erro inesperado: {erro}", "erro")
        return redirect(url_for("index"))


@app.route("/pedidos/<int:id_pedido>/concluir", methods=["POST"])
def concluir_pedido(id_pedido):
    if alterar_status_pedido(id_pedido, "Concluído"):
        flash("Pedido marcado como concluído.", "sucesso")
    else:
        flash("Pedido não encontrado.", "erro")

    return redirect(url_for("index"))


@app.route("/pedidos/<int:id_pedido>/remover", methods=["POST"])
def remover_pedido_web(id_pedido):
    if remover_pedido(id_pedido):
        flash("Pedido removido com sucesso.", "sucesso")
    else:
        flash("Pedido não encontrado.", "erro")

    return redirect(url_for("index"))


@app.route("/pedidos/<int:id_pedido>/mensagem", methods=["GET"])
def gerar_mensagem(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)

    if pedido is None:
        flash("Pedido não encontrado.", "erro")
        return redirect(url_for("index"))

    return redirect(url_for("index", mensagem=gerar_mensagem_pedido(pedido)))


@app.route("/pedidos/<int:id_pedido>/editar", methods=["GET", "POST"])
def editar_pedido(id_pedido):
    pedido = buscar_pedido_por_id(id_pedido)

    if pedido is None:
        flash("Pedido não encontrado.", "erro")
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template(
            "editar.html",
            pedido=pedido,
            servicos=SERVICOS_VALIDOS,
            status_validos=STATUS_VALIDOS,
        )

    try:
        nome = request.form.get("nome_agricultor", "").strip()
        telefone = request.form.get("telefone", "").strip()
        servico = request.form.get("servico", "").strip()
        local = request.form.get("local", "").strip()
        duracao_texto = request.form.get("duracao_horas", "").strip()
        data = request.form.get("data_marcada", "").strip()
        hora_inicio = request.form.get("hora_inicio", "").strip()
        hora_fim = request.form.get("hora_fim", "").strip()
        status = request.form.get("status", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if nome == "":
            raise ValueError("O nome do agricultor é obrigatório.")
        if telefone == "":
            raise ValueError("O telefone é obrigatório.")
        if local == "":
            raise ValueError("O local/sítio é obrigatório.")
        if servico not in SERVICOS_VALIDOS:
            raise ValueError("Serviço inválido.")
        if status not in STATUS_VALIDOS:
            raise ValueError("Status inválido.")

        if duracao_texto == "":
            duracao = None
            tempo_indefinido = True
            data = None
            hora_inicio = None
            hora_fim = None
            status = "Pendente"
        else:
            duracao = int(duracao_texto)
            tempo_indefinido = False

            if duracao <= 0:
                raise ValueError("A duração precisa ser maior que zero.")
            if data == "":
                raise ValueError("Informe a data marcada.")
            if hora_inicio == "":
                raise ValueError("Informe a hora de início.")
            if hora_fim == "":
                raise ValueError("Informe a hora de fim.")

            datetime.strptime(data, "%Y-%m-%d")
            datetime.strptime(hora_inicio, "%H:%M")
            datetime.strptime(hora_fim, "%H:%M")

        dados_atualizados = {
            "nome_agricultor": nome,
            "telefone": telefone,
            "servico": servico,
            "local": local,
            "duracao_horas": duracao,
            "tempo_indefinido": tempo_indefinido,
            "data_marcada": data,
            "hora_inicio": hora_inicio,
            "hora_fim": hora_fim,
            "status": status,
            "observacoes": observacoes,
        }

        if atualizar_pedido(id_pedido, dados_atualizados):
            flash("Pedido editado com sucesso.", "sucesso")
        else:
            flash("Pedido não encontrado.", "erro")

        return redirect(url_for("index"))

    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("editar_pedido", id_pedido=id_pedido))

    except Exception as erro:
        flash(f"Erro inesperado: {erro}", "erro")
        return redirect(url_for("editar_pedido", id_pedido=id_pedido))


if __name__ == "__main__":
    app.run(debug=True)
