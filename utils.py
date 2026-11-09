"""
Funções e dados partilhados entre todas as páginas da demo.
"""

import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

NOME_NEGOCIO = "MBM"          # <- muda aqui o nome do teu negócio
TAGLINE = "Gestão de redes sociais para negócios locais"

# Palavra-passe de administrador, dá acesso a TODOS os clientes e ao seletor.
# Muda isto antes de partilhares a app com alguém.
SENHA_ADMIN = "mbm2026"

# ---------------------------------------------------------------------------
# CORES DE MARCA (fixas, usadas em títulos, botões e destaques em toda a app)
# Paleta alinhada com o logótipo da MBM: fundo claro/neutro, texto azul-marinho
# escuro, e destaques no gradiente rosa-magenta -> roxo do logo.
# ---------------------------------------------------------------------------
COR_FUNDO = "#F4F3F1"        # cinza muito claro (fundo do logo)
COR_FUNDO_LATERAL = "#ECEAE6"  # tom um pouco mais escuro (sidebar)
COR_CARTAO = "#FFFFFF"       # branco
COR_TEXTO = "#12172B"        # azul-marinho escuro (texto principal, letras "M" do logo)
COR_MARCA = "#7B3FF2"        # roxo do logo (títulos, destaques secundários)
COR_MARCA_VERDE = "#E91E8C"  # rosa-magenta do logo (nome da marca, destaques fortes)
COR_BOTAO_DE = "#E91E8C"     # início do gradiente dos botões (rosa-magenta)
COR_BOTAO_PARA = "#7B3FF2"   # fim do gradiente dos botões (roxo)
COR_BOTAO_HOVER_DE = "#C81577"  # gradiente do hover, mais escuro
COR_BOTAO_HOVER_PARA = "#6425D9"
COR_BOTAO = f"linear-gradient(90deg, {COR_BOTAO_DE}, {COR_BOTAO_PARA})"
COR_BOTAO_HOVER = f"linear-gradient(90deg, {COR_BOTAO_HOVER_DE}, {COR_BOTAO_HOVER_PARA})"

# ---------------------------------------------------------------------------
# ARMAZENAMENTO LOCAL (calendário, fotos e clientes adicionados por ti)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "dados_clientes"
DATA_DIR.mkdir(exist_ok=True)
FICHEIRO_CLIENTES_EXTRA = DATA_DIR / "clientes.json"

# ---------------------------------------------------------------------------
# LOGÓTIPO
# ---------------------------------------------------------------------------
PASTA_ASSETS = Path(__file__).parent / "assets"


def _encontrar_logo() -> Path | None:
    """Procura o ficheiro do logo na pasta assets/, seja qual for a extensão
    (jpg, jpeg ou png), para não voltar a partir se o ficheiro for substituído
    com um nome ligeiramente diferente."""
    if not PASTA_ASSETS.exists():
        return None
    for extensao in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        candidato = PASTA_ASSETS / f"logo.{extensao}"
        if candidato.exists():
            return candidato
    return None


@st.cache_data
def _logo_base64() -> str | None:
    """Devolve o logótipo em base64 (para embutir em HTML), ou None se ainda não existir."""
    ficheiro = _encontrar_logo()
    if not ficheiro:
        return None
    import base64

    tipo = "jpeg" if ficheiro.suffix.lower() in (".jpg", ".jpeg") else "png"
    conteudo = base64.b64encode(ficheiro.read_bytes()).decode("utf-8")
    return f"data:image/{tipo};base64,{conteudo}"


@st.cache_data
def _foto_fundador_base64() -> str | None:
    """Foto do fundador (assets/bernardo.jpg, .jpeg, .png ou .webp), reduzida para
    não pesar na página. Devolve None se o ficheiro ainda não existir."""
    if not PASTA_ASSETS.exists():
        return None
    for extensao in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG"):
        ficheiro = PASTA_ASSETS / f"bernardo.{extensao}"
        if ficheiro.exists():
            import base64
            import io

            from PIL import Image

            img = Image.open(ficheiro).convert("RGB")
            img.thumbnail((500, 500))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=88)
            return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
    return None


def avatar_fundador_html(tamanho: int = 120) -> str:
    """HTML (numa só linha) do círculo com a foto do fundador; se ainda não houver
    foto, mostra as iniciais 'BG' sobre o gradiente da marca."""
    foto = _foto_fundador_base64()
    if foto:
        return (
            f'<img src="{foto}" style="width:{tamanho}px;height:{tamanho}px;border-radius:50%;'
            'object-fit:cover;object-position:center 20%;flex-shrink:0;border:3px solid #ffffff;'
            'box-shadow:0 4px 14px rgba(18,23,43,0.18);" />'
        )
    return (
        f'<div style="width:{tamanho}px;height:{tamanho}px;border-radius:50%;'
        'background:linear-gradient(135deg,#E91E8C,#7B3FF2);display:flex;align-items:center;'
        f'justify-content:center;font-size:{int(tamanho * 0.3)}px;color:white;flex-shrink:0;">BG</div>'
    )


# ---------------------------------------------------------------------------
# CLIENTE FICTÍCIO DE DEMONSTRAÇÃO: é o que os visitantes veem. Os dados são
# gerados aqui (não vêm do disco), por isso nunca se perdem nem expõem um cliente real.
# ---------------------------------------------------------------------------
DEMO_CLIENTE = "Farmácia Exemplo"


def _e_demo(cliente: str) -> bool:
    return cliente == DEMO_CLIENTE


def _mes_atras(n: int) -> str:
    hoje = date.today()
    ano, mes = hoje.year, hoje.month - n
    while mes <= 0:
        mes += 12
        ano -= 1
    return f"{ano:04d}-{mes:02d}"


def _estatisticas_demo() -> dict:
    """6 meses fictícios (até ao mês passado), com uma evolução positiva realista."""
    dados = {}
    for i, n in enumerate(range(6, 0, -1)):
        dados[_mes_atras(n)] = {
            "seguidores": 820 + i * 52 + (i % 2) * 6,
            "alcance": 2400 + i * 430 + (i % 3) * 120,
            "impressoes": 4100 + i * 700 + (i % 2) * 200,
            "engagement": round(2.4 + i * 0.35 - (i % 2) * 0.1, 1),
            "novos_seguidores": 18 + i * 9 + (i % 2) * 4,
            "visitas_perfil": 150 + i * 28,
            "cliques_link": 22 + i * 7,
            "mensagens": 4 + i * 2,
        }
    return dados


def _calendario_demo() -> dict:
    """Calendário fictício: post à terça, story à quinta (plano Business, 4+4 por mês)."""
    cal = {}
    d = date.today() - timedelta(days=180)
    fim = date.today() + timedelta(days=90)
    n_tercas = 0
    while d <= fim:
        if d.weekday() == 1:
            n_tercas += 1
            if n_tercas % 4 == 0:
                cal[d.isoformat()] = "🎉 Promoção"
            elif n_tercas % 3 == 0:
                cal[d.isoformat()] = "🎬 Reel"
            else:
                cal[d.isoformat()] = "📸 Post"
        elif d.weekday() == 3:
            cal[d.isoformat()] = "📝 Story"
        d += timedelta(days=1)
    return cal


def _fotos_demo(categoria: str) -> list[Path]:
    """O cliente de demonstração não mostra fotos nos Exemplos de Posts."""
    return []


def _slug(texto: str) -> str:
    """Transforma um texto num nome de pasta seguro."""
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def cliente_dir(cliente: str) -> Path:
    d = DATA_DIR / _slug(cliente)
    d.mkdir(parents=True, exist_ok=True)
    return d


def carregar_calendario(cliente: str) -> dict:
    if _e_demo(cliente):
        return _calendario_demo()
    ficheiro = cliente_dir(cliente) / "calendario.json"
    if ficheiro.exists():
        return json.loads(ficheiro.read_text(encoding="utf-8"))
    return {}


def guardar_calendario(cliente: str, calendario: dict):
    if _e_demo(cliente):
        return  # o cliente de demonstração é só de leitura
    ficheiro = cliente_dir(cliente) / "calendario.json"
    ficheiro.write_text(json.dumps(calendario, ensure_ascii=False, indent=2), encoding="utf-8")


def listar_fotos(cliente: str, categoria: str) -> list[Path]:
    """Lista as fotos guardadas dentro de uma categoria/legenda específica."""
    if _e_demo(cliente):
        return _fotos_demo(categoria)
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
    if _e_demo(cliente):
        return _estatisticas_demo()
    ficheiro = cliente_dir(cliente) / "estatisticas.json"
    if ficheiro.exists():
        return json.loads(ficheiro.read_text(encoding="utf-8"))
    return {}


def guardar_estatisticas(cliente: str, historico: dict):
    if _e_demo(cliente):
        return  # o cliente de demonstração é só de leitura
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
    ax.plot(meses, seguidores, marker="o", color="#E91E8C")
    ax.set_ylabel("Seguidores")
    ax.set_xlabel("Mês")
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)

    VERDE = (123, 63, 242)       # roxo do logo (cabeçalho do PDF)
    TURQUESA = (123, 63, 242)    # roxo do logo (títulos de secção)
    TEXTO_ESCURO = (18, 23, 43)  # azul-marinho escuro (texto principal)
    CINZA = (110, 110, 110)
    FUNDO_CARTAO = (244, 243, 241)

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
    DEMO_CLIENTE: {
        "cor": "#7B3FF2",
        "nicho": "Farmácia",
        "plano": "Business",
        "desde": "Jan 2026",
        "posts_mes": 4,
        "stories_mes": 4,
        "demo": True,
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
            background: linear-gradient(90deg, {COR_BOTAO_DE}, {COR_BOTAO_PARA}) !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            color: transparent !important;
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
        .stButton>button,
        div[data-testid="stLinkButton"] a,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stFormSubmitButton"] button {{
            background: {COR_BOTAO} !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 600 !important;
        }}
        .stButton>button *,
        div[data-testid="stLinkButton"] a *,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stFormSubmitButton"] button * {{
            background: transparent !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }}
        .stButton>button:hover,
        div[data-testid="stLinkButton"] a:hover,
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {{
            background: {COR_BOTAO_HOVER} !important;
            color: #ffffff !important;
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
    login/logout, dentro de uma caixa verde de marca com texto a branco. Pode ser
    chamado em mais do que um sítio (sidebar e página inicial), o parâmetro 'contexto'
    só serve para gerar chaves de widget/CSS únicas."""
    chave_container = f"login_caixa_{contexto}"
    chave_aberto = f"mostrar_login_{contexto}"
    autenticado = bool(st.session_state.get("autenticado"))

    # Antes de haver sessão iniciada e antes de a caixa estar aberta, mostra só um
    # botão simples para não ocupar espaço com o formulário sempre visível.
    if not autenticado and not st.session_state.get(chave_aberto):
        if st.button("🔐 Entrar (clientes e administração)", key=f"abrir-{contexto}", use_container_width=True):
            st.session_state[chave_aberto] = True
            st.rerun()
        return

    with st.container(key=chave_container):
        st.markdown(
            f"""
            <style>
            div.st-key-{chave_container} {{
                background: {COR_BOTAO};
                border-radius: 10px;
                padding: 14px 16px 6px 16px;
            }}
            div.st-key-{chave_container} * {{
                color: #ffffff !important;
            }}
            div.st-key-{chave_container} input {{
                color: {COR_TEXTO} !important;
                background-color: #ffffff !important;
            }}
            div.st-key-{chave_container} [data-testid="stAlertContainer"] * {{
                color: inherit !important;
            }}
            div.st-key-{chave_container} .stButton>button,
            div.st-key-{chave_container} .stButton>button * {{
                background-color: #ffffff !important;
                color: {COR_MARCA_VERDE} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        if autenticado:
            quem = st.session_state.get("cliente_bloqueado") or "Administração"
            st.markdown(f"🔓 Sessão iniciada: **{quem}**")
            if st.button("🚪 Sair", key=f"sair-{contexto}", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.cliente_bloqueado = None
                st.session_state[chave_aberto] = False
                st.rerun()
        else:
            st.markdown("**🔐 Entrar (clientes e administração)**")
            senha = st.text_input(
                "Palavra-passe",
                type="password",
                key=f"login-senha-{contexto}",
                placeholder="Introduz a tua palavra-passe",
                label_visibility="collapsed",
            )
            col_entrar, col_cancelar = st.columns(2)
            with col_entrar:
                if st.button("Entrar", key=f"login-btn-{contexto}", use_container_width=True):
                    if _tentar_login(senha):
                        st.session_state[chave_aberto] = False
                        st.rerun()
                    else:
                        st.error("Palavra-passe incorreta.")
            with col_cancelar:
                if st.button("Cancelar", key=f"cancelar-{contexto}", use_container_width=True):
                    st.session_state[chave_aberto] = False
                    st.rerun()


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
    logo = _logo_base64()
    if logo:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
                <img src="{logo}" style="height:92px;width:auto;" />
                <span class="marca-nome" style="font-size:1.5rem;font-weight:800;">
                    MBMarketing Digital
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
                <div style="width:32px;height:32px;border-radius:8px;background:{COR_MARCA_VERDE};
                            display:flex;align-items:center;justify-content:center;font-size:16px;">
                    📱
                </div>
                <span class="marca-nome" style="font-size:1.1rem;font-weight:800;">
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
    if not pode_editar():
        # Visitantes só veem o cliente fictício de demonstração.
        st.session_state.cliente = DEMO_CLIENTE
        return
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
        demo_cliente = DEMO_CLIENTE
        st.session_state.cliente = demo_cliente
        st.markdown('<div class="sidebar-label">A ver (demonstração)</div>', unsafe_allow_html=True)
        st.markdown(f"**{demo_cliente}**")
        st.caption("Dados fictícios, só para demonstrar o serviço. Inicia sessão para aceder à tua área.")
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
    if dados.get("demo"):
        selo_real = '<span class="pill">🧪 Cliente de exemplo</span>'
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
