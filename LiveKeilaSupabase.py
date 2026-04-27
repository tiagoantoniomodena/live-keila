import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# --- CHAVES QUE VOCÊ ENVIOU ---
URL = "https://filmiluacrjfmgpjsdts.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpbG1pbHVhY3JqZm1ncGpzZHRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczMDQzMzEsImV4cCI6MjA5Mjg4MDMzMX0.gaAAB_O--pAnQtHaV7KFdVs4LXN6Es4hors4iZm2CGs"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Live da Keila - Cloud", layout="wide")

# --- CSS (Mantendo sua identidade visual) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
    html, body, .stApp { font-family: 'Space Grotesk', sans-serif !important; background: #080C12 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1A1F2B; border-radius: 4px; color: white; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def get_clientes():
    res = supabase.table("clientes").select("*").order("nome").execute()
    return res.data

def get_sacolas():
    res = supabase.table("sacolas_ativas").select("*").execute()
    return res.data

def add_item_sacola(cliente, novo_item):
    # Busca itens atuais
    res = supabase.table("sacolas_ativas").select("itens").eq("cliente", cliente).execute()
    itens = res.data[0]['itens'] if res.data else []
    itens.append(novo_item)
    
    data = {"cliente": cliente, "itens": itens, "ultima_alteracao": datetime.now().isoformat()}
    supabase.table("sacolas_ativas").upsert(data).execute()

# --- INTERFACE PRINCIPAL ---
st.title("🔴 Sistema Live da Keila (Web)")

abas = st.tabs(["🛍️ Vendas/Sacolas", "📊 Relatórios", "👤 Cadastro de Clientes"])

with abas[0]:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Lançar Produto")
        clientes = get_clientes()
        nomes = [c['nome'].upper() for c in clientes]
        nome_sel = st.selectbox("Cliente", ["Selecione..."] + nomes)
        
        prod = st.text_input("Produto")
        preco = st.number_input("Preço", min_value=0.0, format="%.2f")
        qtd = st.number_input("Qtd", min_value=1, value=1)
        
        if st.button("Adicionar à Sacola", type="primary"):
            if nome_sel != "Selecione..." and prod:
                item = {"nome": prod, "preco": preco, "qtd": qtd}
                add_item_sacola(nome_sel.lower(), item)
                st.success(f"Adicionado para {nome_sel}!")
                st.rerun()

    with col2:
        st.subheader("Sacolas em Aberto")
        sacolas = get_sacolas()
        for s in sacolas:
            with st.expander(f"👤 {s['cliente'].upper()}"):
                total_geral = 0
                for i in s['itens']:
                    sub = i['preco'] * i['qtd']
                    st.write(f"{i['qtd']}x {i['nome']} - R$ {sub:.2f}")
                    total_geral += sub
                st.markdown(f"**Total: R$ {total_geral:.2f}**")
                
                if st.button("Finalizar Venda", key=f"btn_{s['cliente']}"):
                    venda = {
                        "cliente": s['cliente'],
                        "itens": s['itens'],
                        "total": total_geral,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    supabase.table("vendas").insert(venda).execute()
                    supabase.table("sacolas_ativas").delete().eq("cliente", s['cliente']).execute()
                    st.rerun()

# --- ABA DE RELATÓRIOS ---
with abas[1]:
    res_vendas = supabase.table("vendas").select("*").execute()
    if res_vendas.data:
        df = pd.DataFrame(res_vendas.data)
        st.metric("Faturamento Total", f"R$ {df['total'].sum():.2f}")
        st.dataframe(df[['data', 'cliente', 'total']], use_container_width=True)
    else:
        st.info("Nenhuma venda finalizada ainda.")