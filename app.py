import streamlit as st
from utils import NOME_NEGOCIO, render_marca_sidebar, render_cliente_selector, render_sair_button, login_gate

st.set_page_config(
    page_title=NOME_NEGOCIO,
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bloqueia todo o resto da app até haver login válido.
login_gate()

# Os títulos ficam definidos aqui, no código — não dependem do nome do ficheiro,
# por isso os acentos e emojis aparecem sempre corretamente na barra lateral.

# Páginas gerais/comerciais — não dependem de qual cliente está selecionado.
paginas_gerais = [
    st.Page("views/home.py", title="Início", icon="🏠", default=True),
    st.Page("views/como_funciona.py", title="Como Funciona", icon="🧭"),
    st.Page("views/proposta_condicoes.py", title="Proposta & Condições", icon="📋"),
    st.Page("views/mockups.py", title="Mockups", icon="🖼️"),
]

# Páginas operacionais — mostram o conteúdo do cliente selecionado.
paginas_cliente = [
    st.Page("views/exemplos_posts.py", title="Exemplos de Posts", icon="🎨"),
    st.Page("views/calendario.py", title="Calendário de Publicação", icon="🗓️"),
    st.Page("views/estatisticas.py", title="Estatísticas", icon="📊"),
]

todas_paginas = paginas_gerais + paginas_cliente

# Menu automático escondido — desenhamos os links à mão, para controlar a ordem
# exata na sidebar (marca → páginas gerais → cliente selecionado → páginas do cliente).
navegacao = st.navigation(todas_paginas, position="hidden")

with st.sidebar:
    render_marca_sidebar()

    for pagina in paginas_gerais:
        st.page_link(pagina)

    st.markdown("---")
    render_cliente_selector()
    st.markdown("---")

    for pagina in paginas_cliente:
        st.page_link(pagina)

    st.markdown("---")
    render_sair_button()

navegacao.run()
