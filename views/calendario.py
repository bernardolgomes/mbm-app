import streamlit as st
from datetime import date
import calendar as cal
from utils import setup_page, carregar_calendario, guardar_calendario, pode_editar

cliente, dados, accent = setup_page("Calendário de Publicação")
editavel = pode_editar()

st.markdown("# Calendário de Publicação")
if editavel:
    st.write("Escolhe o mês e o tipo de conteúdo para cada dia. Fica tudo gravado por cliente.")
else:
    st.write("A ver em modo visitante. Inicia sessão para editar o calendário.")
st.markdown("")

TIPOS = ["—", "📸 Post", "🎬 Reel", "📝 Story", "🎉 Promoção"]
MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

# ---------------------------------------------------------------------------
# SELETOR DE MÊS / ANO
# ---------------------------------------------------------------------------
hoje = date.today()

col_mes, col_ano = st.columns(2)
with col_mes:
    mes_sel = st.selectbox("Mês", MESES_PT, index=hoje.month - 1)
with col_ano:
    ano_sel = st.selectbox("Ano", list(range(hoje.year - 1, hoje.year + 3)), index=1)

mes_num = MESES_PT.index(mes_sel) + 1
_, num_dias = cal.monthrange(ano_sel, mes_num)

st.markdown("")

# calendário guardado deste cliente (chave = "AAAA-MM-DD"), persiste entre meses/anos
calendario = carregar_calendario(cliente)

dias_do_mes = [date(ano_sel, mes_num, d) for d in range(1, num_dias + 1)]

# alinhar a grelha começando na segunda-feira, com espaços vazios antes do dia 1
primeiro_dia_semana = dias_do_mes[0].weekday()  # 0 = segunda
grelha = [None] * primeiro_dia_semana + dias_do_mes
while len(grelha) % 7 != 0:
    grelha.append(None)
semanas = [grelha[i : i + 7] for i in range(0, len(grelha), 7)]

dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
cols_cab = st.columns(7)
for c, nome_dia in zip(cols_cab, dias_semana_pt):
    c.markdown(f"<div style='text-align:center;color:#7c8aa8;font-size:0.8rem;'>{nome_dia}</div>", unsafe_allow_html=True)

alterou = False
for semana in semanas:
    cols = st.columns(7)
    for c, d in zip(cols, semana):
        with c:
            if d is None:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                continue
            chave = d.isoformat()
            valor_atual = calendario.get(chave, "—")
            st.markdown(f"**{d.day}**")
            escolha = st.selectbox(
                f"dia-{chave}",
                TIPOS,
                index=TIPOS.index(valor_atual) if valor_atual in TIPOS else 0,
                key=f"sel-{chave}",
                label_visibility="collapsed",
                disabled=not editavel,
            )
            if editavel and escolha != valor_atual:
                calendario[chave] = escolha
                alterou = True

if alterou:
    guardar_calendario(cliente, calendario)
    st.toast("Calendário atualizado ✅")

st.markdown("---")
st.caption(f"Plano contratado: {dados['posts_mes']} publicações + {dados['stories_mes']} stories / mês")
