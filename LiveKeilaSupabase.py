import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests as _req
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Live da Keila - Cloud", layout="wide", page_icon="🔴")

# --- CHAVES DO SUPABASE (INSERIDAS DIRETAMENTE) ---
URL = "https://filmiluacrjfmgpjsdts.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpbG1pbHVhY3JqZm1ncGpzZHRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczMDQzMzEsImV4cCI6MjA5Mjg4MDMzMX0.gaAAB_O--pAnQtHaV7KFdVs4LXN6Es4hors4iZm2CGs"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- CSS PERSONALIZADO (DARK MODE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    html, body, .stApp { font-family: 'Space Grotesk', sans-serif !important; background: #080C12 !important; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #111827; border-radius: 8px; color: #9CA3AF; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #3B82F6 !important; color: white !important; }
    div[data-testid="stExpander"] { background-color: #111827; border: 1px solid #1F2937; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE BANCO DE DADOS ---
def get_clientes():
    res = supabase.table("clientes").select("*").order("nome").execute()
    return res.data

def get_sacolas():
    res = supabase.table("sacolas_ativas").select("*").execute()
    return res.data

def get_vendas():
    res = supabase.table("vendas").select("*").order("id", desc=True).execute()
    return res.data

def upsert_sacola(cliente, itens):
    data = {"cliente": cliente, "itens": itens, "ultima_alteracao": datetime.now().isoformat()}
    supabase.table("sacolas_ativas").upsert(data).execute()

# --- INTERFACE ---
st.title("🔴 Live da Keila | Sistema Cloud")

abas = st.tabs(["🛍️ Vendas & Sacolas", "📊 Relatórios", "👤 Clientes"])

# --- ABA 1: VENDAS ---
with abas[0]:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Lançar Produto")
        clientes_db = get_clientes()
        lista_nomes = ["➕ NOVO CLIENTE..."] + [c['nome'].upper() for c in clientes_db]
        escolha = st.selectbox("Selecione o Cliente", lista_nomes)
        
        if escolha == "➕ NOVO CLIENTE...":
            nome_c = st.text_input("Nome/@ do Novo Cliente").strip().lower()
        else:
            nome_c = escolha.lower()
            
        prod = st.text_input("Nome do Produto")
        col_p, col_q = st.columns(2)
        preco = col_p.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        qtd = col_q.number_input("Qtd", min_value=1, value=1)
        
        if st.button("Adicionar à Sacola", use_container_width=True, type="primary"):
            if nome_c and prod:
                res_s = supabase.table("sacolas_ativas").select("itens").eq("cliente", nome_c).execute()
                itens = res_s.data[0]['itens'] if res_s.data else []
                itens.append({"nome": prod, "preco": preco, "qtd": qtd})
                upsert_sacola(nome_c, itens)
                st.success(f"Item adicionado para {nome_c}!")
                st.rerun()

    with c2:
        st.subheader("Sacolas Abertas")
        sacolas = get_sacolas()
        if not sacolas:
            st.info("Nenhuma sacola aberta no momento.")
        for s in sacolas:
            with st.expander(f"👤 {s['cliente'].upper()}"):
                total_sacola = 0
                for idx, item in enumerate(s['itens']):
                    sub = item['preco'] * item['qtd']
                    total_sacola += sub
                    st.write(f"• {item['qtd']}x {item['nome']} - R$ {sub:.2f}")
                
                st.divider()
                frete = st.number_input(f"Frete para {s['cliente']}", min_value=0.0, key=f"f_{s['cliente']}")
                st.markdown(f"### Total: R$ {total_sacola + frete:.2f}")
                
                if st.button(f"Finalizar Venda: {s['cliente'].upper()}", key=f"btn_{s['cliente']}"):
                    venda_data = {
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "cliente": s['cliente'],
                        "itens": s['itens'],
                        "total": total_sacola + frete,
                        "frete": frete
                    }
                    supabase.table("vendas").insert(venda_data).execute()
                    supabase.table("sacolas_ativas").delete().eq("cliente", s['cliente']).execute()
                    st.balloons()
                    st.rerun()

# --- ABA 2: RELATÓRIOS ---
with abas[1]:
    vendas_db = get_vendas()
    if vendas_db:
        df = pd.DataFrame(vendas_db)
        st.metric("Faturamento Bruto", f"R$ {df['total'].sum():.2f}")
        st.dataframe(df[['data', 'cliente', 'total']], use_container_width=True)
    else:
        st.write("Nenhuma venda realizada ainda.")

# --- ABA 3: CLIENTES ---
with abas[2]:
    st.subheader("Cadastro de Clientes")
    with st.form("cad_cliente"):
        n_c = st.text_input("Nome do Cliente / @Instagram")
        tel = st.text_input("Telefone")
        obs = st.text_area("Observações")
        if st.form_submit_button("Salvar Cliente"):
            supabase.table("clientes").insert({"nome": n_c.lower(), "telefone": tel, "observacoes": obs}).execute()
            st.success("Cliente cadastrado!")
            st.rerun()
