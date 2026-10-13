"""
Camada de Logica de Negocio (Business Layer)
---------------------------------------------
Aqui ficam as regras da aplicacao. Esta camada nao sabe nada sobre
HTTP nem sobre SQL diretamente - ela conversa apenas com a camada de dados
(database.py) e aplica as validacoes necessarias.
"""

import database

DIAMETROS_VALIDOS = (1.75, 2.85, 3.00)


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
    database.deletar_produto(produto_id)
