import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import calendar

st.set_page_config(page_title="Calendário BabySit MV", layout="wide")

st.title("🗓️ Calendário de BabySit - MV")

# Inicializar banco de dados em memória
if 'solicitacoes' not in st.session_state:
    st.session_state.solicitacoes = []

if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

# Sidebar para autenticação
with st.sidebar:
    senha = st.text_input("Senha de admin", type="password")
    if senha == "mvadmin123":
        st.success("Modo admin ativado")
        st.session_state.admin_mode = True
    elif senha:
        st.error("Senha incorreta")

# --- CALENDÁRIO ---
st.markdown("---")
st.subheader("📆 Disponibilidade Mensal")

df = pd.DataFrame(st.session_state.solicitacoes)
if not df.empty and 'data' in df.columns:
    df['data'] = pd.to_datetime(df['data']).dt.date
else:
    df = pd.DataFrame(columns=['data', 'status'])

today = date.today()
ano, mes = today.year, today.month
primeiro_dia_semana, dias_no_mes = calendar.monthrange(ano, mes)
dias_do_mes = [date(ano, mes, d) for d in range(1, dias_no_mes + 1)]

dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
cols = st.columns(7)
for i in range(7):
    cols[i].markdown(f"**{dias_semana[i]}**")

linha = ["" for _ in range(primeiro_dia_semana)] + dias_do_mes
for i in range(0, len(linha), 7):
    semana = linha[i:i+7]
    cols = st.columns(7)
    for j, dia in enumerate(semana):
        if dia == "":
            cols[j].markdown(" ")
        else:
            status_dia = df[df['data'] == dia]['status'].tolist()
            emoji = "✅"
            if any(s == "Aceita" for s in status_dia):
                emoji = "❌"
            elif any(s == "Pendente" for s in status_dia):
                emoji = "⏳"
            if cols[j].button(f"{dia.day} {emoji}", key=str(dia)):
                st.session_state['dia_selecionado'] = dia

# --- INFERIOR: PEDIDO À ESQUERDA, HORAS À DIREITA ---
st.markdown("---")
col_pedido, col_horas = st.columns([1, 1])

with col_pedido:
    st.subheader("📣 Solicitar Babysit")
    with st.form("form_solicitacao"):
        nome = st.text_input("Seu nome")
        data = st.date_input("Data desejada", min_value=datetime.today())
        hora_inicio = st.time_input("Hora de início", value=time(9,0))
        hora_fim = st.time_input("Hora de término", value=time(17,0))
        detalhes = st.text_area("Mais detalhes (opcional)")
        enviar = st.form_submit_button("Enviar solicitação")

        if enviar:
            st.session_state.solicitacoes.append({
                "nome": nome,
                "data": str(data),
                "hora_inicio": str(hora_inicio),
                "hora_fim": str(hora_fim),
                "detalhes": detalhes,
                "status": "Pendente"
            })
            st.success("Solicitação enviada com sucesso!")
            st.rerun()

with col_horas:
    if 'dia_selecionado' in st.session_state:
        dia = st.session_state['dia_selecionado']
        st.subheader(f"🔹 Horários para {dia.strftime('%d/%m/%Y')}")
        pedidos_dia = df[df['data'] == dia]

        if pedidos_dia.empty:
            st.info("Nenhuma solicitação para este dia.")
        else:
            horarios_ocupados = []
            for _, row in pedidos_dia.iterrows():
                st.write(f"🕒 {row['hora_inicio']} - {row['hora_fim']} | **{row['nome']}** ({row['status']})")
                if row['status'] == "Aceita":
                    horarios_ocupados.append((row['hora_inicio'], row['hora_fim']))

            st.markdown("#### 🕓 Horas Livres Estimadas")
            for h in range(8, 20):
                bloco_inicio = time(h, 0)
                bloco_fim = time(h+1, 0)
                ocupado = False
                for h_ini_str, h_fim_str in horarios_ocupados:
                    h_ini = datetime.strptime(h_ini_str, "%H:%M:%S").time()
                    h_fim = datetime.strptime(h_fim_str, "%H:%M:%S").time()
                    if (bloco_inicio < h_fim) and (bloco_fim > h_ini):
                        ocupado = True
                        break
                if not ocupado:
                    st.write(f"✅ {bloco_inicio.strftime('%H:%M')} - {bloco_fim.strftime('%H:%M')}")

# --- ADMIN ---
if st.session_state.admin_mode:
    st.markdown("---")
    st.subheader("📋 Solicitações Recebidas (Admin)")
    for i, s in enumerate(st.session_state.solicitacoes):
        with st.expander(f"{s['data']} - {s['nome']}"):
            st.write(f"**Nome:** {s['nome']}")
            st.write(f"**Data:** {s['data']}")
            st.write(f"**Hora:** {s['hora_inicio']} - {s['hora_fim']}")
            st.write(f"**Detalhes:** {s['detalhes'] or 'N/A'}")
            st.write(f"**Status:** {s['status']}")
            if s['status'] == "Pendente":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Aceitar {i}"):
                        st.session_state.solicitacoes[i]['status'] = "Aceita"
                        st.rerun()
                with col2:
                    if st.button(f"Recusar {i}"):
                        st.session_state.solicitacoes[i]['status'] = "Recusada"
                        st.rerun()