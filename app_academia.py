import streamlit as st
import requests
import time
from datetime import datetime

# Configuração da página focada em celular
st.set_page_config(page_title="PulseAI - Treino Mobile", layout="centered")
st.title("🏋️‍♂️ Modo Academia")

# --- FUNÇÃO ATUALIZADA COM O SEU LINK DO MAKE ---
def salvar_treino_no_notion(exercicio, treino_tipo, carga, reps, rpe):
    # O seu link oficial do Make já está configurado aqui!
    URL_MAKE = "https://hook.us2.make.com/d7vhnmged2s5liwdht7i8vshmf4ir0h5" 
    
    payload = {
        "exercicio": exercicio,
        "treino": treino_tipo,
        "carga": carga,
        "reps": reps,
        "rpe": rpe
    }
    
    # O aplicativo agora dispara diretamente para o seu cenário do Make
    resposta = requests.post(URL_MAKE, json=payload)
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

# Menu de seleção
treino_selecionado = st.selectbox("📅 Selecione o Treino de Hoje:", list(fichas.keys()))
tempo_descanso = st.selectbox("⏱️ Tempo de Descanso Padrão:", [60, 90, 120], format_func=lambda x: f"{x}s")

st.markdown("---")
st.markdown(f"### 📝 Exercícios - {treino_selecionado}")

# Renderização dinâmica dos exercícios
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
        
        with cs1:
            s1 = st.checkbox("1ª Série", key=f"s1_{treino_selecionado}_{idx}")
        with cs2:
            s2 = st.checkbox("2ª Série", key=f"s2_{treino_selecionado}_{idx}")
        with cs3:
            s3 = st.checkbox("3ª Série", key=f"s3_{treino_selecionado}_{idx}")
            
        # Lógica do Cronômetro Automático ao marcar a série
        trigger_key = f"last_triggered_{treino_selecionado}_{idx}"
        if trigger_key not in st.session_state:
            st.session_state[trigger_key] = [False, False, False]
            
        current_states = [s1, s2, s3]
        if current_states != st.session_state[trigger_key]:
            if any(c and not p for c, p in zip(current_states, st.session_state[trigger_key])):
                placeholder = st.empty()
                for t in range(tempo_descanso, -1, -1):
                    placeholder.metric("⏳ Tempo de Descanso:", f"{t // 60:02d}:{t % 60:02d}")
                    time.sleep(1)
                placeholder.success("💪 Hora da próxima série!")
            st.session_state[trigger_key] = current_states

st.markdown("---")

# Botão de envio
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
        st.success("🏆 Ficha de treino enviada com sucesso para o Make!")
    else:
        st.error("❌ Erro ao enviar os dados. Verifique a conexão do Webhook.")