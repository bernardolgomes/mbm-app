"""
Funções e dados partilhados entre todas as páginas da demo.
"""

import json
import os
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
# ESTATÍSTICAS: análise própria e independente, guardada mês a mês por cliente.
# Introduzida manualmente (admin), não depende de nenhuma API externa.
# ---------------------------------------------------------------------------
INDICADORES = [
    ("seguidores", "Total de seguidores", "{:,.0f}"),
    ("alcance", "Alcance mensal", "{:,.0f}"),
    ("impressoes", "Impressões", "{:,.0f}"),
    ("engagement", "Taxa de engagement (%)", "{:.1f}%"),
    ("novos_seguidores", "Novos seguidores", "{:,.0f}"),
    ("visitas_perfil", "Visitas ao perfil", "{:,.0f}"),
    ("cliques_link", "Cliques no link da bio", "{:,.0f}"),
    ("mensagens", "Mensagens/contactos recebidos", "{:,.0f}"),
]

# Indicadores que são sempre número inteiro (sem casas decimais nem percentagem
# nos campos de introdução/edição). Só a taxa de engagement fica com 1 casa decimal.
INDICADORES_INTEIROS = {
    "seguidores", "alcance", "impressoes", "novos_seguidores",
    "visitas_perfil", "cliques_link", "mensagens",
}


def carregar_estatisticas(cliente: str) -> dict:
    """Devolve {"AAAA-MM": {indicador: valor, ...}, ...} guardado para este cliente."""
    ficheiro = cliente_dir(cliente) / "estatisticas.json"
    if ficheiro.exists():
        return json.loads(ficheiro.read_text(encoding="utf-8"))
    return {}


def guardar_estatisticas(cliente: str, historico: dict):
    ficheiro = cliente_dir(cliente) / "estatisticas.json"
    ficheiro.write_text(json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8")


def e_admin() -> bool:
    """True só quando a sessão iniciada é de administração (não é acesso de cliente).
    Usar para ações reservadas à administração, como exportar relatórios em PDF."""
    return bool(st.session_state.get("autenticado")) and not st.session_state.get("cliente_bloqueado")


def _insight_basico(atual: dict, anterior: dict | None) -> str:
    """Leitura automática simples, sem IA, baseada na variação face ao mês anterior."""
    if not anterior:
        return (
            "Este é o primeiro mês com dados registados para este cliente. A partir do "
            "próximo mês vais poder ver a evolução face a este ponto de partida."
        )
    partes = []
    for chave, label, _ in INDICADORES:
        v_atual = atual.get(chave)
        v_ant = anterior.get(chave)
        if v_atual is None or v_ant is None or v_ant == 0:
            continue
        variacao = (v_atual - v_ant) / v_ant * 100
        if variacao > 0.5:
            tendencia = f"subiu {variacao:.1f}%"
        elif variacao < -0.5:
            tendencia = f"desceu {abs(variacao):.1f}%"
        else:
            tendencia = "manteve-se estável"
        partes.append(f"{label} {tendencia}")
    if not partes:
        return "Ainda não há dados suficientes para comparar com o mês anterior."
    return "; ".join(partes) + "."


def gerar_insights(cliente: str, historico: dict) -> str:
    """Gera uma leitura dos resultados do cliente. Usa a API da Anthropic se houver
    uma chave configurada (st.secrets['ANTHROPIC_API_KEY'] ou variável de ambiente
    ANTHROPIC_API_KEY); caso contrário, devolve uma leitura automática simples,
    baseada apenas nas variações percentuais entre meses."""
    meses = sorted(historico.keys())
    if not meses:
        return "Ainda não há dados suficientes para gerar uma análise."

    atual = historico[meses[-1]]
    anterior = historico[meses[-2]] if len(meses) >= 2 else None

    chave_api = os.environ.get("ANTHROPIC_API_KEY")
    if not chave_api:
        try:
            chave_api = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            chave_api = None

    if not chave_api:
        return _insight_basico(atual, anterior)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=chave_api)
        resumo_dados = f"Cliente: {cliente}\nDados mensais (mês -> indicadores): {json.dumps(historico, ensure_ascii=False)}"
        resposta = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "És um analista de redes sociais de uma agência de gestão de redes sociais "
                        "para negócios locais. Analisa os dados mensais abaixo de um cliente e escreve "
                        "uma leitura curta (máximo 120 palavras) em português de Portugal, destacando "
                        "tendências, o que correu bem e uma sugestão concreta de melhoria para o próximo mês.\n\n"
                        "Escreve em texto corrido, dividido em 3 parágrafos curtos com uma linha em branco "
                        "entre eles, cada um a começar por um rótulo simples seguido de dois pontos: "
                        "'Tendências:', 'Pontos positivos:' e 'Sugestão de melhoria:'. "
                        "NÃO uses markdown (nada de #, **, -, *, listas ou títulos), só texto simples.\n\n"
                        + resumo_dados
                    ),
                }
            ],
        )
        return _limpar_markdown(resposta.content[0].text.strip())
    except Exception as e:
        return f"(Não foi possível gerar a análise com IA, mostrando leitura automática. Detalhe: {e})\n\n" + _insight_basico(atual, anterior)


def _limpar_markdown(texto: str) -> str:
    """Remove símbolos de markdown que a IA às vezes usa (#, **, -, *), para o texto
    poder ser mostrado tal e qual, tanto no cartão HTML como no PDF."""
    texto = re.sub(r"^#{1,6}\s*", "", texto, flags=re.MULTILINE)
    texto = texto.replace("**", "").replace("__", "")
    texto = re.sub(r"^[\-\*•]\s+", "", texto, flags=re.MULTILINE)
    return texto.strip()


def insight_para_html(texto: str) -> str:
    """Converte o texto de insights (com rótulos tipo 'Tendências:') em HTML simples,
    com o rótulo a bold, para mostrar dentro de um cartão da app."""
    import html as html_lib

    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    partes_html = []
    for p in paragrafos:
        linhas = p.split("\n")
        primeira = linhas[0]
        m = re.match(r"^([^:]{2,40}:)\s*(.*)$", primeira)
        if m:
            rotulo, resto = m.groups()
            resto_completo = " ".join([resto] + linhas[1:]).strip()
            partes_html.append(
                f"<p><b>{html_lib.escape(rotulo)}</b> {html_lib.escape(resto_completo)}</p>"
            )
        else:
            partes_html.append(f"<p>{html_lib.escape(p).replace(chr(10), '<br>')}</p>")
    return "".join(partes_html)


def gerar_pdf_relatorio(cliente: str, dados_cliente: dict, historico: dict, insight_texto: str, mes_calendario: dict | None = None) -> bytes:
    """Gera o PDF do relatório mensal deste cliente: indicadores, gráfico de evolução,
    publicações do mês (via calendário) e a análise/insights. Só deve ser chamado a
    partir de uma sessão de administração (ver e_admin())."""
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from fpdf import FPDF

    meses = sorted(historico.keys())
    ultimo = meses[-1]
    anterior = meses[-2] if len(meses) >= 2 else None
    dados_ultimo = historico[ultimo]
    dados_anterior = historico[anterior] if anterior else None

    # Gráfico de evolução de seguidores ao longo dos meses.
    fig, ax = plt.subplots(figsize=(6.4, 3))
    seguidores = [historico[m].get("seguidores", 0) for m in meses]
    ax.plot(meses, seguidores, marker="o", color="#1E8A5F")
    ax.set_ylabel("Seguidores")
    ax.set_xlabel("Mês")
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)

    VERDE = (30, 138, 95)
    TURQUESA = (15, 120, 105)
    TEXTO_ESCURO = (38, 45, 40)
    CINZA = (110, 110, 110)
    FUNDO_CARTAO = (247, 242, 231)

    def _l1(txt: str) -> str:
        """Garante que o texto é seguro para o PDF (latin-1), sem perder acentos comuns."""
        return txt.encode("latin-1", "replace").decode("latin-1")

    def _titulo_secao(texto: str):
        pdf.ln(2)
        pdf.set_text_color(*TURQUESA)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, _l1(texto), ln=True)
        pdf.set_draw_color(*TURQUESA)
        pdf.set_line_width(0.6)
        y = pdf.get_y()
        pdf.line(pdf.l_margin, y, pdf.l_margin + 40, y)
        pdf.ln(3)
        pdf.set_text_color(*TEXTO_ESCURO)

    def _cartao(altura: float):
        x, y = pdf.l_margin, pdf.get_y()
        largura = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_fill_color(*FUNDO_CARTAO)
        pdf.rect(x, y, largura, altura, style="F")
        pdf.set_xy(x + 4, y + 3)

    pdf = FPDF()
    pdf.add_page()

    # Cabeçalho com barra de cor de marca.
    pdf.set_fill_color(*VERDE)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_xy(pdf.l_margin, 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "MBM  |  Relatorio mensal", ln=True)
    pdf.set_xy(pdf.l_margin, 19)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, _l1(f"{cliente}  -  {ultimo}"), ln=True)

    pdf.set_xy(pdf.l_margin, 36)
    pdf.set_text_color(*CINZA)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0, 7,
        _l1(
            f"Plano: {dados_cliente.get('plano', '-')}   |   Nicho: {dados_cliente.get('nicho', '-')}   |   "
            f"Cliente desde: {dados_cliente.get('desde', '-')}"
        ),
        ln=True,
    )
    pdf.ln(2)

    # Indicadores do mês, dentro de um cartão com fundo creme.
    _titulo_secao("Indicadores do mes")
    altura_cartao = 7 * len(INDICADORES) + 6
    _cartao(altura_cartao)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*TEXTO_ESCURO)
    for chave, label, fmt in INDICADORES:
        v_atual = dados_ultimo.get(chave)
        v_ant = dados_anterior.get(chave) if dados_anterior else None
        linha = f"{label}: {fmt.format(v_atual) if v_atual is not None else '-'}"
        if v_atual is not None and v_ant not in (None, 0):
            variacao = (v_atual - v_ant) / v_ant * 100
            linha += f"   ({'+' if variacao >= 0 else ''}{variacao:.1f}% vs mes anterior)"
        pdf.set_x(pdf.l_margin + 4)
        pdf.cell(0, 7, _l1(linha), ln=True)
    pdf.ln(6)

    # Gráfico de evolução.
    _titulo_secao("Evolucao de seguidores")
    pdf.image(buf, w=170)
    pdf.ln(4)

    # Publicações do mês (a partir do calendário).
    if mes_calendario:
        contagem: dict[str, int] = {}
        for tipo in mes_calendario.values():
            if tipo and tipo != "—":
                contagem[_l1(tipo)] = contagem.get(_l1(tipo), 0) + 1
        _titulo_secao("Publicacoes do mes")
        pdf.set_font("Helvetica", "", 10)
        if contagem:
            for tipo, n in contagem.items():
                pdf.cell(0, 7, f"{tipo}: {n}", ln=True)
        else:
            pdf.cell(0, 7, "Sem publicacoes registadas no calendario este mes.", ln=True)
        pdf.ln(2)

    # Análise e insights, com rótulos a bold.
    _titulo_secao("Analise e insights")
    texto_seguro = _l1(insight_texto)
    paragrafos = [p.strip() for p in texto_seguro.split("\n\n") if p.strip()]
    if not paragrafos:
        paragrafos = [texto_seguro]
    for p in paragrafos:
        linhas = p.split("\n")
        primeira = linhas[0]
        m = re.match(r"^([^:]{2,40}:)\s*(.*)$", primeira)
        if m:
            rotulo, resto = m.groups()
            resto_completo = " ".join([resto] + linhas[1:]).strip()
            pdf.set_font("Helvetica", "B", 10)
            pdf.write(6, rotulo + " ")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, resto_completo)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, p)
        pdf.ln(2)

    return bytes(pdf.output())


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
        "plano": "Business",
        "desde": "Jul 2026",
        "posts_mes": 4,
        "stories_mes": 4,
        "real": True,
        "senha": "carvoeiro2026",
    },
}

NICHOS = ["Farmácia", "Restauração", "Ginásio", "Personal Trainer", "Clínica", "Outro"]

PLANOS = {
    "Starter / Basic": {"posts_mes": 2, "stories_mes": 2},
    "Business": {"posts_mes": 4, "stories_mes": 4},
    "Premium": {"posts_mes": 6, "stories_mes": 6},
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
    """Garante que existe estado de sessão para autenticação, sem bloquear a app.
    Qualquer pessoa com o link pode ver tudo em modo visitante (só leitura);
    para editar (calendário, fotos, gerir clientes) é preciso iniciar sessão.
    Chamar em app.py, logo a seguir ao st.set_page_config."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.cliente_bloqueado = None


def pode_editar() -> bool:
    """True se houver sessão iniciada (admin ou cliente). Usar para mostrar/esconder
    ações de edição (calendário, upload/remoção de fotos, gestão de clientes)."""
    return bool(st.session_state.get("autenticado", False))


def _tentar_login(senha: str) -> bool:
    """Valida a palavra-passe introduzida e atualiza o estado de sessão. Devolve True se entrou."""
    if senha == SENHA_ADMIN:
        st.session_state.autenticado = True
        st.session_state.cliente_bloqueado = None
        return True
    clientes = todos_clientes()
    encontrado = next(
        (nome for nome, dados in clientes.items() if dados.get("senha") and senha == dados["senha"]),
        None,
    )
    if encontrado:
        st.session_state.autenticado = True
        st.session_state.cliente_bloqueado = encontrado
        st.session_state.cliente = encontrado
        return True
    return False


def render_login(contexto: str = "sidebar"):
    """Mostra o estado de sessão (visitante / com sessão iniciada) e o formulário de
    login/logout. Pode ser chamado em mais do que um sítio (sidebar e página inicial),
    o parâmetro 'contexto' só serve para gerar chaves de widget únicas."""
    if st.session_state.get("autenticado"):
        quem = st.session_state.get("cliente_bloqueado") or "Administração"
        st.markdown(f"🔓 Sessão iniciada: **{quem}**")
        if st.button("🚪 Sair", key=f"sair-{contexto}", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.cliente_bloqueado = None
            st.rerun()
    else:
        with st.expander("🔐 Entrar (clientes e administração)"):
            senha = st.text_input(
                "Palavra-passe",
                type="password",
                key=f"login-senha-{contexto}",
                placeholder="Introduz a tua palavra-passe",
            )
            if st.button("Entrar", key=f"login-btn-{contexto}", use_container_width=True):
                if _tentar_login(senha):
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta.")


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
    """Mostra o seletor de cliente (ou o cliente fixo, se for acesso de cliente ou visitante).
    Chamar em app.py, dentro de 'with st.sidebar:', no sítio exato onde deve aparecer."""
    clientes = todos_clientes()
    bloqueado = st.session_state.get("cliente_bloqueado")
    garantir_cliente_valido()

    if not pode_editar():
        # Visitante sem sessão: só vê o cliente de demonstração, em modo leitura.
        demo_cliente = next(
            (nome for nome, dados in CLIENTES_BASE.items() if dados.get("real")),
            list(CLIENTES_BASE.keys())[0],
        )
        st.session_state.cliente = demo_cliente
        st.markdown('<div class="sidebar-label">A ver (demonstração)</div>', unsafe_allow_html=True)
        st.markdown(f"**{demo_cliente}**")
        st.caption("Inicia sessão para ver a área de um cliente específico.")
        return

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
