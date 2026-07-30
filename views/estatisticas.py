import random
import streamlit as st
from utils import setup_page

cliente, dados, accent = setup_page("Estatísticas")

st.markdown("# Estatísticas")
st.write("Resultados do último mês (dados de demonstração).")
st.markdown("")

seed = sum(ord(ch) for ch in cliente)
seguidores = 800 + (seed % 900)
alcance = 3000 + (seed % 4000)
engagement = round(2.5 + (seed % 30) / 10, 1)
novos_seguidores = 20 + (seed % 80)

c1, c2, c3, c4 = st.columns(4)
for c, label, val in zip(
    [c1, c2, c3, c4],
    ["Seguidores", "Alcance mensal", "Taxa de engagement", "Novos seguidores"],
    [f"{seguidores:,}", f"{alcance:,}", f"{engagement}%", f"+{novos_seguidores}"],
):
    with c:
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
                <div class="metric-big">{val}</div>
                <div style="color:#a9b6d0;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")
st.markdown("### Evolução de seguidores")
random.seed(seed)
base = seguidores - novos_seguidores
valores = [base + int(novos_seguidores * i / 6 + random.randint(-5, 5)) for i in range(7)]
st.line_chart(valores)
