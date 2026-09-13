const API = "/api";

// ---------- Abas ----------

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---------- Cadastros simples: Marcas, Cores, Materiais ----------

const RECURSOS_SIMPLES = ["marcas", "cores", "materiais"];

async function carregarSimples(recurso) {
  const res = await fetch(`${API}/${recurso}`);
  const itens = await res.json();

  const lista = document.querySelector(`[data-lista="${recurso}"]`);
  const vazio = document.querySelector(`[data-vazio="${recurso}"]`);
  lista.innerHTML = "";
  vazio.style.display = itens.length === 0 ? "block" : "none";

  itens.forEach(item => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${item.nome}</span>
      <span class="simple-item-actions">
        <button class="btn-text edit" data-recurso="${recurso}" data-id="${item.id}" data-nome="${item.nome}">Editar</button>
        <button class="btn-text remove" data-recurso="${recurso}" data-id="${item.id}">Excluir</button>
      </span>
    `;
    lista.appendChild(li);
  });

  return itens;
}

function mostrarMensagemSimples(recurso, texto, tipo) {
  const msg = document.querySelector(`[data-msg="${recurso}"]`);
  msg.textContent = texto;
  msg.className = `form-msg ${tipo}`;
}

document.querySelectorAll(".inline-form").forEach(form => {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const recurso = form.dataset.tabela;
    const nome = form.nome.value.trim();

    const res = await fetch(`${API}/${recurso}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome })
    });

    if (res.ok) {
      form.reset();
      mostrarMensagemSimples(recurso, "Adicionado com sucesso.", "success");
      carregarSimples(recurso);
      atualizarSelectsDeFilamento();
    } else {
      const corpo = await res.json();
      mostrarMensagemSimples(recurso, corpo.erro || "Erro ao cadastrar.", "error");
    }
  });
});

document.addEventListener("click", async (e) => {
  if (e.target.matches(".btn-text.edit") && RECURSOS_SIMPLES.includes(e.target.dataset.recurso)) {
    const { recurso, id, nome } = e.target.dataset;
    const novoNome = prompt("Editar nome:", nome);
    if (novoNome === null || novoNome.trim() === "") return;

    const res = await fetch(`${API}/${recurso}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome: novoNome.trim() })
    });

    if (res.ok) {
      carregarSimples(recurso);
      atualizarSelectsDeFilamento();
      carregarFilamentos();
    } else {
      const corpo = await res.json();
      alert(corpo.erro || "Erro ao editar.");
    }
  }

  if (e.target.matches(".btn-text.remove") && RECURSOS_SIMPLES.includes(e.target.dataset.recurso)) {
    const { recurso, id } = e.target.dataset;
    if (!confirm("Tem certeza que deseja excluir?")) return;

    const res = await fetch(`${API}/${recurso}/${id}`, { method: "DELETE" });
    if (res.ok) {
      carregarSimples(recurso);
      atualizarSelectsDeFilamento();
    } else {
      const corpo = await res.json();
      alert(corpo.erro || "Erro ao excluir.");
    }
  }
});

// ---------- Filamentos ----------

const formFilamento = document.getElementById("form-filamento");
const msgFilamento = document.getElementById("msg-filamento");
const selectMarca = document.getElementById("select-marca");
const selectCor = document.getElementById("select-cor");
const selectMaterial = document.getElementById("select-material");

let editandoFilamentoId = null;

async function preencherSelect(select, recurso, valorSelecionado) {
  const res = await fetch(`${API}/${recurso}`);
  const itens = await res.json();
  select.innerHTML = "";
  itens.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.id;
    opt.textContent = item.nome;
    if (valorSelecionado && Number(valorSelecionado) === item.id) opt.selected = true;
    select.appendChild(opt);
  });
}

async function atualizarSelectsDeFilamento() {
  await preencherSelect(selectMarca, "marcas");
  await preencherSelect(selectCor, "cores");
  await preencherSelect(selectMaterial, "materiais");
}

async function carregarFilamentos() {
  const res = await fetch(`${API}/filamentos`);
  const filamentos = await res.json();

  const tbody = document.querySelector("#tabela-filamentos tbody");
  const vazio = document.getElementById("vazio-filamentos");
  tbody.innerHTML = "";
  vazio.style.display = filamentos.length === 0 ? "block" : "none";

  filamentos.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="item-primary">${f.marca_nome} — ${f.cor_nome}</div>
        <div class="item-secondary">${f.material_nome}</div>
      </td>
      <td class="mono">${f.diametro_mm} mm</td>
      <td class="mono">${f.peso_rolo_g.toFixed(0)}g</td>
      <td>
        <span class="mono">${f.quantidade_rolos} rolo(s)</span>
        <div class="item-secondary">${f.peso_total_g.toFixed(0)}g no total</div>
      </td>
      <td>
        <button class="btn-text edit" data-tipo="filamento" data-id="${f.id}">Editar</button>
        <button class="btn-text remove" data-tipo="filamento" data-id="${f.id}">Excluir</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  return filamentos;
}

formFilamento.addEventListener("submit", async (e) => {
  e.preventDefault();
  const dados = Object.fromEntries(new FormData(formFilamento));
  dados.marca_id = parseInt(dados.marca_id);
  dados.cor_id = parseInt(dados.cor_id);
  dados.material_id = parseInt(dados.material_id);
  dados.diametro_mm = parseFloat(dados.diametro_mm);
  dados.peso_rolo_g = parseFloat(dados.peso_rolo_g);
  dados.quantidade_rolos = parseInt(dados.quantidade_rolos);

  const editando = editandoFilamentoId !== null;
  const url = editando ? `${API}/filamentos/${editandoFilamentoId}` : `${API}/filamentos`;
  const method = editando ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados)
  });

  if (res.ok) {
    msgFilamento.textContent = editando ? "Filamento atualizado." : "Filamento adicionado.";
    msgFilamento.className = "form-msg success";
    formFilamento.reset();
    sairDoModoEdicao();
    carregarFilamentos();
  } else {
    const corpo = await res.json();
    msgFilamento.textContent = corpo.erro || "Erro ao salvar.";
    msgFilamento.className = "form-msg error";
  }
});

function sairDoModoEdicao() {
  editandoFilamentoId = null;
  formFilamento.querySelector("button[type=submit]").textContent = "Adicionar filamento";
}

document.addEventListener("click", async (e) => {
  if (e.target.matches("[data-tipo=filamento].edit")) {
    const id = e.target.dataset.id;
    const res = await fetch(`${API}/filamentos`);
    const filamentos = await res.json();
    const f = filamentos.find(x => x.id === Number(id));
    if (!f) return;

    await atualizarSelectsDeFilamento();
    formFilamento.marca_id.value = f.marca_id;
    formFilamento.cor_id.value = f.cor_id;
    formFilamento.material_id.value = f.material_id;
    formFilamento.diametro_mm.value = f.diametro_mm.toFixed(2);
    formFilamento.peso_rolo_g.value = f.peso_rolo_g;
    formFilamento.quantidade_rolos.value = f.quantidade_rolos;

    editandoFilamentoId = f.id;
    formFilamento.querySelector("button[type=submit]").textContent = "Salvar alteração";
    document.querySelector('[data-tab="filamentos"]').click();
    formFilamento.scrollIntoView({ behavior: "smooth" });
  }

  if (e.target.matches("[data-tipo=filamento].remove")) {
    if (!confirm("Tem certeza que deseja excluir este filamento?")) return;
    await fetch(`${API}/filamentos/${e.target.dataset.id}`, { method: "DELETE" });
    carregarFilamentos();
  }
});

// ---------- Inicialização ----------

RECURSOS_SIMPLES.forEach(carregarSimples);
atualizarSelectsDeFilamento();
carregarFilamentos();
