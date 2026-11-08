"""
Camada de Logica de Negocio (Business Layer)
---------------------------------------------
Aqui ficam as regras da aplicacao. Esta camada nao sabe nada sobre
HTTP nem sobre SQL diretamente - ela conversa apenas com a camada de dados
(database.py) e aplica as validacoes necessarias.
"""

from datetime import date, datetime

import database

DIAMETROS_VALIDOS = (1.75, 2.85, 3.00)
STATUS_PEDIDO = ("Pendente", "Em produção", "Concluído", "Cancelado")


class RegraDeNegocioError(Exception):
    """Erro esperado de regra de negocio (ex: nome duplicado, referencia em uso)."""
    pass


# ---------- Cadastros auxiliares: Marca, Cor, Material ----------
# As tres tabelas seguem a mesma regra, entao usamos uma unica implementacao
# generica reaproveitada pelas rotas especificas de cada entidade.

def cadastrar_simples(tabela, nome):
    nome = (nome or "").strip()
    if not nome:
        raise RegraDeNegocioError("O nome e obrigatorio.")
    if len(nome) > 60:
        raise RegraDeNegocioError("O nome deve ter no maximo 60 caracteres.")

    existentes = [item["nome"].lower() for item in database.listar_simples(tabela)]
    if nome.lower() in existentes:
        raise RegraDeNegocioError(f'"{nome}" ja esta cadastrado.')

    return database.inserir_simples(tabela, nome)


def listar_simples(tabela):
    return database.listar_simples(tabela)


def atualizar_simples(tabela, item_id, nome):
    nome = (nome or "").strip()
    if not nome:
        raise RegraDeNegocioError("O nome e obrigatorio.")

    item = database.buscar_simples(tabela, item_id)
    if not item:
        raise RegraDeNegocioError("Registro nao encontrado.")

    existentes = [i["nome"].lower() for i in database.listar_simples(tabela) if i["id"] != item_id]
    if nome.lower() in existentes:
        raise RegraDeNegocioError(f'"{nome}" ja esta cadastrado.')

    database.atualizar_simples(tabela, item_id, nome)


def remover_simples(tabela, item_id, coluna_fk):
    item = database.buscar_simples(tabela, item_id)
    if not item:
        raise RegraDeNegocioError("Registro nao encontrado.")

    em_uso = database.contar_filamentos_usando(coluna_fk, item_id)
    if em_uso > 0:
        raise RegraDeNegocioError(
            f'Nao e possivel excluir "{item["nome"]}": esta em uso em {em_uso} filamento(s) cadastrado(s).'
        )

    database.deletar_simples(tabela, item_id)


# ---------- Filamentos ----------

def _validar_dados_filamento(marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos):
    if not database.buscar_simples("marcas", marca_id):
        raise RegraDeNegocioError("Marca selecionada nao existe.")
    if not database.buscar_simples("cores", cor_id):
        raise RegraDeNegocioError("Cor selecionada nao existe.")
    if not database.buscar_simples("materiais", material_id):
        raise RegraDeNegocioError("Material selecionado nao existe.")

    if diametro_mm is None or diametro_mm <= 0:
        raise RegraDeNegocioError("Diametro invalido.")
    if peso_rolo_g is None or peso_rolo_g <= 0:
        raise RegraDeNegocioError("Peso do rolo deve ser maior que zero.")
    if quantidade_rolos is None or quantidade_rolos < 0:
        raise RegraDeNegocioError("Quantidade de rolos nao pode ser negativa.")


def cadastrar_filamento(marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos):
    _validar_dados_filamento(marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos)
    return database.inserir_filamento(
        marca_id, cor_id, material_id, float(diametro_mm), float(peso_rolo_g), int(quantidade_rolos)
    )


def obter_filamentos():
    filamentos = database.listar_filamentos()
    for f in filamentos:
        f["peso_total_g"] = round(f["peso_rolo_g"] * f["quantidade_rolos"], 1)
    return filamentos


def atualizar_filamento(filamento_id, marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos):
    if not database.buscar_filamento(filamento_id):
        raise RegraDeNegocioError("Filamento nao encontrado.")
    _validar_dados_filamento(marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos)
    database.atualizar_filamento(
        filamento_id, marca_id, cor_id, material_id, float(diametro_mm), float(peso_rolo_g), int(quantidade_rolos)
    )


def remover_filamento(filamento_id):
    if not database.buscar_filamento(filamento_id):
        raise RegraDeNegocioError("Filamento nao encontrado.")

    em_uso = database.contar_produtos_usando_filamento(filamento_id)
    if em_uso > 0:
        raise RegraDeNegocioError(
            f"Nao e possivel excluir: este filamento e usado em {em_uso} produto(s) cadastrado(s)."
        )

    database.deletar_filamento(filamento_id)


# ---------- Produtos ----------

def _validar_produto(nome, tempo_impressao_h, preco_venda, filamentos):
    nome = (nome or "").strip()
    if not nome:
        raise RegraDeNegocioError("O nome do produto e obrigatorio.")
    if len(nome) > 100:
        raise RegraDeNegocioError("O nome deve ter no maximo 100 caracteres.")
    if tempo_impressao_h is None or tempo_impressao_h <= 0:
        raise RegraDeNegocioError("O tempo de impressao deve ser maior que zero.")
    if preco_venda is None or preco_venda < 0:
        raise RegraDeNegocioError("O preco de venda nao pode ser negativo.")

    if not filamentos:
        raise RegraDeNegocioError("Informe ao menos um filamento para o produto.")

    ids_vistos = set()
    itens = []
    for item in filamentos:
        filamento_id = item.get("filamento_id")
        peso_g = item.get("peso_g")

        if not database.buscar_filamento(filamento_id):
            raise RegraDeNegocioError("Um dos filamentos selecionados nao existe.")
        if filamento_id in ids_vistos:
            raise RegraDeNegocioError("O mesmo filamento foi informado mais de uma vez.")
        if peso_g is None or peso_g <= 0:
            raise RegraDeNegocioError("O peso gasto de cada filamento deve ser maior que zero.")

        ids_vistos.add(filamento_id)
        itens.append({"filamento_id": filamento_id, "peso_g": float(peso_g)})

    return nome, float(tempo_impressao_h), float(preco_venda), itens


def cadastrar_produto(nome, tempo_impressao_h, preco_venda, filamentos):
    nome, tempo, preco, itens = _validar_produto(nome, tempo_impressao_h, preco_venda, filamentos)
    return database.inserir_produto(nome, tempo, preco, itens)


def obter_produtos():
    produtos = database.listar_produtos()
    for p in produtos:
        p["peso_total_g"] = round(sum(f["peso_g"] for f in p["filamentos"]), 1)
    return produtos


def atualizar_produto(produto_id, nome, tempo_impressao_h, preco_venda, filamentos):
    if not database.buscar_produto(produto_id):
        raise RegraDeNegocioError("Produto nao encontrado.")
    nome, tempo, preco, itens = _validar_produto(nome, tempo_impressao_h, preco_venda, filamentos)
    database.atualizar_produto(produto_id, nome, tempo, preco, itens)


def remover_produto(produto_id):
    if not database.buscar_produto(produto_id):
        raise RegraDeNegocioError("Produto nao encontrado.")

    em_uso = database.contar_pedidos_usando_produto(produto_id)
    if em_uso > 0:
        raise RegraDeNegocioError(
            f"Nao e possivel excluir: este produto esta em {em_uso} pedido(s) cadastrado(s)."
        )

    database.deletar_produto(produto_id)


# ---------- Pedidos ----------

def _validar_pedido(cliente_nome, data_pedido, status, itens, itens_antigos=None):
    """Valida os dados e devolve (cliente, data, status, itens prontos para gravar).

    itens_antigos: itens ja gravados (na edicao). Produtos que continuam no
    pedido mantem o preco da epoca da venda; produtos novos usam o preco atual.
    """
    cliente_nome = (cliente_nome or "").strip()
    if not cliente_nome:
        raise RegraDeNegocioError("O nome do cliente e obrigatorio.")
    if len(cliente_nome) > 100:
        raise RegraDeNegocioError("O nome do cliente deve ter no maximo 100 caracteres.")

    if not data_pedido:
        data_pedido = date.today().isoformat()
    try:
        datetime.strptime(data_pedido, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise RegraDeNegocioError("Data do pedido invalida.")

    status = status or STATUS_PEDIDO[0]
    if status not in STATUS_PEDIDO:
        raise RegraDeNegocioError("Status invalido.")

    if not itens:
        raise RegraDeNegocioError("Informe ao menos um produto no pedido.")

    precos_antigos = {i["produto_id"]: i["preco_unitario"] for i in (itens_antigos or [])}
    ids_vistos = set()
    itens_validos = []
    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")

        produto = database.buscar_produto(produto_id)
        if not produto:
            raise RegraDeNegocioError("Um dos produtos selecionados nao existe.")
        if produto_id in ids_vistos:
            raise RegraDeNegocioError("O mesmo produto foi informado mais de uma vez.")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise RegraDeNegocioError("A quantidade de cada produto deve ser um numero inteiro maior que zero.")

        ids_vistos.add(produto_id)
        itens_validos.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
            "preco_unitario": precos_antigos.get(produto_id, produto["preco_venda"]),
        })

    return cliente_nome, data_pedido, status, itens_validos


def cadastrar_pedido(cliente_nome, data_pedido, status, itens):
    cliente, data, status, itens_validos = _validar_pedido(cliente_nome, data_pedido, status, itens)
    return database.inserir_pedido(cliente, data, status, itens_validos)


def obter_pedidos():
    pedidos = database.listar_pedidos()
    for p in pedidos:
        for item in p["itens"]:
            item["subtotal"] = round(item["quantidade"] * item["preco_unitario"], 2)
        p["valor_total"] = round(sum(i["subtotal"] for i in p["itens"]), 2)
    return pedidos


def atualizar_pedido(pedido_id, cliente_nome, data_pedido, status, itens):
    if not database.buscar_pedido(pedido_id):
        raise RegraDeNegocioError("Pedido nao encontrado.")
    itens_antigos = database.listar_itens_do_pedido(pedido_id)
    cliente, data, status, itens_validos = _validar_pedido(
        cliente_nome, data_pedido, status, itens, itens_antigos
    )
    database.atualizar_pedido(pedido_id, cliente, data, status, itens_validos)


def alterar_status_pedido(pedido_id, status):
    if not database.buscar_pedido(pedido_id):
        raise RegraDeNegocioError("Pedido nao encontrado.")
    if status not in STATUS_PEDIDO:
        raise RegraDeNegocioError("Status invalido.")
    database.atualizar_status_pedido(pedido_id, status)


def remover_pedido(pedido_id):
    if not database.buscar_pedido(pedido_id):
        raise RegraDeNegocioError("Pedido nao encontrado.")
    database.deletar_pedido(pedido_id)
