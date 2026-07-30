import streamlit as st
from utils import setup_page, NEGOCIOS_MOCKUP, listar_mockups, guardar_mockup, apagar_foto

setup_page("Mockups", mostrar_cliente=False)

st.markdown("# Mockups")
st.write(
    "Exemplos reais de trabalhos que já fizemos, para mostrar aos clientes o "
    "nível de qualidade e o tipo de conteúdo que criamos para cada setor."
)
st.markdown("")

cols = st.columns(3)

for i, (icone, negocio) in enumerate(NEGOCIOS_MOCKUP):
    fotos = listar_mockups(negocio)

    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="card">
                <b style="font-size:1.05rem;">{icone} {negocio}</b>
            """,
            unsafe_allow_html=True,
        )

        if fotos:
            sub_cols = st.columns(2)
            for j, caminho in enumerate(fotos):
                with sub_cols[j % 2]:
                    st.image(str(caminho), use_container_width=True)
                    if st.button("🗑️", key=f"remover-mockup-{negocio}-{caminho.name}", help="Remover"):
                        apagar_foto(caminho)
                        st.rerun()
        else:
            st.caption("Ainda sem exemplos.")

        with st.expander("➕ Enviar imagens"):
            novos = st.file_uploader(
                f"Enviar mockups para: {negocio}",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=f"upload-mockup-{negocio}",
                label_visibility="collapsed",
            )
            if novos:
                for f in novos:
                    guardar_mockup(negocio, f.name, f.getbuffer())
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.info("💡 Estes exemplos aparecem aqui independentemente do cliente selecionado. Servem para mostrar o teu portefólio geral.")
