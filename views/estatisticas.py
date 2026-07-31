import streamlit as st
import pandas as pd
from datetime import date

from utils import (
    setup_page,
    e_admin,
    carregar_estatisticas,
    guardar_estatisticas,
    carregar_calendario,
    gerar_insights,
    gerar_pdf_relatorio,
    INDICADORES,
    INDICADORES_INTEIROS,
)

cliente, dados, accent = setup_page("Estatísticas")

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

st.markdown("# Estatísticas")
st.write(
    f"Aqui podes acompanhar a evolução da tua performance nas redes sociais de forma "
    f"clara e direta, mês após mês. Todos os nossos relatórios são construídos com base "
    f"nesta leitura própria dos resultados de **{cliente}**, independente da análise que "
    "o Instagram e o Facebook fazem internamente."
)
st.markdown("")

historico = carregar_estatisticas(cliente)

# ---------------------------------------------------------------------------
# ADMIN: introduzir/atualizar os números do mês
# ---------------------------------------------------------------------------
if e_admin():
    with st.expander("✏️ Atualizar números deste mês (admin)"):
        hoje = date.today()
        col_m, col_a = st.columns(2)
        with col_m:
            mes_num = st.selectbox(
                "Mês", list(range(1, 13)), index=hoje.month - 1,
                format_func=lambda m: MESES_PT[m - 1], key="stats_mes",
            )
        with col_a:
            ano_num = st.selectbox(
                "Ano", list(range(hoje.year - 1, hoje.year + 2)), index=1, key="stats_ano",
            )
        chave_mes = f"{ano_num:04d}-{mes_num:02d}"
        existente = historico.get(chave_mes, {})

        with st.form("form_estatisticas"):
            valores = {}
            cols_input = st.columns(len(INDICADORES))
            for c, (chave, label, _) in zip(cols_input, INDICADORES):
                with c:
                    if chave in INDICADORES_INTEIROS:
                        valores[chave] = st.number_input(
                            label, value=int(existente.get(chave, 0)), step=1, format="%d",
                            key=f"input-{chave}",
                        )
                    else:
                        valores[chave] = st.number_input(
                            label, value=float(existente.get(chave, 0)), step=0.1, format="%.1f",
                            key=f"input-{chave}",
                        )
            guardar = st.form_submit_button("💾 Guardar dados deste mês")
            if guardar:
                historico[chave_mes] = valores
                guardar_estatisticas(cliente, historico)
                st.toast("Dados guardados ✅")
                st.rerun()

if not historico:
    st.info(
        "Ainda não há dados guardados para este cliente. Inicia sessão como administração "
        "e usa o formulário acima para introduzir os primeiros números, a partir do mês em "
        "que o cliente começou (isto serve de base de comparação para os meses seguintes)."
    )
    st.stop()

meses_ordenados = sorted(historico.keys())
ultimo = meses_ordenados[-1]
anterior = meses_ordenados[-2] if len(meses_ordenados) >= 2 else None
dados_ultimo = historico[ultimo]
dados_anterior = historico[anterior] if anterior else None

# ---------------------------------------------------------------------------
# MÉTRICAS DO ÚLTIMO MÊS (com variação face ao mês anterior)
# ---------------------------------------------------------------------------
st.markdown(f"### Resultados de {ultimo}")
cols = st.columns(len(INDICADORES))
for c, (chave, label, fmt) in zip(cols, INDICADORES):
    valor = dados_ultimo.get(chave)
    delta = None
    if dados_anterior and dados_anterior.get(chave) not in (None, 0) and valor is not None:
        delta = f"{(valor - dados_anterior[chave]) / dados_anterior[chave] * 100:+.1f}%"
    with c:
        st.metric(label, fmt.format(valor) if valor is not None else "-", delta)

st.markdown("")
st.markdown("### Evolução mensal")
if len(meses_ordenados) >= 2:
    indicador_sel = st.selectbox("Indicador", [label for _, label, _ in INDICADORES])
    chave_sel = next(chave for chave, label, _ in INDICADORES if label == indicador_sel)
    valores_serie = {m: historico[m].get(chave_sel, 0) for m in meses_ordenados}
    st.line_chart(valores_serie)
else:
    st.caption("Assim que houver dois ou mais meses registados, aparece aqui o gráfico de evolução.")

st.markdown("### Histórico completo")
linhas = []
for m in meses_ordenados:
    linha = {"Mês": m}
    for chave, label, _ in INDICADORES:
        linha[label] = historico[m].get(chave, 0)
    linhas.append(linha)
df_historico = pd.DataFrame(linhas)

configuracao_colunas = {"Mês": st.column_config.TextColumn("Mês", disabled=True)}
for chave, label, _ in INDICADORES:
    formato = "%.1f" if chave == "engagement" else "%d"
    configuracao_colunas[label] = st.column_config.NumberColumn(label, format=formato)

if e_admin():
    st.caption(
        "Podes corrigir os valores diretamente na tabela. Para remover um mês, seleciona "
        "a linha (à esquerda) e clica no ícone de lixo que aparece por cima da tabela."
    )
    df_editado = st.data_editor(
        df_historico,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config=configuracao_colunas,
        key="editor_estatisticas",
    )
    if st.button("💾 Guardar alterações à tabela"):
        novo_historico = {}
        for _, linha in df_editado.iterrows():
            mes = linha["Mês"]
            if not mes or (isinstance(mes, float) and pd.isna(mes)):
                continue
            novo_historico[mes] = {
                chave: (float(linha[label]) if not pd.isna(linha[label]) else 0.0)
                for chave, label, _ in INDICADORES
            }
        guardar_estatisticas(cliente, novo_historico)
        st.toast("Tabela atualizada ✅")
        st.rerun()
else:
    st.dataframe(
        df_historico, use_container_width=True, hide_index=True, column_config=configuracao_colunas
    )

# ---------------------------------------------------------------------------
# ANÁLISE / INSIGHTS
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🧠 Análise e insights")
chave_cache = f"insights-{cliente}-{ultimo}"
if e_admin():
    if st.button("Gerar leitura dos resultados"):
        with st.spinner("A analisar os dados..."):
            st.session_state[chave_cache] = gerar_insights(cliente, historico)

texto_insight = st.session_state.get(chave_cache)
if texto_insight:
    st.markdown(f'<div class="card">{texto_insight}</div>', unsafe_allow_html=True)
else:
    st.caption(
        "Ainda sem análise gerada para este mês."
        + (" Usa o botão acima para gerar." if e_admin() else "")
    )

# ---------------------------------------------------------------------------
# ADMIN: exportar relatório em PDF
# ---------------------------------------------------------------------------
if e_admin():
    st.markdown("---")
    st.markdown("### 📄 Exportar relatório")
    st.caption("Visível apenas em sessão de administração.")
    if st.button("Gerar PDF do relatório deste cliente"):
        with st.spinner("A montar o relatório..."):
            calendario_completo = carregar_calendario(cliente)
            mes_cal_filtrado = {k: v for k, v in calendario_completo.items() if k.startswith(ultimo)}
            texto_final = texto_insight or gerar_insights(cliente, historico)
            pdf_bytes = gerar_pdf_relatorio(cliente, dados, historico, texto_final, mes_cal_filtrado)
        st.download_button(
            "⬇️ Descarregar PDF",
            data=pdf_bytes,
            file_name=f"relatorio-{cliente}-{ultimo}.pdf",
            mime="application/pdf",
        )
