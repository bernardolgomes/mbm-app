import streamlit as st
from utils import setup_page, listar_fotos, guardar_foto, apagar_foto

cliente, dados, accent = setup_page("Exemplos de Posts")

st.markdown("# Exemplos de Posts")
st.write(f"Sugestões de conteúdo para **{cliente}** — envia fotos para cada tipo de publicação.")
st.markdown("")

EXEMPLOS = {
    "Farmácia": [
        ("👩‍⚕️ Apresentação / equipa", "Conhece a equipa da farmácia ou um serviço, ex.: entrega ao domicílio"),
        ("💊 Dica do farmacêutico", "Conselho de saúde sazonal — alergias, hidratação, gripes"),
        ("⭐ Testemunho / prova social", "Feedback de um cliente ou destaque de produto/serviço"),
        ("🎉 Promoção / chamada para ação", "Campanha do mês ou lembrete, ex.: vacinação da gripe"),
    ],
    "Restauração": [
        ("🍽️ Prato do dia", "Hoje é dia de bacalhau à Brás"),
        ("🎉 Promoção", "Menu de almoço a 8,50€ até sexta"),
        ("👨‍🍳 Bastidores", "O chef a preparar o prato da semana"),
        ("❓ Story interativo", "Vota: qual sobremesa volta ao menu?"),
    ],
    "Ginásio": [
        ("💪 Dica de treino", "3 exercícios para fortalecer o core"),
        ("🎉 Promoção", "Inscrição grátis até domingo"),
        ("🏆 Bastidores", "Antes/depois de um aluno do ginásio"),
        ("❓ Story interativo", "Quiz: qual o teu treino ideal?"),
    ],
}
lista = EXEMPLOS.get(dados["nicho"], EXEMPLOS["Farmácia"])

for titulo, legenda in lista:
    fotos = listar_fotos(cliente, titulo)

    st.markdown(
        f"""
        <div class="card">
            <b style="font-size:1.05rem;">{titulo}</b>
            <p style="color:#a9b6d0;font-size:0.9rem;margin-top:4px;">"{legenda}"</p>
        """,
        unsafe_allow_html=True,
    )

    if fotos:
        cols = st.columns(4)
        for i, caminho in enumerate(fotos):
            with cols[i % 4]:
                st.image(str(caminho), use_container_width=True)
                if st.button("🗑️ Remover", key=f"remover-{titulo}-{caminho.name}"):
                    apagar_foto(caminho)
                    st.rerun()
    else:
        st.caption("Ainda sem fotos para esta legenda.")

    novos = st.file_uploader(
        f"Enviar fotos para: {titulo}",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"upload-{titulo}",
    )
    if novos:
        for f in novos:
            guardar_foto(cliente, titulo, f.name, f.getbuffer())
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

st.info("💡 As fotos ficam associadas à legenda correspondente, para o cliente ver exatamente como cada tipo de post vai ficar.")
