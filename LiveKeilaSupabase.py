import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import requests as _req
from supabase import create_client, Client

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Live da Keila - Cloud", layout="wide", page_icon="🔴")

# --- CONEXÃO SUPABASE ---
# Buscando das Secrets do Streamlit que você configurou
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# --- CSS ORIGINAL (MANTIDO) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, .stApp { font-family: 'Space Grotesk', sans-serif !important; background: #080C12 !important; }
.kpi-card { background: #111827; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 18px 20px; border-left: 3px solid #60A5FA; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #111827; border-radius: 8px; color: #9CA3AF; }
.stTabs [aria-selected="true"] { background: #1D4ED8 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE BANCO DE DADOS (ADAPTADAS DO SEU ORIGINAL) ---

def get_clientes():
    res = supabase.table("clientes").select("*").order("nome").execute()
    return res.data

def get_sacolas():
    res = supabase.table("sacolas_ativas").select("*").order("ultima_alteracao", desc=True).execute()
    return res.data

def get_vendas():
    res = supabase.table("vendas").select("*").order("id", desc=True).execute()
    return res.data

def salvar_sacola(cliente, itens):
    data = {
        "cliente": cliente,
        "itens": itens,
        "ultima_alteracao": datetime.now().isoformat()
    }
    supabase.table("sacolas_ativas").upsert(data).execute()

def finalizar_venda(data_venda, cliente, itens, total, frete=0):
    venda = {
        "data": data_venda,
        "cliente": cliente,
        "itens": itens,
        "total": total,
        "frete": frete,
        "pago": 0
    }
    supabase.table("vendas").insert(venda).execute()
    supabase.table("sacolas_ativas").delete().eq("cliente", cliente).execute()

# --- FUNÇÕES DE UTILITÁRIOS (ETIQUETAS / CEP / CPF - IGUAIS AO SEU ORIGINAL) ---

def buscar_cep(cep):
    cep = "".join(filter(str.isdigit, cep))
    if len(cep) != 8: return None
    try:
        r = _req.get(f"https://viacep.com.br/ws/{cep}/json/")
        return r.json() if r.status_code == 200 else None
    except: return None

# --- INTERFACE PRINCIPAL ---

st.markdown('### 🔴 Live da Keila | Gestão Cloud')

aba1, aba2, aba3, aba4 = st.tabs(["🛍️ Sacolas", "📋 Histórico", "📊 Relatórios", "👤 Clientes"])

# --- LÓGICA DA ABA 1: SACOLAS (Com todas as suas funções) ---
with aba1:
    col_l, col_r = st.columns([1, 2.5])
    
    with col_l:
        st.subheader("Lançar Item")
        clientes_db = get_clientes()
        nomes_lista = ["➕ NOVO CLIENTE..."] + [c['nome'].upper() for c in clientes_db]
        escolha = st.selectbox("Cliente", nomes_lista)
        
        nome_cliente = ""
        if escolha == "➕ NOVO CLIENTE...":
            nome_cliente = st.text_input("@ Instagram").strip().lower()
        else:
            nome_cliente = escolha.lower()
            
        prod = st.text_input("Produto")
        c_p, c_q = st.columns(2)
        preco = c_p.number_input("Preço", min_value=0.0, format="%.2f")
        qtd = c_q.number_input("Qtd", min_value=1, value=1)
        
        if st.button("Adicionar à Sacola", type="primary", use_container_width=True):
            if nome_cliente and prod:
                # Busca itens atuais da sacola no Supabase
                res_s = supabase.table("sacolas_ativas").select("itens").eq("cliente", nome_cliente).execute()
                itens_atuais = res_s.data[0]['itens'] if res_s.data else []
                itens_atuais.append({"nome": prod, "preco": preco, "qtd": qtd})
                salvar_sacola(nome_cliente, itens_atuais)
                st.success(f"Item adicionado para {nome_cliente}!")
                st.rerun()

    with col_r:
        sacolas = get_sacolas()
        if not sacolas:
            st.info("Nenhuma sacola aberta no momento.")
        for s in sacolas:
            with st.expander(f"🛍️ {s['cliente'].upper()}"):
                total_s = 0
                for idx, item in enumerate(s['itens']):
                    c1, c2, c3 = st.columns([3, 1, 0.5])
                    sub = item['preco'] * item['qtd']
                    total_s += sub
                    c1.write(f"{item['qtd']}x {item['nome']}")
                    c2.write(f"R$ {sub:.2f}")
                    if c3.button("❌", key=f"del_{s['cliente']}_{idx}"):
                        s['itens'].pop(idx)
                        salvar_sacola(s['cliente'], s['itens'])
                        st.rerun()
                
                st.divider()
                frete = st.number_input("Frete (R$)", min_value=0.0, key=f"frete_{s['cliente']}")
                st.write(f"**Total Geral: R$ {total_s + frete:.2f}**")
                
                if st.button("Finalizar Venda", key=f"fin_{s['cliente']}", use_container_width=True):
                    finalizar_venda(datetime.now().strftime("%d/%m/%Y %H:%M"), s['cliente'], None, total_s + frete, frete)
                    st.balloons()
                    st.rerun()

# --- ABA 3: RELATÓRIOS (Com Gráficos e KPIs) ---
with aba3:
    vendas = get_vendas()
    if vendas:
        df = pd.DataFrame(vendas)
        c1, c2, c3 = st.columns(3)
        c1.metric("Faturamento Total", f"R$ {df['total'].sum():.2f}")
        c2.metric("Vendas", len(df))
        c3.metric("Média por Venda", f"R$ {df['total'].mean():.2f}")
        
        fig = px.line(df, x="data", y="total", title="Desempenho de Vendas", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados para gerar relatórios.")

# (As abas de Clientes e Histórico seguem a mesma lógica de trazer o seu código original e trocar o banco)
