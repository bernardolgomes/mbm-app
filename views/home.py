import streamlit as st
from utils import NOME_NEGOCIO, setup_page, render_login

cliente, dados, accent = setup_page("Início", mostrar_cliente=False)

_, col_login = st.columns([3, 1])
with col_login:
    render_login("home")

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="padding:12px 0 6px 0;">
        <h1 style="font-size:2.6rem;line-height:1.15;margin-bottom:6px;">
            Fazemos a tua marca crescer nas redes sociais.
        </h1>
        <p style="font-size:1.05rem;color:#4b5a51;max-width:640px;">
            Gestão profissional de Instagram e Facebook, criação de conteúdo e planeamento
            que dá resultados, sem teres de gastar tempo nenhum com isso.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("📩 Pedir orçamento", "mailto:bernardo.lemos.gomes@gmail.com?subject=Pedido de orçamento", use_container_width=True)
with c2:
    st.link_button("💬 Falar no WhatsApp", "https://wa.me/351967878262", use_container_width=True)
with c3:
    st.link_button("📅 Agendar reunião", "mailto:bernardo.lemos.gomes@gmail.com?subject=Agendar reunião", use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# QUEM SOMOS
# ---------------------------------------------------------------------------
st.markdown("## Quem somos")
st.markdown(
    f"""
    <div class="card">
        <p>Ajudamos negócios locais (farmácias, restaurantes, ginásios e clínicas) a
        fortalecer a sua presença digital através da gestão de redes sociais, criação de
        conteúdo e planeamento estratégico feito à medida de cada negócio.</p>
        <p>Nada de conteúdo genérico: cada plano é pensado para o setor e o público do
        cliente, com um calendário alinhado às épocas e temas que realmente interessam.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SERVIÇOS
# ---------------------------------------------------------------------------
st.markdown("## Serviços")
servicos = [
    ("📱", "Gestão de Instagram e Facebook", "Publicações e stories geridos do início ao fim"),
    ("🎨", "Criação de conteúdo e design", "Imagens, textos e hashtags estratégicas"),
    ("📸", "Fotografia e vídeo", "Conteúdo visual para redes sociais"),
    ("📅", "Planeamento e agendamento", "Calendário mensal alinhado com o teu negócio"),
    ("📊", "Análise de resultados", "Relatórios mensais de alcance e crescimento"),
    ("📢", "Publicidade nas redes (Meta Ads)", "Campanhas pagas geridas por nós"),
]
cols = st.columns(3)
for i, (icone, titulo, desc) in enumerate(servicos):
    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="card">
                <div style="font-size:1.6rem;margin-bottom:6px;">{icone}</div>
                <b>{titulo}</b>
                <p style="color:#6b7a70;font-size:0.85rem;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# PORQUE ESCOLHER-NOS
# ---------------------------------------------------------------------------
st.markdown("## Porque escolher-nos")
vantagens = [
    "Estratégias personalizadas para o teu setor",
    "Conteúdos criativos, nunca genéricos",
    "Publicações consistentes, sem falhas",
    "Comunicação próxima e direta",
    "Relatórios claros de desempenho, todos os meses",
]
st.markdown(
    '<div class="card">' + "".join(f"<p>✅ {v}</p>" for v in vantagens) + "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# COMO TRABALHAMOS
# ---------------------------------------------------------------------------
st.markdown("## Como trabalhamos")
passos = [
    ("1", "Reunião inicial", "Percebemos o teu negócio, objetivos e público"),
    ("2", "Definição da estratégia", "Escolhemos o plano e montamos o calendário"),
    ("3", "Criação e aprovação", "Produzimos o conteúdo e validamos contigo antes de publicar"),
    ("4", "Publicação e acompanhamento", "Publicamos nos melhores horários e reportamos os resultados"),
]
cols = st.columns(4)
for c, (num, titulo, desc) in zip(cols, passos):
    with c:
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
                <div class="accent" style="font-size:1.8rem;font-weight:800;">{num}</div>
                <b>{titulo}</b>
                <p style="color:#6b7a70;font-size:0.82rem;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# QUEM SOU (FUNDADOR)
# ---------------------------------------------------------------------------
st.markdown("## Quem sou")
st.markdown(
    """
    <div class="card">
        <div style="display:flex;align-items:flex-start;gap:16px;">
            <div style="width:56px;height:56px;border-radius:50%;background:#1E8A5F;
                        display:flex;align-items:center;justify-content:center;font-size:1.6rem;
                        color:white;flex-shrink:0;">
                BG
            </div>
            <div>
                <b style="font-size:1.05rem;">Bernardo Lemos Gomes</b>
                <p style="color:#6b7a70;font-size:0.85rem;margin-top:-4px;">Fundador do MBM</p>
                <p>Tenho formação em Gestão Aplicada pela Católica Lisbon School of Business &
                Economics e um bootcamp de Data Analytics pelo Le Wagon, onde trabalho com
                análise de dados, estratégia e ferramentas de visualização como Power BI e
                Looker Studio. Antes disso, geri as operações de um clube de padel, onde ajudei
                a multiplicar a faturação mensal, uma experiência que me mostrou o impacto real
                que uma boa gestão e comunicação têm num negócio local.</p>
                <p>Junto essa visão analítica e orientada a resultados à criação de conteúdo.
                Também crio conteúdo próprio no YouTube sobre finanças e mentalidade, para
                ajudar negócios como o teu a crescerem nas redes sociais de forma consistente
                e mensurável.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# TESTEMUNHOS
# ---------------------------------------------------------------------------
st.markdown("## Testemunhos")
st.markdown(
    """
    <div class="card">
        <p style="color:#6b7a70;">Ainda estamos a começar. Os primeiros testemunhos de
        clientes vão aparecer aqui assim que tivermos os primeiros resultados documentados.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# CONTACTOS
# ---------------------------------------------------------------------------
st.markdown("## Contactos")
st.markdown(
    """
    <div class="card">
        <p>📞 <b>Telefone:</b> +351 967 878 262</p>
        <p>📧 <b>E-mail:</b> bernardo.lemos.gomes@gmail.com</p>
        <p>💬 <b>WhatsApp:</b> +351 967 878 262</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# EXPLORAR A TUA ÁREA (navegação rápida)
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("## Explorar a tua área")
c1, c2, c3, c4, c5 = st.columns(5)
resumo = [
    ("🧭 Como Funciona", "O processo completo, passo a passo"),
    ("📋 Proposta & Condições", "Preços e o que está incluído no teu plano"),
    ("🎨 Exemplos de Posts", "Mockups de conteúdo pensados para o teu negócio"),
    ("🗓️ Calendário", "Planificação mensal das publicações"),
    ("📊 Estatísticas", "Resultados e evolução das redes"),
]
for c, (titulo, desc) in zip([c1, c2, c3, c4, c5], resumo):
    with c:
        st.markdown(
            f"""
            <div class="card">
                <b>{titulo}</b>
                <p style="color:#6b7a70;font-size:0.85rem;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

