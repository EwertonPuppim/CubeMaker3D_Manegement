# CubeMaker3D Management

Projeto de TCC

Etapa 1 - Cadastros de itens auxiliares como Marca, Cor, filamentos

Etapa 2 - Cadastro de itens criados

Etapa 3 - Controle de pedidos/vendas


## Arquitetura em 3 camadas

```
CubeMaker3D/
├── backend/
│   ├── database.py   -> Camada de Dados (acesso ao SQLite)
│   ├── services.py   -> Camada de Lógica de Negócio (validações e regras)
│   └── app.py         -> Camada de Apresentação/API (rotas Flask)
├── frontend/
│   ├── index.html     -> Camada de Apresentação (interface do usuário)
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md
```

## Modelo de dados

- **Marca** (`id`, `nome`)
- **Cor** (`id`, `nome`)
- **Material** (`id`, `nome`)
- **Filamento** (`id`, `marca_id`, `cor_id`, `material_id`, `diametro_mm`,
  `peso_rolo_g`, `quantidade_rolos`)

`diametro_mm`, `peso_rolo_g` e `quantidade_rolos` guardam separadamente o
diâmetro do fio, o peso de cada rolo e quantos rolos existem em estoque —
essa granularidade é o que vai permitir, na próxima entrega, calcular o
consumo exato de filamento por peça impressa.

## Como rodar

1. Clone o repositório e entre na pasta:
   ```bash
   git clone <url-do-repositorio>
   cd filastock
   ```

2. (Recomendado) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Entre na pasta backend e rode a aplicação:
   ```bash
   cd backend
   python app.py
   ```

5. Acesse no navegador:
   ```
   http://localhost:5000
   ```

O banco (`backend/CubeMaker3D_Management.db`) é criado automaticamente na primeira
execução.

## Testando

1. Na aba **Marcas**, cadastre uma marca (ex: "Bambu Lab").
2. Na aba **Cores**, cadastre uma cor (ex: "Preto").
3. Na aba **Materiais**, cadastre um material (ex: "PLA").
4. Na aba **Filamentos**, cadastre um filamento combinando os três, mais
   diâmetro, peso do rolo e quantidade de rolos.
5. Tente excluir a marca, cor ou material usados no filamento — o sistema
   deve recusar, avisando que o registro está em uso.
6. Edite e exclua registros normalmente pelas ações "Editar"/"Excluir".
