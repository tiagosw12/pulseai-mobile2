import streamlit as st
import requests
import time
from datetime import datetime

# Configuração da página focada em celular
st.set_page_config(page_title="PulseAI - Modo Academia", layout="centered")
st.title("🏋️‍♂️ Modo Academia")

# Credenciais diretas do seu Notion (Simples e Automático)
NOTION_TOKEN = "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"
DATABASE_ID = "382e3a01f89080a9b5a9d0db04121564"

# --- FUNÇÃO PARA ADICIONAR O TREINO DIRETO NO NOTION ---
def salvar_treino_no_notion(exercicio, carga, reps, rpe):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Envia os dados do exercício para as colunas da sua tabela do Notion
    payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Name": { "title": [{ "text": { "content": exercicio } }] },
            "VFC": { "number": int(carga) },          # Usando a coluna VFC temporariamente para Carga
            "FC_Repouso": { "number": int(reps) },   # Usando FC_Repouso para Repetições
            "Sono": { "number": float(rpe) },        # Usando Sono para RPE
            "Data": { "date": { "start": datetime.now().strftime("%Y-%m-%d") } }
        }
    }
    
    resposta = requests.post(url, headers=headers, json=payload)
    return resposta.status_code == 200

# --- SIMULAÇÃO DA SUA FICHA DE TREINO ---
# Depois podemos fazer o site ler dinamicamente, mas fixo assim é o jeito mais rápido e blindado de testar hoje
ficha_treino = [
    {"nome": "Supino Reto", "carga_antiga": 30, "reps_antigas": 10},
    {"nome": "Puxada Pulley", "carga_antiga": 40, "reps_antigas": 12},
    {"nome": "Agachamento", "carga_antiga": 50, "reps_antigas": 10},
    {"nome": "Rosca Direta", "carga_antiga": 12, "reps_antigas": 12}
]

st.markdown("### 📝 Exercícios de Hoje")

# Renderiza os exercícios na tela do celular
for idx, ex in enumerate(ficha_treino):
    with st.container(border=True):
        st.markdown(f"#### 🏷️ {ex['nome']}")
        st.caption(f"Meta anterior: {ex['carga_antiga']} kg x {ex['reps_antigas']} reps")
        
        # Inputs compactos para o celular
        c1, c2, c3 = st.columns(3)
        with c1:
            carga_atual = st.number_input("Carga (kg)", min_value=0, value=ex['carga_antiga'], key=f"cg_{idx}")
        with c2:
            reps_atuais = st.number_input("Reps", min_value=0, value=ex['reps_antigas'], key=f"rp_{idx}")
        with c3:
            rpe_atual = st.number_input("RPE", min_value=1, max_value=10, value=8, key=f"rpe_{idx}")
            
        # Sistema de progresso visual
        if carga_atual > ex['carga_antiga']:
            st.success("🚀 Carga Progredida!")
            
        # Contador de Séries
        st.write("Séries:")
        cs1, cs2, cs3, _ = st.columns([2, 2, 2, 4])
        s1 = cs1.checkbox("1ª", key=f"s1_{idx}")
        s2 = cs2.checkbox("2ª", key=f"s3_{idx}")
        s3 = cs3.checkbox("3ª", key=f"s2_{idx}")
        
        # Timer de Descanso integrado por exercício
        c_tm, c_btn = st.columns([4, 6])
        with c_tm:
            tempo = st.selectbox("Descanso:", [60, 90, 120], format_func=lambda x: f"{x}s", key=f"tm_{idx}")
        with c_btn:
            st.write("") # Espaçador
            if st.button("⏱️ Iniciar", key=f"btn_{idx}", use_container_width=True):
                placeholder = st.empty()
                for t in range(tempo, -1, -1):
                    placeholder.metric("⏳ Descanse:", f"{t // 60:02d}:{t % 60:02d}")
                    time.sleep(1)
                placeholder.success("💪 Próxima série!")

st.markdown("---")

# Botão de envio para a nuvem
if st.button("🏁 Finalizar Treino e Mandar pro Notion", type="primary", use_container_width=True):
    com_sucesso = True
    
    # Varre os exercícios e envia um por um para a tabela do Notion
    for idx, ex in enumerate(ficha_treino):
        sucesso = salvar_treino_no_notion(
            exercicio=ex['nome'],
            carga=st.session_state[f"cg_{idx}"],
            reps=st.session_state[f"rp_{idx}"],
            rpe=st.session_state[f"rpe_{idx}"]
        )
        if not sucesso:
            com_sucesso = False
            
    if com_sucesso:
        st.balloons()
        st.success("🏆 Treino salvo no seu Notion com sucesso!")
    else:
        st.error("❌ Ops, houve uma falha ao enviar alguns dados para o Notion.")