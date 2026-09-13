import database

DIAMETROS_VALIDOS = (1.75, 2.85, 3.00)


class RegraDeNegocioError(Exception):
    """Erro esperado de regra de negocio (ex: nome duplicado, referencia em uso)."""
    pass


# ---------- Cadastros auxiliares: Marca, Cor, Material ----------

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
    database.deletar_filamento(filamento_id)
