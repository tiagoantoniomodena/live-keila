# ============================================================
#  Tiago Modena Corporation Final
#  Live da Keila — Sistema Gerencial de Lives
#  Backend: PostgreSQL (Supabase) | Deploy: Streamlit Cloud
# ============================================================

import streamlit as st
import psycopg2
import psycopg2.extras
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import requests as _req
import uuid as _uuid

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(page_title="Live da Keila", layout="wide", page_icon="🔴")

# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@500&display=swap');
html, body, .stApp { font-family: 'Space Grotesk', sans-serif !important; background: #080C12 !important; }
.stRadio > div { flex-direction: row !important; gap: 20px !important; }
.stRadio label { background: #1A1F2B; padding: 10px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); color: white; }
.stExpander details summary p { color: #00E676 !important; font-weight: 700 !important; }
.live-header { display: flex; align-items: center; gap: 10px; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1.5rem; }
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: #FF5252; animation: blink 1s infinite; }
@keyframes blink { 0%{opacity:1} 50%{opacity:0.3} 100%{opacity:1} }
.stButton>button[kind="primary"] { background-color: #FF5252 !important; border: none !important; color: white !important; font-weight: bold !important; }
[data-testid="column"] > div > div > div > div { padding-top: 0px !important; }
div[data-testid="stHorizontalBlock"] { align-items: flex-start !important; }

/* ── MELHORIA 2: ícones da sacola alinhados horizontalmente ── */
div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] { align-items: center !important; }

/* ── MELHORIA 3: selecionar texto ao focar ── */
input[type="text"], input[type="number"] { cursor: text; }
input[type="text"]:focus, input[type="number"]:focus { selection-background-color: #FF5252; }

.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-ok   { background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid #00E676; }
.badge-novo { background: rgba(255,82,82,0.15);  color: #FF5252; border: 1px solid #FF5252; }

/* ── Card de sacola — tudo dentro de um único retângulo ── */
.col-header {
    font-size: 0.68rem;
    font-weight: 700;
    color: #4B5563;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 0 0 4px 0;
}
/* Faz o st.container(border=True) da sacola ter visual de card escuro */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0D1117 !important;
    border-color: rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(0,230,118,0.28) !important;
}
/* Remove borda dupla dos containers internos (novo item, etc) */
div[data-testid="stVerticalBlockBorderWrapper"]
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #161B27 !important;
    border-color: rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
}
/* Expander dentro do card — sem borda extra */
div[data-testid="stVerticalBlockBorderWrapper"] details {
    border: none !important;
    background: transparent !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] details summary {
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 0 !important;
    padding: 8px 4px !important;
}
/* Cabeçalho do card dentro do container */
.sacola-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 6px;
}
.sacola-nome { font-size:1rem; font-weight:700; color:#F9FAFB; letter-spacing:0.02em; }
.sacola-tel  { font-size:0.78rem; color:#6B7280; margin-top:2px; }
.sacola-total       { font-size:1.1rem; font-weight:700; color:#00E676; text-align:right; }
.sacola-itens-count { font-size:0.72rem; color:#9CA3AF; text-align:right; }

/* KPI cards */
.kpi-card { background: #111827; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 18px 20px; margin-bottom: 8px; }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #F9FAFB; line-height: 1.1; }
.kpi-sub { font-size: 0.75rem; color: #9CA3AF; margin-top: 2px; }
.kpi-green  { border-left: 3px solid #00E676; }
.kpi-red    { border-left: 3px solid #FF5252; }
.kpi-blue   { border-left: 3px solid #60A5FA; }
.kpi-yellow { border-left: 3px solid #FBBF24; }
.kpi-purple { border-left: 3px solid #A78BFA; }
.kpi-pink   { border-left: 3px solid #F472B6; }
.section-title { font-size: 0.78rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.08em; margin: 1.2rem 0 0.5rem 0; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }
</style>

<script>
/* MELHORIA 3: selecionar todo o texto ao clicar em qualquer input */
document.addEventListener('focusin', function(e) {
    if (e.target.tagName === 'INPUT') {
        setTimeout(() => e.target.select(), 50);
    }
}, true);
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONEXÃO COM BANCO
# ─────────────────────────────────────────────
def _nova_conexao():
    return psycopg2.connect(
        st.secrets["SUPABASE_DB_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

def db():
    conn = st.session_state.get("_pg_conn")
    if conn is None or conn.closed:
        conn = _nova_conexao()
        conn.autocommit = True
        st.session_state["_pg_conn"] = conn
    else:
        try:
            conn.cursor().execute("SELECT 1")
        except Exception:
            conn = _nova_conexao()
            conn.autocommit = True
            st.session_state["_pg_conn"] = conn
    return conn.cursor()

def run(sql, params=()):
    cur = db(); cur.execute(sql, params)

def fetch(sql, params=()):
    cur = db(); cur.execute(sql, params); return cur.fetchall()

def fetchone(sql, params=()):
    cur = db(); cur.execute(sql, params); return cur.fetchone()


# ─────────────────────────────────────────────
# CRIAÇÃO DAS TABELAS
# ─────────────────────────────────────────────
def criar_tabelas():
    run("""CREATE TABLE IF NOT EXISTS sacolas_ativas (
        cliente TEXT PRIMARY KEY, telefone TEXT, itens TEXT, ultima_alteracao TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS vendas (
        id BIGSERIAL PRIMARY KEY, data TEXT, cliente TEXT, telefone TEXT,
        itens TEXT, frete REAL DEFAULT 0, total REAL, pago INTEGER DEFAULT 0)""")
    run("""CREATE TABLE IF NOT EXISTS clientes (
        id BIGSERIAL PRIMARY KEY, nome TEXT, nome_completo TEXT, telefone TEXT,
        cpf TEXT, cep TEXT, logradouro TEXT, numero TEXT, complemento TEXT,
        bairro TEXT, cidade TEXT, estado TEXT, observacoes TEXT, data_cadastro TEXT)""")

criar_tabelas()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def carregar_itens(json_str):
    try:
        dados = json.loads(json_str or "[]")
        return dados if isinstance(dados, list) else []
    except Exception:
        return []

def sincronizar_clientes():
    existentes = {r["nome"].lower() for r in fetch("SELECT nome FROM clientes WHERE nome IS NOT NULL") if r["nome"]}
    fontes = (
        fetch("SELECT cliente AS nome, telefone FROM sacolas_ativas WHERE cliente IS NOT NULL") +
        fetch("SELECT DISTINCT cliente AS nome, telefone FROM vendas WHERE cliente IS NOT NULL")
    )
    vistos = set()
    for row in fontes:
        nome = (row["nome"] or "").strip().lower()
        if not nome or nome in existentes or nome in vistos:
            continue
        vistos.add(nome)
        run("INSERT INTO clientes (nome, data_cadastro) VALUES (%s,%s) ON CONFLICT DO NOTHING",
            (nome, datetime.now().strftime("%d/%m/%Y %H:%M")))

sincronizar_clientes()


# ─────────────────────────────────────────────
# CUPOM
# ─────────────────────────────────────────────
def gerar_imagem_cupom(cliente, itens, frete, subtotal, total_geral, data_venda=""):
    """Gera cupom com layout alinhado idêntico à imagem de referência."""
    BRANCO   = (255, 255, 255)
    PRETO    = (0, 0, 0)
    CINZA    = (130, 130, 130)
    CINZA_L  = (200, 200, 200)
    VERMELHO = (210, 50, 50)

    largura  = 680
    MARG     = 48
    LIN      = 34          # altura de cada linha de item
    altura   = 340 + max(len(itens), 1) * LIN + (40 if frete > 0 else 0)

    img  = Image.new("RGB", (largura, altura), BRANCO)
    draw = ImageDraw.Draw(img)

    # ── Fontes (Courier para visual de cupom) ──
    font_titulo  = None
    font_normal  = None
    font_small   = None
    font_bold    = None
    for nome in ["C:\\Windows\\Fonts\\courbd.ttf", "C:\\Windows\\Fonts\\cour.ttf", "arial.ttf"]:
        try:
            font_titulo = ImageFont.truetype(nome, 22)
            font_bold   = ImageFont.truetype(nome, 20)
            font_normal = ImageFont.truetype(nome, 18)
            font_small  = ImageFont.truetype(nome, 16)
            break
        except Exception:
            continue
    if not font_normal:
        font_titulo = font_bold = font_normal = font_small = ImageFont.load_default()

    # ── Colunas de itens (posições X fixas) ──
    COL_ITEM  = MARG           # Nome do produto
    COL_QTD   = MARG + 260    # Quantidade
    COL_UNIT  = MARG + 320    # Preço unitário
    COL_RS    = MARG + 450    # "R$"
    COL_TOT   = largura - MARG  # Total (alinhado à direita)

    def txt_r(x, y, texto, fonte, cor=PRETO):
        """Escreve texto alinhado à direita a partir de x."""
        bb = draw.textbbox((0, 0), texto, font=fonte)
        w  = bb[2] - bb[0]
        draw.text((x - w, y), texto, cor, font=fonte)

    y = 40

    # Título centralizado
    titulo = "--- LIVE DA KEILA ---"
    bb = draw.textbbox((0, 0), titulo, font=font_titulo)
    tw = bb[2] - bb[0]
    draw.text(((largura - tw) // 2, y), titulo, PRETO, font=font_titulo); y += 44

    # Cliente e data
    draw.text((MARG, y), f"CLIENTE: {cliente.upper()}", PRETO,  font=font_bold);  y += 30
    draw.text((MARG, y), f"DATA:    {data_venda.split(' ')[0]}", CINZA, font=font_normal); y += 40

    # Cabeçalho da tabela
    draw.text((COL_ITEM, y), "ITEM",  PRETO, font=font_bold)
    draw.text((COL_QTD,  y), "QTD",  PRETO, font=font_bold)
    draw.text((COL_UNIT, y), "UNIT", PRETO, font=font_bold)
    txt_r(COL_TOT, y, "TOTAL", font_bold); y += 26

    draw.line((MARG, y, largura - MARG, y), CINZA_L, 1); y += 14

    # Linhas de itens
    for i in itens:
        u = float(i["preco"]); q = int(i["qtd"]); s = u * q
        nome_curto = i["nome"][:26]
        draw.text((COL_ITEM, y), nome_curto,      PRETO, font=font_normal)
        draw.text((COL_QTD,  y), str(q),           PRETO, font=font_normal)
        txt_r(COL_UNIT + 80, y, f"{u:.2f}",        font_normal)
        draw.text((COL_RS,   y), "R$",              CINZA, font=font_small)
        txt_r(COL_TOT,  y, f"{s:.2f}",             font_normal)
        y += LIN

    draw.line((MARG, y + 6, largura - MARG, y + 6), CINZA_L, 1); y += 28

    # Totais
    qtd_tot = sum(int(i["qtd"]) for i in itens)
    draw.text((MARG, y), f"TOTAL ITENS: {qtd_tot}", PRETO, font=font_normal); y += 30
    draw.text((MARG, y), f"SUBTOTAL: R$ {subtotal:.2f}", PRETO, font=font_normal); y += 30
    if frete > 0:
        draw.text((MARG, y), f"FRETE: R$ {frete:.2f}", PRETO, font=font_normal); y += 30

    y += 10
    draw.text((MARG, y), f"TOTAL GERAL: R$ {total_geral:.2f}", VERMELHO, font=font_bold)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=96)
    return buf.getvalue()


# ─────────────────────────────────────────────
# DIALOGS
# ─────────────────────────────────────────────
@st.dialog("Confirmar Finalização")
def confirmar_finalizar_compra(cliente, telefone, itens, total):
    st.warning(f"Finalizar venda de **{cliente.upper()}**?")
    c1, c2 = st.columns(2)
    if c1.button("✅ Sim, Finalizar", type="primary", use_container_width=True):
        run("INSERT INTO vendas (data,cliente,telefone,itens,frete,total) VALUES (%s,%s,%s,%s,%s,%s)",
            (datetime.now().strftime("%d/%m/%Y %H:%M"), cliente, telefone, json.dumps(itens), 0, total))
        run("DELETE FROM sacolas_ativas WHERE cliente=%s", (cliente,))
        st.rerun()
    if c2.button("Cancelar", use_container_width=True): st.rerun()

@st.dialog("Confirmar Exclusão")
def confirmar_exclusao(tipo, id_excluir, extra=None):
    st.error("Tem certeza que deseja excluir este item?")
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Sim, Excluir", type="primary", use_container_width=True):
        if tipo == "venda":       run("DELETE FROM vendas WHERE id=%s", (id_excluir,))
        elif tipo == "item_sacola": run("UPDATE sacolas_ativas SET itens=%s WHERE cliente=%s", (json.dumps(extra), id_excluir))
        elif tipo == "cliente_cadastro": run("DELETE FROM clientes WHERE id=%s", (id_excluir,))
        st.rerun()
    if c2.button("Cancelar", use_container_width=True): st.rerun()


# ─────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────
for k in ["edit_venda_id", "cupom_aberto", "edit_sacola_item", "novo_item_sacola",
          "cad_editando_id", "cad_cep_dados", "hist_itens_uid", "hist_frete", "hist_tel",
          "sacola_expandida"]:
    if k not in st.session_state: st.session_state[k] = None

if not isinstance(st.session_state.hist_itens_uid, dict): st.session_state.hist_itens_uid = {}
if not isinstance(st.session_state.hist_frete, dict):     st.session_state.hist_frete = {}
if not isinstance(st.session_state.hist_tel, dict):       st.session_state.hist_tel = {}


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="live-header"><div class="live-dot"></div>'
    '<span style="color:#FFF;font-weight:700;">Live da Keila | Live Sales</span></div>',
    unsafe_allow_html=True
)

opcoes_aba = ["🛍️ Monitor de Sacolas", "📋 Histórico de Vendas", "📊 Relatório Geral", "👤 Cadastro de Clientes"]
aba_selecionada = st.radio("Navegação", opcoes_aba, horizontal=True, label_visibility="collapsed")


# ══════════════════════════════════════════════════════════════════
# ABA 1 — MONITOR DE SACOLAS
# ══════════════════════════════════════════════════════════════════
if aba_selecionada == "🛍️ Monitor de Sacolas":

    # ── Autocomplete de clientes ──
    todos_clientes = {}
    for r in fetch("SELECT nome, telefone FROM clientes WHERE nome IS NOT NULL"):
        n = (r["nome"] or "").strip().lower()
        if n: todos_clientes[n] = r["telefone"] or ""

    NOVO = "➕ Novo cliente..."
    opcoes_select = [NOVO] + sorted([n.upper() for n in todos_clientes.keys()])

    c_form, c_grid = st.columns([1, 2.5])

    # ──────────────────────────────────────────
    # FORMULÁRIO NOVA SACOLA
    # MELHORIA 1: limpar campos após criar
    # ──────────────────────────────────────────
    with c_form:
        st.markdown("#### 🛍️ Nova Sacola")

        # Usamos um "form_key" incremental para resetar os widgets
        if "form_reset_key" not in st.session_state:
            st.session_state.form_reset_key = 0
        fk = st.session_state.form_reset_key

        escolha = st.selectbox(
            "👤 Cliente", options=opcoes_select, index=0,
            key=f"select_cliente_sacola_{fk}",
            placeholder="Digite para filtrar..."
        )

        if escolha and escolha != NOVO:
            nome_final   = escolha.strip().lower()
            tel_sugerido = todos_clientes.get(nome_final, "")
        else:
            nome_final   = ""
            tel_sugerido = ""

        if escolha == NOVO:
            nome_final = st.text_input(
                "✏️ Nome / @ Instagram",
                placeholder="Cole o @ ou digite o nome",
                key=f"input_nome_novo_sacola_{fk}"
            ).strip().lower()

        if escolha != NOVO and tel_sugerido:
            st.markdown(f"📞 **{tel_sugerido}**")
            tel_nova = tel_sugerido
        else:
            tel_nova = st.text_input(
                "📞 Telefone / WhatsApp",
                value=tel_sugerido,
                placeholder="(00) 00000-0000",
                key=f"input_tel_sacola_{fk}"
            )

        st.divider()
        st.caption("PRODUTO INICIAL (opcional)")
        p = st.text_input("Produto", placeholder="Nome do produto", key=f"input_prod_sacola_{fk}")
        col_q, col_pr = st.columns(2)
        q  = col_q.number_input("Qtd", min_value=1, value=1, key=f"input_qtd_sacola_{fk}")
        pr = col_pr.number_input("R$", min_value=0.0, value=0.0, step=0.5, key=f"input_preco_sacola_{fk}")

        st.write("")
        if st.button("🛍️ Criar Sacola", use_container_width=True, type="primary", key="btn_criar_sacola"):
            cli_nome = nome_final.strip().lower()
            if cli_nome:
                res = fetchone("SELECT itens, telefone FROM sacolas_ativas WHERE cliente=%s", (cli_nome,))
                it = carregar_itens(res["itens"] if res else "[]")
                if p.strip():
                    it.append({"qtd": q, "nome": p.strip(), "preco": pr})
                tel_salvo = tel_nova if tel_nova else (res["telefone"] if res else "")
                # MELHORIA 4: ultima_alteracao = agora → sobe para o topo
                run("""
                    INSERT INTO sacolas_ativas (cliente, telefone, itens, ultima_alteracao)
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (cliente) DO UPDATE SET
                        telefone=EXCLUDED.telefone, itens=EXCLUDED.itens,
                        ultima_alteracao=EXCLUDED.ultima_alteracao
                """, (cli_nome, tel_salvo, json.dumps(it), datetime.now().isoformat()))
                # MELHORIA 1: incrementa chave para resetar todos os widgets
                st.session_state.form_reset_key += 1
                # Expande a sacola recém-criada
                st.session_state.sacola_expandida = cli_nome
                st.rerun()
            else:
                st.warning("Informe o nome do cliente.")

    # ──────────────────────────────────────────
    # GRID DE SACOLAS
    # MELHORIA 5: cards encapsulados com visual limpo
    # ──────────────────────────────────────────
    with c_grid:
        busca = st.text_input(
            "Busca", placeholder="🔍 Pesquisar sacola...", label_visibility="collapsed"
        ).strip().lower()

        sacolas = fetch("SELECT * FROM sacolas_ativas ORDER BY ultima_alteracao DESC")

        for row in sacolas:
            its     = carregar_itens(row["itens"])
            cli_id  = row["cliente"]
            tel_row = row["telefone"] or ""

            if busca and busca not in cli_id.lower(): continue
            if not busca and len(its) == 0: continue

            tot_sac   = sum(float(i["qtd"]) * float(i["preco"]) for i in its)
            qtd_itens = sum(int(i["qtd"]) for i in its)

            # ── Card único: cabeçalho + detalhes no mesmo retângulo ──
            expandido = st.session_state.sacola_expandida == cli_id
            with st.container(border=True):
                # Cabeçalho sempre visível
                st.markdown(f"""
                <div class="sacola-header-inner">
                    <div>
                        <div class="sacola-nome">🛍️ {cli_id.upper()}</div>
                        <div class="sacola-tel">📞 {tel_row if tel_row else 'Sem telefone'}</div>
                    </div>
                    <div>
                        <div class="sacola-total">R$ {tot_sac:.2f}</div>
                        <div class="sacola-itens-count">{qtd_itens} item(ns)</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("▼ Ver detalhes / editar", expanded=expandido):

                        # Editar nome e telefone
                        hi1, hi2, hi3 = st.columns([2, 2, 1])
                        novo_nome_cli = hi1.text_input(
                            "👤 Nome", value=cli_id, key=f"name_edit_{cli_id}",
                            label_visibility="collapsed", placeholder="Nome do cliente"
                        ).strip().lower()
                        novo_tel = hi2.text_input(
                            "📞 Tel", value=tel_row, key=f"tel_sac_{cli_id}",
                            label_visibility="collapsed", placeholder="Telefone"
                        )
                        if hi3.button("💾", key=f"save_info_{cli_id}", use_container_width=True, help="Salvar nome/telefone"):
                            if novo_nome_cli != cli_id:
                                run("""INSERT INTO sacolas_ativas (cliente,telefone,itens,ultima_alteracao)
                                    VALUES (%s,%s,%s,%s)
                                    ON CONFLICT (cliente) DO UPDATE SET
                                        telefone=EXCLUDED.telefone, itens=EXCLUDED.itens,
                                        ultima_alteracao=EXCLUDED.ultima_alteracao""",
                                    (novo_nome_cli, novo_tel, row["itens"], datetime.now().isoformat()))
                                run("DELETE FROM sacolas_ativas WHERE cliente=%s", (cli_id,))
                            else:
                                run("UPDATE sacolas_ativas SET telefone=%s, ultima_alteracao=%s WHERE cliente=%s",
                                    (novo_tel, datetime.now().isoformat(), cli_id))
                            st.session_state.sacola_expandida = novo_nome_cli
                            st.rerun()

                        # Cabeçalho de colunas
                        COLS = [3.5, 1.5, 1.2, 0.6, 0.6]
                        hc1, hc2, hc3, hc4, hc5 = st.columns(COLS)
                        hc1.markdown('<div class="col-header">Produto</div>', unsafe_allow_html=True)
                        hc2.markdown('<div class="col-header">Qtd × R$</div>', unsafe_allow_html=True)
                        hc3.markdown('<div class="col-header">Subtotal</div>', unsafe_allow_html=True)

                        # Linhas de itens
                        for idx, i in enumerate(its):
                            item_key = f"sac_{cli_id}_{idx}"

                            if st.session_state.edit_sacola_item == item_key:
                                ec1, ec2, ec3, ec4, ec5 = st.columns(COLS)
                                n_n = ec1.text_input("Item", i["nome"],           key=f"en_{item_key}", label_visibility="collapsed")
                                n_q = ec2.number_input("Qtd", value=int(i["qtd"]),     key=f"eq_{item_key}", label_visibility="collapsed")
                                n_p = ec3.number_input("R$",  value=float(i["preco"]),  key=f"ep_{item_key}", label_visibility="collapsed", step=0.5)
                                if ec4.button("💾", key=f"sv_{item_key}", use_container_width=True, help="Salvar"):
                                    its[idx] = {"nome": n_n, "qtd": n_q, "preco": n_p}
                                    run("UPDATE sacolas_ativas SET itens=%s, ultima_alteracao=%s WHERE cliente=%s",
                                        (json.dumps(its), datetime.now().isoformat(), cli_id))
                                    st.session_state.edit_sacola_item = None
                                    st.session_state.sacola_expandida = cli_id
                                    st.rerun()
                                if ec5.button("✕", key=f"cx_{item_key}", use_container_width=True, help="Cancelar"):
                                    st.session_state.edit_sacola_item = None
                                    st.rerun()
                            else:
                                subtotal_item = float(i["qtd"]) * float(i["preco"])
                                vc1, vc2, vc3, vc4, vc5 = st.columns(COLS)
                                vc1.markdown(
                                    f'<p style="margin:0;padding:5px 0;font-size:0.85rem;font-weight:600;color:#E5E7EB;">{i["nome"]}</p>',
                                    unsafe_allow_html=True)
                                vc2.markdown(
                                    f'<p style="margin:0;padding:5px 0;font-size:0.82rem;color:#9CA3AF;">{int(i["qtd"])} × R$ {float(i["preco"]):.2f}</p>',
                                    unsafe_allow_html=True)
                                vc3.markdown(
                                    f'<p style="margin:0;padding:5px 0;font-size:0.85rem;font-weight:700;color:#fff;">R$ {subtotal_item:.2f}</p>',
                                    unsafe_allow_html=True)
                                if vc4.button("✏️", key=f"ed_{item_key}", use_container_width=True, help="Editar item"):
                                    st.session_state.edit_sacola_item = item_key
                                    st.session_state.sacola_expandida = cli_id
                                    st.rerun()
                                if vc5.button("🗑️", key=f"rm_{item_key}", use_container_width=True, help="Remover item"):
                                    its_temp = list(its); its_temp.pop(idx)
                                    confirmar_exclusao("item_sacola", cli_id, its_temp)

                        # Adicionar novo item
                        if st.session_state.novo_item_sacola == cli_id:
                            with st.container(border=True):
                                st.caption("NOVO ITEM")
                                nc1, nc2, nc3 = st.columns([2.5, 1, 1])
                                novo_n = nc1.text_input("Produto", key=f"new_n_{cli_id}", placeholder="Nome do produto")
                                novo_q = nc2.number_input("Qtd", 1, key=f"new_q_{cli_id}")
                                novo_p = nc3.number_input("R$", 0.0, step=0.5, key=f"new_p_{cli_id}")
                                bc1, bc2 = st.columns(2)
                                if bc1.button("✅ Confirmar", key=f"cn_{cli_id}", use_container_width=True, type="primary"):
                                    if novo_n:
                                        its.append({"nome": novo_n, "qtd": novo_q, "preco": novo_p})
                                        run("UPDATE sacolas_ativas SET itens=%s, ultima_alteracao=%s WHERE cliente=%s",
                                            (json.dumps(its), datetime.now().isoformat(), cli_id))
                                        st.session_state.novo_item_sacola = None
                                        st.session_state.sacola_expandida = cli_id
                                        st.rerun()
                                if bc2.button("❌ Cancelar", key=f"cc_{cli_id}", use_container_width=True):
                                    st.session_state.novo_item_sacola = None
                                    st.rerun()
                        else:
                            if st.button("➕ Adicionar Item", key=f"bt_a_{cli_id}", use_container_width=True):
                                st.session_state.novo_item_sacola = cli_id
                                st.session_state.sacola_expandida = cli_id
                                st.rerun()

                        st.divider()

                        # Rodapé: total + finalizar
                        rf1, rf2, rf3 = st.columns([1.2, 1, 1.8])
                        rf1.markdown(
                            f'<div style="font-size:0.82rem;color:#9CA3AF;">{qtd_itens} item(ns)</div>'
                            f'<div style="font-size:1.1rem;font-weight:700;color:#00E676;">R$ {tot_sac:.2f}</div>',
                            unsafe_allow_html=True)
                        if rf3.button("✅ FINALIZAR COMPRA", key=f"f_{cli_id}", use_container_width=True, type="primary"):
                            confirmar_finalizar_compra(cli_id, novo_tel, its, tot_sac)


# ══════════════════════════════════════════════════════════════════
# ABA 2 — HISTÓRICO DE VENDAS
# ══════════════════════════════════════════════════════════════════
elif aba_selecionada == "📋 Histórico de Vendas":

    vendas = fetch("SELECT * FROM vendas ORDER BY id DESC")

    # ALTERAÇÃO 3: busca primeiro, totais refletem o filtro
    busca_h = st.text_input(
        "Pesquisar", placeholder="🔍 Pesquisar no Histórico...", label_visibility="collapsed"
    ).strip().lower()

    # Filtra a lista
    vendas_filtradas = []
    for v in vendas:
        if busca_h and (
            busca_h not in v["cliente"].lower()
            and busca_h not in v["data"].lower()
            and busca_h not in (v["telefone"] or "")
        ):
            continue
        vendas_filtradas.append(v)

    # Totais calculados sobre a lista filtrada
    if vendas_filtradas:
        v_tot = sum(v["total"] or 0 for v in vendas_filtradas)
        f_tot = sum(v["frete"] or 0 for v in vendas_filtradas)
        pagas = sum(1 for v in vendas_filtradas if v["pago"] == 1)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Vendas",   f"R$ {v_tot:.2f}")
        m2.metric("Total Fretes",   f"R$ {f_tot:.2f}")
        m3.metric("Volume",         len(vendas_filtradas))
        m4.metric("Pagas",          pagas)
        st.divider()

    def _uid_lista(itens_raw):
        result = []
        for i in itens_raw:
            item = dict(i)
            if "_uid" not in item: item["_uid"] = _uuid.uuid4().hex
            result.append(item)
        return result

    for v in vendas_filtradas:

        its = carregar_itens(v["itens"])
        t_v = (v["total"] or 0) + (v["frete"] or 0)
        vid = v["id"]

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1.5])
            c1.markdown(
                f"**{v['cliente'].upper()}**<br>"
                f"<small>{v['data']} | {v['telefone'] or 'S/ Tel'}</small>",
                unsafe_allow_html=True)
            c2.markdown(f"**R$ {t_v:.2f}**")

            status_txt = "🟢 Pago" if v["pago"] == 1 else "🔴 Aberto"
            if c3.button(status_txt, key=f"st_{vid}", use_container_width=True):
                run("UPDATE vendas SET pago=%s WHERE id=%s", (1 if v["pago"]==0 else 0, vid))
                st.rerun()

            with c4:
                b1, b2, b3 = st.columns(3)
                if b1.button("📋", key=f"cp_{vid}", use_container_width=True):
                    st.session_state.cupom_aberto = vid if st.session_state.cupom_aberto != vid else None
                    st.rerun()
                if b2.button("⚙️", key=f"cfg_{vid}", use_container_width=True):
                    if st.session_state.edit_venda_id == vid:
                        st.session_state.edit_venda_id = None
                        st.session_state.hist_itens_uid.pop(vid, None)
                        st.session_state.hist_frete.pop(vid, None)
                        st.session_state.hist_tel.pop(vid, None)
                    else:
                        st.session_state.edit_venda_id = vid
                        st.session_state.hist_itens_uid[vid] = _uid_lista(its)
                        st.session_state.hist_frete[vid] = float(v["frete"] or 0)
                        st.session_state.hist_tel[vid]   = v["telefone"] or ""
                    st.rerun()
                if b3.button("🗑️", key=f"del_{vid}", use_container_width=True):
                    confirmar_exclusao("venda", vid)

            if st.session_state.cupom_aberto == vid:
                st.image(gerar_imagem_cupom(
                    v["cliente"], its, v["frete"] or 0, v["total"] or 0, t_v, v["data"]))

            if st.session_state.edit_venda_id == vid:
                if vid not in st.session_state.hist_itens_uid:
                    st.session_state.hist_itens_uid[vid] = _uid_lista(its)
                    st.session_state.hist_frete[vid] = float(v["frete"] or 0)
                    st.session_state.hist_tel[vid]   = v["telefone"] or ""

                itens_uid = st.session_state.hist_itens_uid[vid]
                COLS_H = [3.5, 1.5, 1.5, 0.6]
                hh1, hh2, hh3, _ = st.columns(COLS_H)
                _h = '<span style="font-size:0.7rem;color:#6B7280;font-weight:600;text-transform:uppercase;">'
                hh1.markdown(f'{_h}Produto</span>', unsafe_allow_html=True)
                hh2.markdown(f'{_h}Qtd</span>',     unsafe_allow_html=True)
                hh3.markdown(f'{_h}R$ Unit.</span>', unsafe_allow_html=True)

                uid_remover = None
                for item in itens_uid:
                    uid = item["_uid"]
                    ic1, ic2, ic3, ic4 = st.columns(COLS_H)
                    ic1.text_input("Produto", value=item["nome"],          key=f"hn_{vid}_{uid}", label_visibility="collapsed")
                    ic2.number_input("Qtd",   value=int(item["qtd"]),     min_value=1,   key=f"hq_{vid}_{uid}", label_visibility="collapsed")
                    ic3.number_input("R$",    value=float(item["preco"]),  min_value=0.0, step=0.5, key=f"hp_{vid}_{uid}", label_visibility="collapsed")
                    if ic4.button("✕", key=f"hx_{vid}_{uid}", use_container_width=True):
                        uid_remover = uid

                if uid_remover is not None:
                    st.session_state.hist_itens_uid[vid] = [i for i in itens_uid if i["_uid"] != uid_remover]
                    st.rerun()

                if st.button("➕ Adicionar Item", key=f"hi_add_{vid}", use_container_width=True):
                    st.session_state.hist_itens_uid[vid].append(
                        {"_uid": _uuid.uuid4().hex, "nome": "Novo item", "qtd": 1, "preco": 0.0})
                    st.rerun()

                st.divider()
                f1, f2 = st.columns(2)
                st.session_state.hist_tel[vid]   = f1.text_input("WhatsApp", value=st.session_state.hist_tel.get(vid,""),     key=f"et_{vid}")
                st.session_state.hist_frete[vid] = f2.number_input("Frete R$", value=st.session_state.hist_frete.get(vid,0.0), step=0.5, key=f"ef_{vid}")

                if st.button("Salvar Edição ✅", key=f"save_{vid}", type="primary", use_container_width=True):
                    itens_salvos = []
                    for item in st.session_state.hist_itens_uid[vid]:
                        uid       = item["_uid"]
                        nome_val  = st.session_state.get(f"hn_{vid}_{uid}", item["nome"])
                        qtd_val   = st.session_state.get(f"hq_{vid}_{uid}", item["qtd"])
                        preco_val = st.session_state.get(f"hp_{vid}_{uid}", item["preco"])
                        if str(nome_val).strip():
                            itens_salvos.append({"nome": nome_val, "qtd": int(qtd_val), "preco": float(preco_val)})
                    frete_val = st.session_state.hist_frete.get(vid, 0.0)
                    tel_val   = st.session_state.hist_tel.get(vid, "")
                    sub = sum(float(i["qtd"]) * float(i["preco"]) for i in itens_salvos)
                    run("UPDATE vendas SET itens=%s, frete=%s, total=%s, telefone=%s WHERE id=%s",
                        (json.dumps(itens_salvos), frete_val, sub, tel_val, vid))
                    st.session_state.edit_venda_id = None
                    st.session_state.hist_itens_uid.pop(vid, None)
                    st.session_state.hist_frete.pop(vid, None)
                    st.session_state.hist_tel.pop(vid, None)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# ABA 3 — RELATÓRIO GERAL
# ══════════════════════════════════════════════════════════════════
elif aba_selecionada == "📊 Relatório Geral":

    vendas_rows = fetch("SELECT * FROM vendas")

    if not vendas_rows:
        st.info("Nenhuma venda registrada ainda.")
    else:
        df = pd.DataFrame([dict(r) for r in vendas_rows])
        df["dt"]      = pd.to_datetime(df["data"], format="%d/%m/%Y %H:%M", errors="coerce")
        df["dia"]     = df["dt"].dt.strftime("%d/%m/%Y")
        df["total_g"] = df["total"].fillna(0) + df["frete"].fillna(0)
        df["frete"]   = df["frete"].fillna(0)

        col_f1, col_f2, col_f3 = st.columns([2, 1.2, 1.2])
        busca_rel     = col_f1.text_input("Filtrar cliente", placeholder="🔍 Filtrar por cliente...", label_visibility="collapsed").strip().lower()
        periodo       = col_f2.selectbox("Período", ["Todos","Hoje","Últimos 7 dias","Últimos 30 dias","Este mês"], label_visibility="collapsed")
        status_filtro = col_f3.selectbox("Status",  ["Todos","Pagos","Em Aberto"], label_visibility="collapsed")

        df_f = df.copy()
        hoje = datetime.now().date()
        if periodo == "Hoje":           df_f = df_f[df_f["dt"].dt.date == hoje]
        elif periodo == "Últimos 7 dias":  df_f = df_f[df_f["dt"].dt.date >= hoje - timedelta(days=7)]
        elif periodo == "Últimos 30 dias": df_f = df_f[df_f["dt"].dt.date >= hoje - timedelta(days=30)]
        elif periodo == "Este mês":
            df_f = df_f[(df_f["dt"].dt.month==hoje.month) & (df_f["dt"].dt.year==hoje.year)]
        if busca_rel: df_f = df_f[df_f["cliente"].str.lower().str.contains(busca_rel)]
        if status_filtro == "Pagos":     df_f = df_f[df_f["pago"]==1]
        elif status_filtro == "Em Aberto": df_f = df_f[df_f["pago"]==0]

        if df_f.empty:
            st.warning("Nenhum resultado para os filtros selecionados.")
        else:
            st.markdown('<div class="section-title">💰 Financeiro</div>', unsafe_allow_html=True)
            total_faturado = df_f["total_g"].sum()
            total_recebido = df_f[df_f["pago"]==1]["total_g"].sum()
            total_aberto   = df_f[df_f["pago"]==0]["total_g"].sum()
            total_fretes   = df_f["frete"].sum()
            num_vendas     = len(df_f)
            ticket_medio   = total_faturado / num_vendas if num_vendas > 0 else 0
            taxa_pagamento = (df_f["pago"].sum() / num_vendas * 100) if num_vendas > 0 else 0

            k1,k2,k3,k4,k5,k6 = st.columns(6)
            k1.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-label">Faturamento Total</div><div class="kpi-value">R$ {total_faturado:,.2f}</div><div class="kpi-sub">{num_vendas} vendas</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-label">Total Recebido</div><div class="kpi-value">R$ {total_recebido:,.2f}</div><div class="kpi-sub">{int(df_f["pago"].sum())} pagas</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card kpi-red"><div class="kpi-label">A Receber</div><div class="kpi-value">R$ {total_aberto:,.2f}</div><div class="kpi-sub">{int((df_f["pago"]==0).sum())} em aberto</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card kpi-yellow"><div class="kpi-label">Ticket Médio</div><div class="kpi-value">R$ {ticket_medio:,.2f}</div><div class="kpi-sub">por venda</div></div>', unsafe_allow_html=True)
            k5.markdown(f'<div class="kpi-card kpi-purple"><div class="kpi-label">Total Fretes</div><div class="kpi-value">R$ {total_fretes:,.2f}</div><div class="kpi-sub">receita de envios</div></div>', unsafe_allow_html=True)
            k6.markdown(f'<div class="kpi-card kpi-pink"><div class="kpi-label">Taxa de Pagamento</div><div class="kpi-value">{taxa_pagamento:.0f}%</div><div class="kpi-sub">vendas quitadas</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">👥 Clientes</div>', unsafe_allow_html=True)
            clientes_unicos   = df_f["cliente"].nunique()
            top_cliente_row   = df_f.groupby("cliente")["total_g"].sum().idxmax() if not df_f.empty else "—"
            top_cliente_val   = df_f.groupby("cliente")["total_g"].sum().max()    if not df_f.empty else 0
            recorrentes       = (df_f.groupby("cliente").size() > 1).sum()
            media_por_cliente = total_faturado / clientes_unicos if clientes_unicos > 0 else 0

            ck1,ck2,ck3,ck4 = st.columns(4)
            ck1.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-label">Clientes Únicos</div><div class="kpi-value">{clientes_unicos}</div><div class="kpi-sub">no período</div></div>', unsafe_allow_html=True)
            ck2.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-label">Melhor Cliente</div><div class="kpi-value" style="font-size:1.1rem;">{str(top_cliente_row).upper()[:14]}</div><div class="kpi-sub">R$ {top_cliente_val:,.2f}</div></div>', unsafe_allow_html=True)
            ck3.markdown(f'<div class="kpi-card kpi-yellow"><div class="kpi-label">Clientes Recorrentes</div><div class="kpi-value">{recorrentes}</div><div class="kpi-sub">compraram 2+ vezes</div></div>', unsafe_allow_html=True)
            ck4.markdown(f'<div class="kpi-card kpi-purple"><div class="kpi-label">Gasto Médio/Cliente</div><div class="kpi-value">R$ {media_por_cliente:,.2f}</div><div class="kpi-sub">lifetime value médio</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">📈 Evolução e Distribuição</div>', unsafe_allow_html=True)
            tab_g1, tab_g2, tab_g3 = st.tabs(["📅 Faturamento por Dia","👤 Top Clientes","📦 Produtos mais Vendidos"])

            with tab_g1:
                df_d = df_f.groupby("dia")["total_g"].sum().reset_index().sort_values("dia")
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=df_d["dia"], y=df_d["total_g"], marker_color="rgba(0,230,118,0.7)", marker_line_color="#00E676", marker_line_width=1, name="Faturamento"))
                fig1.add_trace(go.Scatter(x=df_d["dia"], y=df_d["total_g"], mode="lines+markers", line=dict(color="#60A5FA",width=2), marker=dict(size=6), name="Tendência"))
                fig1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h",yanchor="bottom",y=1.02), xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)",tickprefix="R$ "), height=300)
                st.plotly_chart(fig1, use_container_width=True)

            with tab_g2:
                df_top = df_f.groupby("cliente")["total_g"].sum().reset_index().sort_values("total_g",ascending=True).tail(10)
                fig2 = go.Figure(go.Bar(x=df_top["total_g"], y=df_top["cliente"].str.upper(), orientation="h", marker=dict(color=df_top["total_g"],colorscale="Magma",showscale=False), text=[f"R$ {v:,.2f}" for v in df_top["total_g"]], textposition="outside", textfont=dict(color="white",size=11)))
                fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=80,t=10,b=0), xaxis=dict(gridcolor="rgba(255,255,255,0.05)",tickprefix="R$ "), yaxis=dict(gridcolor="rgba(255,255,255,0.05)"), height=350)
                st.plotly_chart(fig2, use_container_width=True)

            with tab_g3:
                produtos_lista = []
                for _, row in df_f.iterrows():
                    for item in carregar_itens(row["itens"]):
                        produtos_lista.append({"produto": item.get("nome","?"), "qtd": int(item.get("qtd",1)), "receita": float(item.get("qtd",1))*float(item.get("preco",0))})
                if produtos_lista:
                    df_prod = pd.DataFrame(produtos_lista)
                    df_prod_agg = df_prod.groupby("produto").agg(qtd_total=("qtd","sum"), receita_total=("receita","sum")).reset_index().sort_values("receita_total",ascending=True).tail(12)
                    fig3 = go.Figure(go.Bar(x=df_prod_agg["receita_total"], y=df_prod_agg["produto"], orientation="h", marker=dict(color=df_prod_agg["receita_total"],colorscale="Viridis",showscale=False), text=[f"R$ {v:,.2f}  ({q} un)" for v,q in zip(df_prod_agg["receita_total"],df_prod_agg["qtd_total"])], textposition="outside", textfont=dict(color="white",size=10)))
                    fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=120,t=10,b=0), xaxis=dict(gridcolor="rgba(255,255,255,0.05)",tickprefix="R$ "), yaxis=dict(gridcolor="rgba(255,255,255,0.05)"), height=400)
                    st.plotly_chart(fig3, use_container_width=True)
                    top3 = df_prod_agg.sort_values("receita_total",ascending=False).head(3)
                    cols_top = st.columns(3)
                    for idx_t, (col_t, (_, row_t)) in enumerate(zip(cols_top, top3.iterrows())):
                        col_t.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-label">{"🥇🥈🥉"[idx_t]} {row_t["produto"]}</div><div class="kpi-value" style="font-size:1.1rem;">R$ {row_t["receita_total"]:,.2f}</div><div class="kpi-sub">{int(row_t["qtd_total"])} unidades vendidas</div></div>', unsafe_allow_html=True)

            df_aberto = df_f[df_f["pago"]==0][["data","cliente","total_g"]].sort_values("total_g",ascending=False)
            if not df_aberto.empty:
                st.markdown('<div class="section-title">⚠️ Pagamentos Pendentes</div>', unsafe_allow_html=True)
                df_ab = df_aberto.copy(); df_ab.columns = ["Data","Cliente","Valor (R$)"]
                df_ab["Cliente"] = df_ab["Cliente"].str.upper()
                df_ab["Valor (R$)"] = df_ab["Valor (R$)"].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(df_ab, use_container_width=True, hide_index=True)

            st.markdown('<div class="section-title">📋 Extrato Completo</div>', unsafe_allow_html=True)
            df_exibir = df_f[["data","cliente","total","frete","total_g","pago"]].copy()
            df_exibir.columns = ["Data","Cliente","Subtotal","Frete","Total","Status"]
            df_exibir["Cliente"]  = df_exibir["Cliente"].str.upper()
            df_exibir["Subtotal"] = df_exibir["Subtotal"].apply(lambda x: f"R$ {x:,.2f}")
            df_exibir["Frete"]    = df_exibir["Frete"].apply(lambda x: f"R$ {x:,.2f}")
            df_exibir["Total"]    = df_exibir["Total"].apply(lambda x: f"R$ {x:,.2f}")
            df_exibir["Status"]   = df_exibir["Status"].apply(lambda x: "✅ Pago" if x==1 else "🔴 Aberto")
            st.dataframe(df_exibir.sort_values("Data",ascending=False), use_container_width=True, hide_index=True)

            csv = df_f[["data","cliente","telefone","total","frete","total_g","pago"]].to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar para CSV", csv, f"relatorio_live_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════
# ABA 4 — CADASTRO DE CLIENTES
# ══════════════════════════════════════════════════════════════════
elif aba_selecionada == "👤 Cadastro de Clientes":

    def _buscar_cep(cep: str):
        cep_limpo = "".join(filter(str.isdigit, cep))
        if len(cep_limpo) != 8: return None
        try:
            r = _req.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            d = r.json()
            return None if "erro" in d else d
        except: return None

    def _formatar_cpf(cpf: str) -> str:
        digits = "".join(filter(str.isdigit, cpf))
        if len(digits) == 11: return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return cpf

    def _carregar_clientes_db():
        return fetch("""SELECT id, nome, nome_completo, telefone, cpf, cep, logradouro,
                   numero, complemento, bairro, cidade, estado, observacoes, data_cadastro
                   FROM clientes ORDER BY nome ASC""")

    col_busca, col_novo = st.columns([4, 1.2])
    busca_cad = col_busca.text_input(
        "Buscar cliente", placeholder="🔍 @ Instagram, nome completo, CPF, telefone ou cidade...",
        label_visibility="collapsed").strip().lower()

    if col_novo.button("➕ Novo Cliente", use_container_width=True, type="primary"):
        st.session_state.cad_editando_id = "NOVO"
        st.session_state.cad_cep_dados   = {}
        st.rerun()

    st.divider()

    def _form_cliente(dados_iniciais: dict, label_btn: str, id_edicao=None):
        cd = st.session_state.cad_cep_dados or {}
        logradouro_val = cd.get("logradouro") or dados_iniciais.get("logradouro") or ""
        bairro_val     = cd.get("bairro")     or dados_iniciais.get("bairro")     or ""
        cidade_val     = cd.get("localidade") or dados_iniciais.get("cidade")     or ""
        estado_val     = cd.get("uf")         or dados_iniciais.get("estado")     or ""
        cep_val        = cd.get("cep")        or dados_iniciais.get("cep")        or ""
        form_stamp     = cd.get("cep", "")

        with st.container(border=True):
            st.markdown("#### 📋 Identificação")
            fc1, fc2 = st.columns(2)
            nome_v          = fc1.text_input("@ Instagram / Apelido *", value=dados_iniciais.get("nome",""), placeholder="nome de usuário da live", key=f"form_nome_{id_edicao}")
            nome_completo_v = fc2.text_input("Nome Completo (para envio)", value=dados_iniciais.get("nome_completo","") or "", key=f"form_nome_completo_{id_edicao}")
            fd1, fd2 = st.columns(2)
            tel_v = fd1.text_input("📞 Telefone / WhatsApp", value=dados_iniciais.get("telefone","") or "", key=f"form_tel_{id_edicao}")
            cpf_v = fd2.text_input("🪪 CPF", value=dados_iniciais.get("cpf","") or "", placeholder="000.000.000-00", key=f"form_cpf_{id_edicao}", help="O CPF é exigido pelos Correios.")

            st.markdown("#### 📦 Endereço para Entrega")
            cep_col, btn_col = st.columns([2, 1])
            cep_v = cep_col.text_input("CEP", value=cep_val, placeholder="00000-000", key=f"form_cep_{id_edicao}")
            if btn_col.button("🔍 Buscar CEP", use_container_width=True, key=f"btn_buscar_cep_{id_edicao}"):
                resultado = _buscar_cep(cep_v)
                if resultado:
                    st.session_state.cad_cep_dados = resultado; st.toast("✅ CEP encontrado!"); st.rerun()
                else:
                    st.toast("❌ CEP não encontrado.")

            ea1, ea2 = st.columns([3, 1])
            logradouro_v  = ea1.text_input("Logradouro", value=logradouro_val, key=f"form_logradouro_{id_edicao}_{form_stamp}")
            numero_v      = ea2.text_input("Número", value=dados_iniciais.get("numero","") or "", key=f"form_numero_{id_edicao}")
            eb1, eb2 = st.columns(2)
            complemento_v = eb1.text_input("Complemento", value=dados_iniciais.get("complemento","") or "", key=f"form_complemento_{id_edicao}")
            bairro_v      = eb2.text_input("Bairro", value=bairro_val, key=f"form_bairro_{id_edicao}_{form_stamp}")
            ec1, ec2 = st.columns([3, 1])
            cidade_v = ec1.text_input("Cidade", value=cidade_val, key=f"form_cidade_{id_edicao}_{form_stamp}")
            estado_v = ec2.text_input("UF", value=estado_val, key=f"form_estado_{id_edicao}_{form_stamp}", max_chars=2)
            obs_v = st.text_area("📝 Observações", value=dados_iniciais.get("observacoes","") or "", height=80, key=f"form_obs_{id_edicao}")

            if cd and cd.get("logradouro"):
                st.success(f"📍 {logradouro_val}, {bairro_val} — {cidade_val}/{estado_val}")

            sb1, sb2 = st.columns(2)
            if sb1.button(f"💾 {label_btn}", type="primary", use_container_width=True, key=f"btn_salvar_cad_{id_edicao}"):
                if not nome_v.strip():
                    st.error("O @ / apelido é obrigatório.")
                else:
                    if id_edicao == "NOVO":
                        run("""INSERT INTO clientes (nome,nome_completo,telefone,cpf,cep,logradouro,numero,
                             complemento,bairro,cidade,estado,observacoes,data_cadastro)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (nome_v.strip().lower(), nome_completo_v.strip(), tel_v, cpf_v.strip(),
                             cep_v, logradouro_v, numero_v, complemento_v, bairro_v, cidade_v,
                             estado_v, obs_v, datetime.now().strftime("%d/%m/%Y %H:%M")))
                    else:
                        run("""UPDATE clientes SET nome=%s,nome_completo=%s,telefone=%s,cpf=%s,cep=%s,
                             logradouro=%s,numero=%s,complemento=%s,bairro=%s,cidade=%s,estado=%s,observacoes=%s
                             WHERE id=%s""",
                            (nome_v.strip().lower(), nome_completo_v.strip(), tel_v, cpf_v.strip(),
                             cep_v, logradouro_v, numero_v, complemento_v, bairro_v, cidade_v,
                             estado_v, obs_v, id_edicao))
                    st.session_state.cad_editando_id = None
                    st.session_state.cad_cep_dados   = {}
                    st.toast("✅ Cliente salvo!"); st.rerun()
            if sb2.button("Cancelar", use_container_width=True, key=f"btn_cancelar_cad_{id_edicao}"):
                st.session_state.cad_editando_id = None
                st.session_state.cad_cep_dados   = {}
                st.rerun()

    if st.session_state.cad_editando_id == "NOVO":
        _form_cliente({}, "Salvar Novo Cliente", id_edicao="NOVO")
        st.divider()

    clientes_lista = _carregar_clientes_db()

    if not clientes_lista:
        st.info("Nenhum cliente cadastrado ainda. Clique em **➕ Novo Cliente** para adicionar.")
    else:
        total_cli = len(clientes_lista)
        com_end   = sum(1 for c in clientes_lista if c["cep"])
        com_cpf   = sum(1 for c in clientes_lista if c.get("cpf"))
        mc1,mc2,mc3,mc4 = st.columns(4)
        mc1.metric("Total de Clientes", total_cli)
        mc2.metric("Com Endereço",      com_end)
        mc3.metric("Sem Endereço",      total_cli - com_end)
        mc4.metric("Com CPF",           com_cpf)
        st.divider()

        for cli in clientes_lista:
            nome_exib      = cli["nome"] or ""
            nome_comp_exib = cli["nome_completo"] or ""
            cpf_exib       = cli.get("cpf") or ""
            termos = f"{nome_exib} {nome_comp_exib} {cli['telefone'] or ''} {cpf_exib} {cli['cidade'] or ''} {cli['estado'] or ''}".lower()
            if busca_cad and busca_cad not in termos: continue

            tem_end = bool(cli["cep"]); tem_cpf = bool(cpf_exib)
            badge_end = '<span class="badge badge-ok">✅ Endereço</span>'   if tem_end else '<span class="badge badge-novo">⚠️ Sem endereço</span>'
            badge_cpf = '<span class="badge badge-ok">✅ CPF</span>'        if tem_cpf else '<span class="badge badge-novo">⚠️ Sem CPF</span>'
            titulo_exp = nome_exib.upper() + (f"  ·  {nome_comp_exib}" if nome_comp_exib else "")

            with st.expander(f"{titulo_exp} — {cli['telefone'] or 'S/ Telefone'}"):
                st.markdown(f"{badge_end} &nbsp; {badge_cpf}", unsafe_allow_html=True)
                if st.session_state.cad_editando_id == cli["id"]:
                    if not st.session_state.cad_cep_dados: st.session_state.cad_cep_dados = {}
                    _form_cliente(dict(cli), "Salvar Alterações", id_edicao=cli["id"])
                else:
                    vi1,vi2,vi3,vi4 = st.columns(4)
                    vi1.markdown(f"**@ Instagram:** {nome_exib or '—'}")
                    vi2.markdown(f"**Nome completo:** {nome_comp_exib or '—'}")
                    vi3.markdown(f"**📞 Tel:** {cli['telefone'] or '—'}")
                    vi4.markdown(f"**🪪 CPF:** {_formatar_cpf(cpf_exib) if cpf_exib else '—'}")
                    if tem_end:
                        endereco_formatado = (
                            f"{cli['logradouro']}, {cli['numero']}"
                            + (f" — {cli['complemento']}" if cli["complemento"] else "")
                            + f"\n{cli['bairro']} — {cli['cidade']}/{cli['estado']} — CEP {cli['cep']}"
                        )
                        st.markdown("**📦 Endereço:**"); st.code(endereco_formatado, language=None)
                    else:
                        st.warning("Endereço não cadastrado. Clique em editar para adicionar.")
                    if cli["observacoes"]: st.markdown(f"**📝 Obs:** {cli['observacoes']}")
                    st.caption(f"Cadastro: {cli['data_cadastro'] or '—'}")
                    col_ed, col_del = st.columns(2)
                    if col_ed.button("✏️ Editar", key=f"ed_cli_{cli['id']}", use_container_width=True):
                        st.session_state.cad_editando_id = cli["id"]
                        st.session_state.cad_cep_dados   = {}
                        st.rerun()
                    if col_del.button("🗑️ Excluir", key=f"del_cli_{cli['id']}", use_container_width=True):
                        confirmar_exclusao("cliente_cadastro", cli["id"])
