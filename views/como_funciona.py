import streamlit as st
from utils import setup_page

cliente, dados, accent = setup_page("Como Funciona", mostrar_cliente=False)

st.markdown("# Como Funciona")
st.write("O processo completo de gestão das tuas redes sociais, do planeamento aos resultados.")
st.markdown("")

fases = [
    (
        "1️⃣ Planeamento de conteúdo",
        [
            "Definição dos temas: campanhas e dicas do setor",
            "Calendário mensal de conteúdos",
            "Estratégia alinhada com os objetivos do cliente",
            "Planeamento com datas comemorativas relevantes",
        ],
    ),
    (
        "2️⃣ Criação de conteúdo",
        [
            "Design das imagens",
            "Escrita dos textos",
            "Seleção de hashtags estratégicas",
        ],
    ),
    (
        "3️⃣ Publicação",
        [
            "Agendamento dos posts",
            "Publicação nos melhores horários (12h–14h e 19h30–21h)",
            "Gestão de Instagram e Facebook",
        ],
    ),
    (
        "4️⃣ Gestão da comunidade",
        [
            "Resposta a comentários",
            "Resposta a mensagens privadas",
            "Encaminhamento de contactos comerciais",
        ],
    ),
    (
        "5️⃣ Relatórios",
        [
            "Alcance das publicações",
            "Crescimento de seguidores",
            "Interações e resultados",
            "Relatório mensal",
        ],
    ),
]

for titulo, pontos in fases:
    linhas = "".join(f"<p>✅ {p}</p>" for p in pontos)
    st.markdown(
        f"""
        <div class="card">
            <b style="font-size:1.1rem;" class="accent">{titulo}</b>
            {linhas}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("Todo o conteúdo é aprovado pelo cliente antes de publicar.")
