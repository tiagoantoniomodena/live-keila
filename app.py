import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Vendas Keila", layout="wide")

# --- CONEXÃO COM O BANCO DE DADOS ---
def _nova_conexao():
    # URL do Supabase que você forneceu
    url = "postgresql://postgres.filmiluacrjfmgpjsdts:t1980tlivedakeila@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = True
    return conn

def db():
    if "_pg_conn" not in st.session_state or st.session_state["_pg_conn"].closed:
        st.session_state["_pg_conn"] = _nova_conexao()
    return st.session_state["_pg_conn"]

def run(sql, params=()):
    with db().cursor() as cur:
        cur.execute(sql, params)

def query(sql, params=()):
    with db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# --- INICIALIZAÇÃO DO BANCO (Cria todas as tabelas se não existirem) ---
def inicializar_banco():
    # Criando as 3 tabelas necessárias para o seu sistema
    run("""
        CREATE TABLE IF NOT EXISTS sacolas_ativas (
            cliente TEXT PRIMARY KEY,
            telefone TEXT,
            data_entrega DATE,
            itens TEXT,
            total_estimado DECIMAL(10,2)
        );
    """)
    run("""
        CREATE TABLE IF NOT EXISTS estoque (
            produto TEXT PRIMARY KEY,
            quantidade INTEGER,
            preco DECIMAL(10,2)
        );
    """)
    run("""
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            cliente TEXT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total DECIMAL(10,2)
        );
    """)

# --- INTERFACE PRINCIPAL ---
def main():
    # Tenta criar as tabelas antes de qualquer coisa
    try:
        inicializar_banco()
    except Exception as e:
        st.error(f"Erro ao inicializar banco de dados: {e}")
        return

    st.sidebar.title("Menu Principal")
    menu = st.sidebar.radio("Selecione uma opção:", ["Sacolas Ativas", "Estoque", "Histórico de Vendas"])

    # --- ABA: SACOLAS ATIVAS ---
    if menu == "Sacolas Ativas":
        st.header("🛍️ Sacolas Ativas")
        
        with st.expander("Cadastrar Nova Sacola"):
            with st.form("form_sacola"):
                cliente = st.text_input("Nome da Cliente")
                tel = st.text_input("Telefone")
                data = st.date_input("Data de Entrega")
                itens = st.text_area("Itens")
                valor = st.number_input("Valor Estimado (R$)", min_value=0.0)
                
                if st.form_submit_button("Salvar"):
                    if cliente:
                        run("INSERT INTO sacolas_ativas (cliente, telefone, data_entrega, itens, total_estimado) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (cliente) DO UPDATE SET itens=EXCLUDED.itens, total_estimado=EXCLUDED.total_estimado", 
                            (cliente, tel, data, itens, valor))
                        st.success("Sacola salva com sucesso!")
                        st.rerun()

        st.subheader("Lista de Sacolas")
        dados = query("SELECT * FROM sacolas_ativas")
        if dados:
            for s in dados:
                col_txt, col_btn = st.columns([3, 1])
                col_txt.write(f"**{s['cliente']}** - {s['itens']} (R$ {s['total_estimado']})")
                if col_btn.button("Dar Baixa (Vendido)", key=f"venda_{s['cliente']}"):
                    run("INSERT INTO vendas (cliente, valor_total) VALUES (%s, %s)", (s['cliente'], s['total_estimado']))
                    run("DELETE FROM sacolas_ativas WHERE cliente = %s", (s['cliente'],))
                    st.success("Venda registrada!")
                    st.rerun()
        else:
            st.info("Nenhuma sacola aberta.")

    # --- ABA: ESTOQUE ---
    elif menu == "Estoque":
        st.header("📦 Estoque")
        with st.form("add_est"):
            prod = st.text_input("Produto")
            qtd = st.number_input("Quantidade", min_value=0)
            preco = st.number_input("Preço", min_value=0.0)
            if st.form_submit_button("Adicionar"):
                run("INSERT INTO estoque (produto, quantidade, preco) VALUES (%s,%s,%s) ON CONFLICT (produto) DO UPDATE SET quantidade = estoque.quantidade + EXCLUDED.quantidade", (prod, qtd, preco))
                st.rerun()
        
        st.table(query("SELECT * FROM estoque"))

    # --- ABA: HISTÓRICO ---
    elif menu == "Histórico de Vendas":
        st.header("📈 Histórico de Vendas")
        # Agora a tabela 'vendas' existe com certeza
        vendas = query("SELECT * FROM vendas ORDER BY data_venda DESC")
        if vendas:
            st.dataframe(vendas)
            total = sum(v['valor_total'] for v in vendas if v['valor_total'])
            st.metric("Total Vendido", f"R$ {total:,.2f}")
        else:
            st.info("Ainda não há vendas registradas.")

if __name__ == "__main__":
    main()
