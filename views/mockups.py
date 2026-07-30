import streamlit as st
from utils import setup_page, NEGOCIOS_MOCKUP, listar_mockups, guardar_mockup, apagar_foto

cliente, dados, accent = setup_page("Mockups")

st.markdown("# Mockups")
st.write(
    "Exemplos reais de trabalhos que já fizemos — para mostrar aos clientes o "
    "nível de qualidade e o tipo de conteúdo que criamos para cada setor."
)
st.markdown("")

for icone, negocio in NEGOCIOS_MOCKUP:
    fotos = listar_mockups(negocio)

    st.markdown(
        f"""
        <div class="card">
            <b style="font-size:1.1rem;">{icone} {negocio}</b>
        """,
        unsafe_allow_html=True,
    )

    if fotos:
        cols = st.columns(4)
        for i, caminho in enumerate(fotos):
            with cols[i % 4]:
                st.image(str(caminho), use_container_width=True)
                if st.button("🗑️ Remover", key=f"remover-mockup-{negocio}-{caminho.name}"):
                    apagar_foto(caminho)
                    st.rerun()
    else:
        st.caption("Ainda sem exemplos adicionados para este negócio.")

    novos = st.file_uploader(
        f"Enviar mockups para: {negocio}",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"upload-mockup-{negocio}",
    )
    if novos:
        for f in novos:
            guardar_mockup(negocio, f.name, f.getbuffer())
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

st.info("💡 Estes exemplos aparecem aqui independentemente do cliente selecionado — servem para mostrar o teu portefólio geral.")
