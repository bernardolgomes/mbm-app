"""
Funções e dados partilhados entre todas as páginas da demo.
"""

import json
import re
from datetime import date
from pathlib import Path

import streamlit as st

NOME_NEGOCIO = "MBM"          # <- muda aqui o nome do teu negócio
TAGLINE = "Gestão de redes sociais para negócios locais"

# Palavra-passe de administrador, dá acesso a TODOS os clientes e ao seletor.
# Muda isto antes de partilhares a app com alguém.
SENHA_ADMIN = "mbm2026"

# ---------------------------------------------------------------------------
# CORES DE MARCA (fixas, usadas em títulos, botões e destaques em toda a app)
# Paleta inspirada em farmácia: creme + verde + turquesa
# ---------------------------------------------------------------------------
COR_FUNDO = "#F7F2E7"       # creme
COR_FUNDO_LATERAL = "#EFE7D3"  # creme mais escuro (sidebar)
COR_CARTAO = "#FFFFFF"      # branco
COR_TEXTO = "#26332B"       # verde-carvão (texto principal)
COR_MARCA = "#0F9D8C"       # turquesa (títulos, destaques)
COR_MARCA_VERDE = "#1E8A5F"  # verde farmácia (botões, CTA)

# ---------------------------------------------------------------------------
# ARMAZENAMENTO LOCAL (calendário, fotos e clientes adicionados por ti)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "dados_clientes"
DATA_DIR.mkdir(exist_ok=True)
FICHEIRO_CLIENTES_EXTRA = DATA_DIR / "clientes.json"


def _slug(texto: str) -> str:
    """Transforma um texto num nome de pasta seguro."""
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def cliente_dir(cliente: str) -> Path:
    d = DATA_DIR / _slug(cliente)
    d.mkdir(parents=True, exist_ok=True)
    return d


def carregar_calendario(cliente: str) -> dict:
    ficheiro = cliente_dir(cliente) / "calendario.json"
    if ficheiro.exists():
        return json.loads(ficheiro.read_text(encoding="utf-8"))
    return {}


def guardar_calendario(cliente: str, calendario: dict):
    ficheiro = cliente_dir(cliente) / "calendario.json"
    ficheiro.write_text(json.dumps(calendario, ensure_ascii=False, indent=2), encoding="utf-8")


def listar_fotos(cliente: str, categoria: str) -> list[Path]:
    """Lista as fotos guardadas dentro de uma categoria/legenda específica."""
    pasta = cliente_dir(cliente) / "fotos" / _slug(categoria)
    if not pasta.exists():
        return []
    return sorted(pasta.glob("*"))


def guardar_foto(cliente: str, categoria: str, nome_ficheiro: str, conteudo: bytes) -> Path:
    pasta = cliente_dir(cliente) / "fotos" / _slug(categoria)
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome_ficheiro
    destino.write_bytes(conteudo)
    return destino


def apagar_foto(caminho: Path):
    if caminho.exists():
        caminho.unlink()


# ---------------------------------------------------------------------------
# MOCKUPS / PORTEFÓLIO: exemplos de trabalhos reais, independentes de cliente
# ---------------------------------------------------------------------------
NEGOCIOS_MOCKUP = [
    ("💊", "Farmácia 1"),
    ("💊", "Farmácia 2"),
    ("🍽️", "Restaurante"),
    ("🏡", "Alojamento Local"),
    ("📚", "Centro de Estudos"),
    ("🏠", "Agência Imobiliária"),
]

_CHAVE_PORTEFOLIO = "_portefolio"


def listar_mockups(negocio: str) -> list[Path]:
    return listar_fotos(_CHAVE_PORTEFOLIO, negocio)


def guardar_mockup(negocio: str, nome_ficheiro: str, conteudo: bytes) -> Path:
    return guardar_foto(_CHAVE_PORTEFOLIO, negocio, nome_ficheiro, conteudo)


# ---------------------------------------------------------------------------
# CLIENTES: base fixa (exemplos) + clientes adicionados por ti (guardados em disco)
# ---------------------------------------------------------------------------
CLIENTES_BASE = {
    "GRCarvoeiro": {
        "cor": "#0E9488",
        "nicho": "Farmácia",
        "plano": "Plano Business",
        "desde": "Jul 2026",
        "posts_mes": 8,
        "stories_mes": 8,
        "real": True,
        "senha": "carvoeiro2026",
    },
}

NICHOS = ["Farmácia", "Restauração", "Ginásio", "Personal Trainer", "Clínica", "Outro"]

PLANOS = {
    "Plano Start": {"posts_mes": 2, "stories_mes": 2},
    "Plano Business": {"posts_mes": 8, "stories_mes": 8},
    "Plano Premium": {"posts_mes": 8, "stories_mes": 8},
}

# (hex, emoji de amostra, nome em português) — mostrado no seletor de cor do cliente
CORES_DISPONIVEIS = [
    ("#4FD1C5", "🟦", "Turquesa"),
    ("#F6AD55", "🟧", "Laranja"),
    ("#F56565", "🟥", "Vermelho"),
    ("#68D391", "🟩", "Verde"),
    ("#63B3ED", "🟦", "Azul"),
    ("#B794F4", "🟪", "Roxo"),
    ("#F687B3", "🩷", "Rosa"),
]


def carregar_clientes_extra() -> dict:
    if FICHEIRO_CLIENTES_EXTRA.exists():
        return json.loads(FICHEIRO_CLIENTES_EXTRA.read_text(encoding="utf-8"))
    return {}


def guardar_cliente_extra(nome: str, nicho: str, plano: str, desde: str, cor: str, senha: str):
    clientes = carregar_clientes_extra()
    clientes[nome] = {
        "cor": cor,
        "nicho": nicho,
        "plano": plano,
        "desde": desde,
        "posts_mes": PLANOS.get(plano, {}).get("posts_mes", 4),
        "stories_mes": PLANOS.get(plano, {}).get("stories_mes", 4),
        "senha": senha,
    }
    FICHEIRO_CLIENTES_EXTRA.write_text(json.dumps(clientes, ensure_ascii=False, indent=2), encoding="utf-8")


def remover_cliente_extra(nome: str):
    clientes = carregar_clientes_extra()
    if nome in clientes:
        del clientes[nome]
        FICHEIRO_CLIENTES_EXTRA.write_text(json.dumps(clientes, ensure_ascii=False, indent=2), encoding="utf-8")


def todos_clientes() -> dict:
    """Junta os clientes de exemplo com os que foram adicionados por ti."""
    return {**CLIENTES_BASE, **carregar_clientes_extra()}


def inject_css(accent: str):
    """accent = cor do cliente atual, usada só em pequenos detalhes (ícone, badge)."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COR_FUNDO};
            color: {COR_TEXTO};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {COR_FUNDO_LATERAL};
            border-right: 1px solid #ddd2af;
        }}
        section[data-testid="stSidebar"] *:not(.marca-nome) {{
            color: {COR_TEXTO} !important;
        }}
        .marca-nome {{
            color: {COR_MARCA_VERDE} !important;
        }}
        section[data-testid="stSidebar"] hr {{
            margin: 10px 0;
            border-color: #ddd2af;
        }}
        h1, h2, h3 {{
            font-family: Georgia, 'Times New Roman', serif;
            color: {COR_TEXTO};
        }}
        p, span, label, div {{
            color: {COR_TEXTO};
        }}
        .accent {{
            color: {COR_MARCA};
        }}
        .card {{
            background-color: {COR_CARTAO};
            color: {COR_TEXTO};
            border: 1px solid #e5ddc4;
            border-radius: 10px;
            padding: 22px 24px;
            margin-bottom: 16px;
        }}
        .card p, .card b, .card li {{
            color: {COR_TEXTO};
        }}
        .card .pill {{
            background-color: {COR_MARCA}1a;
            color: #0b6e62;
            border: 1px solid {COR_MARCA}55;
        }}
        .pill {{
            display: inline-block;
            background-color: {accent}22;
            color: {accent};
            border: 1px solid {accent}55;
            border-radius: 999px;
            padding: 3px 12px;
            font-size: 0.8rem;
            margin-right: 6px;
        }}
        .metric-big {{
            font-size: 2.1rem;
            font-weight: 700;
            color: {COR_MARCA};
        }}
        .stButton>button {{
            background-color: {COR_MARCA_VERDE};
            color: #ffffff;
            border: none;
            font-weight: 600;
        }}
        .sidebar-label {{
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #6b7a70;
            margin-bottom: 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def login_gate():
    """Mostra um ecrã de login antes de qualquer conteúdo da app.
    Palavra-passe de admin -> acesso a todos os clientes, com seletor.
    Palavra-passe de um cliente -> fica preso a esse cliente, sem seletor.
    Chamar em app.py, logo a seguir ao st.set_page_config."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.cliente_bloqueado = None

    if st.session_state.autenticado:
        return

    inject_css(COR_MARCA_VERDE)

    col_esq, col_meio, col_dir = st.columns([1, 1.2, 1])
    with col_meio:
        st.markdown(f"## {NOME_NEGOCIO}")
        st.caption(TAGLINE)
        st.markdown("")
        st.markdown("### Acesso")
        senha = st.text_input("Palavra-passe", type="password", key="login_senha")
        entrar = st.button("Entrar", use_container_width=True)

        if entrar:
            if senha == SENHA_ADMIN:
                st.session_state.autenticado = True
                st.session_state.cliente_bloqueado = None
                st.rerun()
            else:
                clientes = todos_clientes()
                encontrado = next(
                    (nome for nome, dados in clientes.items() if dados.get("senha") and senha == dados["senha"]),
                    None,
                )
                if encontrado:
                    st.session_state.autenticado = True
                    st.session_state.cliente_bloqueado = encontrado
                    st.session_state.cliente = encontrado
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta.")

    st.stop()


def render_marca_sidebar():
    """Mostra a missão/tagline em destaque no topo da sidebar, acima da navegação
    (estilo 'MONEY · MINDSET · FREEDOM'). Chamar em app.py, ANTES de st.navigation(...)."""
    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background-color: {COR_FUNDO_LATERAL};
        }}
        </style>
        <div style="padding:0.5rem 1rem 0 1rem;">
            <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;
                        text-transform:uppercase;color:{COR_TEXTO};line-height:1.4;margin-bottom:10px;">
                {TAGLINE}
            </div>
            <hr style="margin:0 0 8px 0;border-color:#ddd2af;">
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_marca_pagina(accent: str):
    """Mostra o logótipo/nome da marca no topo de cada página de conteúdo
    (estilo o cabeçalho 'Freenomics' antes do título de cada página)."""
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="width:32px;height:32px;border-radius:8px;background:{COR_MARCA_VERDE};
                        display:flex;align-items:center;justify-content:center;font-size:16px;">
                📱
            </div>
            <span class="marca-nome" style="font-size:1.1rem;font-weight:800;color:{COR_MARCA_VERDE};">
                {NOME_NEGOCIO}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def garantir_cliente_valido():
    """Garante que existe sempre um cliente válido em session_state. Chamar cedo em cada rerun."""
    clientes = todos_clientes()
    bloqueado = st.session_state.get("cliente_bloqueado")
    if "cliente" not in st.session_state or st.session_state.cliente not in clientes:
        st.session_state.cliente = bloqueado or list(clientes.keys())[0]


def render_cliente_selector():
    """Mostra o seletor de cliente (ou o cliente fixo, se for acesso de cliente).
    Chamar em app.py, dentro de 'with st.sidebar:', no sítio exato onde deve aparecer."""
    clientes = todos_clientes()
    bloqueado = st.session_state.get("cliente_bloqueado")
    garantir_cliente_valido()

    if bloqueado:
        # Acesso de cliente: fica preso ao seu próprio cliente, sem ver os outros.
        st.markdown('<div class="sidebar-label">A ver</div>', unsafe_allow_html=True)
        st.markdown(f"**{bloqueado}**")
        return

    # Acesso de admin: pode trocar de cliente e gerir a lista.
    st.markdown('<div class="sidebar-label">Cliente selecionado</div>', unsafe_allow_html=True)
    nomes = list(clientes.keys())
    cliente_sel = st.selectbox(
        "Cliente",
        nomes,
        index=nomes.index(st.session_state.cliente),
        label_visibility="collapsed",
    )
    st.session_state.cliente = cliente_sel

    st.markdown("---")

    with st.expander("➕ Adicionar novo cliente"):
        with st.form("form_novo_cliente", clear_on_submit=True):
            novo_nome = st.text_input("Nome do cliente")
            novo_nicho = st.selectbox("Nicho", NICHOS)
            novo_plano = st.selectbox("Plano escolhido", list(PLANOS.keys()))
            nova_data = st.date_input("Cliente desde", value=date.today())
            nova_cor_opcao = st.selectbox(
                "Cor de identificação",
                CORES_DISPONIVEIS,
                format_func=lambda opcao: f"{opcao[1]} {opcao[2]}",
            )
            nova_senha = st.text_input("Palavra-passe de acesso do cliente")
            submeter = st.form_submit_button("Adicionar cliente")

            if submeter:
                if not novo_nome.strip():
                    st.warning("Indica o nome do cliente.")
                elif novo_nome in clientes:
                    st.warning("Já existe um cliente com esse nome.")
                elif not nova_senha.strip():
                    st.warning("Define uma palavra-passe para este cliente.")
                else:
                    guardar_cliente_extra(
                        nome=novo_nome.strip(),
                        nicho=novo_nicho,
                        plano=novo_plano,
                        desde=nova_data.strftime("%b %Y"),
                        cor=nova_cor_opcao[0],
                        senha=nova_senha.strip(),
                    )
                    st.session_state.cliente = novo_nome.strip()
                    st.rerun()

    if cliente_sel not in CLIENTES_BASE:
        if st.button("🗑️ Remover este cliente"):
            remover_cliente_extra(cliente_sel)
            st.session_state.cliente = list(CLIENTES_BASE.keys())[0]
            st.rerun()


def render_sair_button():
    """Botão de logout. Chamar em app.py, dentro de 'with st.sidebar:'."""
    if st.button("🚪 Sair"):
        st.session_state.autenticado = False
        st.session_state.cliente_bloqueado = None
        st.rerun()


def render_header(cliente: str, dados: dict, accent: str):
    """Nota técnica: isto é construído numa única linha de propósito. Se houver uma
    linha em branco a meio de um bloco de HTML dentro de um st.markdown, o Streamlit
    interpreta o resto como texto em bruto em vez de HTML (acontecia quando o cliente
    não tinha o selo "Cliente real", porque essa linha ficava vazia)."""
    selo_real = (
        '<span class="pill" style="background:#f6ad5522;color:#f6ad55;border-color:#f6ad5555;">⭐ Cliente real</span>'
        if dados.get("real")
        else ""
    )
    linha_info = (
        f'<span class="pill">{dados["nicho"]}</span>'
        f'<span class="pill">{dados["plano"]}</span>'
        f'{selo_real}'
        f'<span style="color:#7c8aa8;font-size:0.85rem;"> cliente desde {dados["desde"]}</span>'
    )
    html = (
        '<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">'
        f'<div style="width:40px;height:40px;border-radius:10px;background:{accent};'
        'display:flex;align-items:center;justify-content:center;font-size:20px;">📱</div>'
        '<div>'
        f'<span style="font-size:1.3rem;font-weight:700;">{cliente}</span><br/>'
        f'{linha_info}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("---")


def setup_page(page_title: str, mostrar_cliente: bool = True) -> tuple[str, dict, str]:
    """Chamar no topo de cada página: configura CSS e header. Devolve (cliente, dados, accent).
    O seletor de cliente é desenhado à parte, em app.py.

    mostrar_cliente=False -> página geral, não ligada a nenhum cliente em concreto
    (não mostra a barra com nome/nicho/plano/cliente desde), usa a cor de marca fixa."""
    garantir_cliente_valido()
    cliente = st.session_state.cliente
    dados = todos_clientes()[cliente]

    if mostrar_cliente:
        accent = dados["cor"]
        inject_css(accent)
        render_marca_pagina(accent)
        render_header(cliente, dados, accent)
    else:
        accent = COR_MARCA_VERDE
        inject_css(accent)
        render_marca_pagina(accent)

    return cliente, dados, accent
