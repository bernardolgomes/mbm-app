import streamlit as st
from utils import setup_page

cliente, dados, accent = setup_page("Proposta & Condições", mostrar_cliente=False)

st.markdown("# Proposta & Condições")
st.write("O que está incluído na gestão mensal das redes sociais.")
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <span class="pill">Starter / Basic</span>
            <h2 class="accent">150€ <span style="font-size:1rem;color:#7c8aa8;">/mês</span></h2>
            <p>2 publicações + 2 stories/mês</p>
            <p>✅ 1 rede social (Instagram)</p>
            <p>✅ Design simples e textos</p>
            <p>✅ Agendamento e publicação</p>
            <p>✅ Criação de destaques no Instagram com os stories publicados</p>
            <p>✅ Relatório mensal simples</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <span class="pill">Business</span>
            <h2 class="accent">225€ <span style="font-size:1rem;color:#7c8aa8;">/mês</span></h2>
            <p>4 publicações + 4 stories/mês</p>
            <p>✅ 2 redes sociais (Instagram + Facebook)</p>
            <p>✅ 1 segmentação de clientes</p>
            <p>✅ Design profissional e copywriting</p>
            <p>✅ Gestão de comunidade (comentários + DMs)</p>
            <p>✅ Criação de destaques no Instagram com os stories publicados</p>
            <p>✅ Relatório mensal detalhado</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="card" style="border-color:{accent};border-width:2px;">
            <span class="pill">Premium ⭐ Mais procurado</span>
            <h2 class="accent">350€ <span style="font-size:1rem;color:#7c8aa8;">/mês</span></h2>
            <p>6 publicações + 6 stories/mês</p>
            <p>✅ 2 redes sociais (Instagram + Facebook)</p>
            <p>✅ 3 segmentações de clientes</p>
            <p>✅ Design profissional + vídeo/reels</p>
            <p>✅ Gestão completa de comunidade</p>
            <p>✅ WhatsApp automático (setup + manutenção)</p>
            <p>✅ Criação de destaques no Instagram com os stories publicados</p>
            <p>✅ Relatório mensal + reunião estratégica</p>
            <p>✅ Gestão de campanhas pagas (orçamento à parte)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")
st.markdown("### Extras (fora dos pacotes)")
st.markdown(
    """
    <div class="card">
    <p>🎯 Segmentação de clientes adicional — <b>20€</b> cada</p>
    <p>📸 Sessão fotográfica — <b>paga à parte</b> (orçamento sob consulta)</p>
    <p>📢 Gestão de campanhas de anúncios pagos — <b>15%–20%</b> do orçamento investido em ads, mínimo 100€/mês</p>
    <p>🎬 Produção de vídeo adicional — <b>25€–40€/vídeo</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")
st.markdown("### 🎉 Campanha de lançamento")
st.markdown(
    """
    <div class="card">
    <p>Para as <b>primeiras 10 angariações</b>: desconto de <b>75€ trimestral</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")
st.markdown("### Condições gerais")
st.markdown(
    """
    <div class="card">
    <p>📌 Sem fidelização — cancelamento com 15 dias de aviso</p>
    <p>📌 Conteúdo aprovado antes de publicar (grupo/app dedicado)</p>
    <p>📌 Fotos fornecidas pelo cliente ou tiradas por nós (sessão fotográfica à parte)</p>
    <p>📌 Pagamento mensal, até ao dia 5</p>
    <p>📌 Publicação nos melhores horários: 12h–14h e 19h30–21h</p>
    </div>
    """,
    unsafe_allow_html=True,
)
