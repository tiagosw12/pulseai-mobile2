import streamlit as st
import requests
import time
from datetime import datetime

# Configuração da página focada em celular
st.set_page_config(page_title="PulseAI - Treino Mobile", layout="centered")
st.title("🏋️‍♂️ Modo Academia")

# Credenciais do seu Notion
NOTION_TOKEN = "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"
DATABASE_ID = "382e3a01f89080a9b5a9d0db04121564"

def salvar_treino_no_notion(exercicio, treino_tipo, carga, reps, rpe):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Organiza os dados para enviar para a tabela
    payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Name": { "title": [{ "text": { "content": exercicio } }] },
            "VFC": { "number": int(carga) },          # Usando a coluna VFC para Carga temporariamente
            "FC_Repouso": { "number": int(reps) },   # Usando FC_Repouso para Repetições temporariamente
            "Sono": { "number": float(rpe) },        # Usando Sono para RPE temporariamente
            "Data": { "date": { "start": datetime.now().strftime("%Y-%m-%d") } }
        }
    }
    
    resposta = requests.post(url, headers=headers, json=payload)
    return resposta.status_code == 200

# --- ESTRUTURA DAS SUAS 3 FICHAS DE TREINO (A, B e C) ---
fichas = {
    "Treino A - Peito e Tríceps": [
        {"nome": "Supino Reto", "carga_antiga": 30, "reps_antigas": 10},
        {"nome": "Supino Inclinado Hálteres", "carga_antiga": 24, "reps_antigas": 12},
        {"nome": "Tríceps Pulley", "carga_antiga": 20, "reps_antigas": 12},
        {"nome": "Tríceps Testa", "carga_antiga": 10, "reps_antigas": 10}
    ],
    "Treino B - Costas e Bíceps": [
        {"nome": "Puxada Pulley", "carga_antiga": 40, "reps_antigas": 12},
        {"nome": "Remada Baixa", "carga_antiga": 45, "reps_antigas": 10},
        {"nome": "Rosca Direta", "carga_antiga": 12, "reps_antigas": 12},
        {"nome": "Rosca Alternada", "carga_antiga": 14, "reps_antigas": 10}
    ],
    "Treino C - Pernas e Ombros": [
        {"nome": "Agachamento", "carga_antiga": 50, "reps_antigas": 10},
        {"nome": "Leg Press", "carga_antiga": 140, "reps_antigas": 12},
        {"nome": "Desenvolvimento Ombros", "carga_antiga": 16, "reps_antigas": 10},
        {"nome": "Elevação Lateral", "carga_antiga": 10, "reps_antigas": 12}
    ]
}

# Menu para escolher o treino do dia no celular
treino_selecionado = st.selectbox("📅 Selecione o Treino de Hoje:", list(fichas.keys()))
tempo_descanso = st.selectbox("⏱️ Tempo de Descanso Padrão:", [60, 90, 120], format_func=lambda x: f"{x}s")

st.markdown("---")
st.markdown(f"### 📝 Exercícios - {treino_selecionado}")

# Renderiza os exercícios da ficha escolhida
for idx, ex in enumerate(fichas[treino_selecionado]):
    with st.container(border=True):
        st.markdown(f"#### 🏷️ {ex['nome']}")
        st.caption(f"Anterior: {ex['carga_antiga']} kg x {ex['reps_antigas']} reps")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            carga_atual = st.number_input("Carga (kg)", min_value=0, value=ex['carga_antiga'], key=f"cg_{treino_selecionado}_{idx}")
        with c2:
            reps_atuais = st.number_input("Reps", min_value=0, value=ex['reps_antigas'], key=f"rp_{treino_selecionado}_{idx}")
        with c3:
            rpe_atual = st.number_input("RPE (Esforço)", min_value=1, max_value=10, value=8, key=f"rpe_{treino_selecionado}_{idx}")
            
        if carga_atual > ex['carga_antiga']:
            st.success("🚀 Progresso de carga detectado!")
            
        st.write("Marque a série concluída para iniciar o descanso:")
        cs1, cs2, cs3 = st.columns(3)
        
        # Sistema automático: marcar o checkbox ativa o timer
        with cs1:
            s1 = st.checkbox("1ª Série", key=f"s1_{treino_selecionado}_{idx}")
        with cs2:
            s2 = st.checkbox("2ª Série", key=f"s2_{treino_selecionado}_{idx}")
        with cs3:
            s3 = st.checkbox("3ª Série", key=f"s3_{treino_selecionado}_{idx}")
            
        # Monitora se qualquer checkbox mudou de estado para disparar o timer
        trigger_key = f"last_triggered_{treino_selecionado}_{idx}"
        if trigger_key not in st.session_state:
            st.session_state[trigger_key] = [False, False, False]
            
        current_states = [s1, s2, s3]
        if current_states != st.session_state[trigger_key]:
            # Se algum checkbox foi marcado (mudou de False para True)
            if any(c and not p for c, p in zip(current_states, st.session_state[trigger_key])):
                placeholder = st.empty()
                for t in range(tempo_descanso, -1, -1):
                    placeholder.metric("⏳ Tempo de Descanso:", f"{t // 60:02d}:{t % 60:02d}")
                    time.sleep(1)
                placeholder.success("💪 Hora da próxima série!")
            st.session_state[trigger_key] = current_states

st.markdown("---")

if st.button("🏁 Finalizar Treino e Mandar pro Notion", type="primary", use_container_width=True):
    com_sucesso = True
    
    for idx, ex in enumerate(fichas[treino_selecionado]):
        sucesso = salvar_treino_no_notion(
            exercicio=ex['nome'],
            treino_tipo=treino_selecionado,
            carga=st.session_state[f"cg_{treino_selecionado}_{idx}"],
            reps=st.session_state[f"rp_{treino_selecionado}_{idx}"],
            rpe=st.session_state[f"rpe_{treino_selecionado}_{idx}"]
        )
        if not sucesso:
            com_sucesso = False
            
    if com_sucesso:
        st.balloons()
        st.success("🏆 Ficha de treino atualizada no Notion!")
    else:
        st.error("❌ Erro ao enviar os dados para o Notion.")