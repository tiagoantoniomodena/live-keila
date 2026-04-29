import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Keila", layout="wide", initial_sidebar_state="expanded")

# --- CONEXÃO COM O BANCO DE DADOS (CORRIGIDA) ---
def _nova_conexao():
    # Sua Connection String do Supabase atualizada
    url = "postgresql://postgres.filmiluacrjfmgpjsdts:t1980tlivedakeila@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = True
    return conn

def db():
    if "_pg_conn" not in st.session_state or st.session_state["_pg_conn"].closed:
        st.session_state["_pg_conn"] = _nova_conexao()
    return st.session_state["_pg_conn"]

def run(sql, params=()):
    """Executa query sem retorno (INSERT, UPDATE, DELETE)."""
    with db().cursor() as cur:
        cur.execute(sql, params)

def query(sql, params=()):
    """Executa query com retorno (SELECT)."""
    with db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# --- CRIAÇÃO DAS TABELAS (Executa na primeira vez) ---
def criar_tabelas():
    run("""
        CREATE TABLE IF NOT EXISTS sacolas_ativas (
            cliente TEXT PRIMARY KEY,
            telefone TEXT,
            data_entrega DATE,
            itens TEXT,
            total_estimado DECIMAL(10,2)
        );
        CREATE TABLE IF NOT EXISTS estoque (
            produto TEXT PRIMARY KEY,
            quantidade INTEGER,
            preco DECIMAL(10,2)
        );
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            cliente TEXT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2)
        );
    """)

# --- INTERFACE PRINCIPAL ---
def main():
    criar_tabelas()
    
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Ir para:", ["Sacolas Ativas", "Estoque", "Histórico de Vendas"])

    # --- ABA: SACOLAS ATIVAS ---
    if menu == "Sacolas Ativas":
        st.header("🛍️ Gerenciamento de Sacolas")
        
        with st.expander("Nova Sacola"):
            with st.form("form_sacola"):
                c1, c2 = st.columns(2)
                cliente = c1.text_input("Nome da Cliente")
                tel = c2.text_input("Telefone")
                data = st.date_input("Data de Entrega")
                itens = st.text_area("Itens (separados por vírgula)")
                valor = st.number_input("Total Estimado (R$)", min_value=0.0, format="%.2f")
                
                if st.form_submit_button("Salvar Sacola"):
                    if cliente:
                        run("INSERT INTO sacolas_ativas (cliente, telefone, data_entrega, itens, total_estimado) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (cliente) DO UPDATE SET data_entrega=EXCLUDED.data_entrega, itens=EXCLUDED.itens", 
                            (cliente, tel, data, itens, valor))
                        st.success("Sacola salva!")
                        st.rerun()

        st.subheader("Sacolas em Aberto")
        dados = query("SELECT * FROM sacolas_ativas")
        if dados:
            for s in dados:
                with st.container():
                    col_info, col_btn = st.columns([4, 1])
                    col_info.write(f"**{s['cliente']}** - Entrega: {s['data_entrega']} | Itens: {s['itens']}")
                    if col_btn.button("Finalizar Venda", key=s['cliente']):
                        # Lógica de venda
                        run("INSERT INTO vendas (cliente, valor_total) VALUES (%s, %s)", (s['cliente'], s['total_estimado']))
                        run("DELETE FROM sacolas_ativas WHERE cliente = %s", (s['cliente'],))
                        st.success(f"Venda de {s['cliente']} finalizada!")
                        st.rerun()
        else:
            st.info("Nenhuma sacola ativa.")

    # --- ABA: ESTOQUE ---
    elif menu == "Estoque":
        st.header("📦 Controle de Estoque")
        with st.form("add_estoque"):
            p = st.text_input("Produto")
            q = st.number_input("Quantidade", min_value=0)
            pr = st.number_input("Preço Unitário", min_value=0.0)
            if st.form_submit_button("Atualizar Estoque"):
                run("INSERT INTO estoque (produto, quantidade, preco) VALUES (%s,%s,%s) ON CONFLICT (produto) DO UPDATE SET quantidade=estoque.quantidade + EXCLUDED.quantidade", (p, q, pr))
                st.success("Estoque atualizado!")
        
        st.table(query("SELECT * FROM estoque"))

    # --- ABA: HISTÓRICO ---
    elif menu == "Histórico de Vendas":
        st.header("📈 Histórico de Vendas")
        vendas = query("SELECT * FROM vendas ORDER BY data_venda DESC")
        if vendas:
            st.dataframe(vendas)
            total = sum(v['valor_total'] for v in vendas)
            st.metric("Faturamento Total", f"R$ {total:,.2f}")
        else:
            st.info("Sem vendas registradas.")

if __name__ == "__main__":
    main()
