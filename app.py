"""
Sistema de Inteligência Comercial S.E.U.
Rastro da Raiva + Rastro do Dinheiro → Análise S.E.U.
Criado para Henrique Guimarães | Março 2026
"""

import streamlit as st
import anthropic
import requests
import time
import json
from datetime import datetime

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema S.E.U. — Inteligência Comercial",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .main-title {
        font-size: 2.2rem; font-weight: 800; color: #FFFFFF;
        text-align: center; margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem; color: #8B9CBD; text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E5FA3 100%);
        border-radius: 12px; padding: 20px; margin: 8px 0;
    }
    .raiva-box {
        background: #1a0000; border-left: 4px solid #C0392B;
        border-radius: 8px; padding: 16px; margin: 8px 0;
    }
    .dinheiro-box {
        background: #001a0a; border-left: 4px solid #27AE60;
        border-radius: 8px; padding: 16px; margin: 8px 0;
    }
    .seu-box {
        background: #0d1b2a; border: 1px solid #2E5FA3;
        border-radius: 12px; padding: 20px; margin: 12px 0;
    }
    .fonte-tag {
        background: #1e2a3a; color: #8B9CBD; font-size: 0.75rem;
        padding: 2px 8px; border-radius: 4px; margin: 2px;
        display: inline-block;
    }
    .insight-item {
        color: #E0E0E0; font-size: 0.9rem;
        padding: 6px 0; border-bottom: 1px solid #1e2a3a;
    }
    div[data-testid="stExpander"] {
        background: #161b22; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Prompt do Sistema (Método S.E.U.) ───────────────────────────────────────
SYSTEM_PROMPT = """Você é o Sistema de Inteligência Comercial S.E.U., especializado em identificar o "Rastro da Raiva" e o "Rastro do Dinheiro" em qualquer mercado.

Seu trabalho: analisar dados brutos de buscas sobre um nicho e entregar uma análise estruturada no Método S.E.U. (Saída de Emergência Única).

DEFINIÇÕES FUNDAMENTAIS:
- RASTRO DA RAIVA: Frustrações reais e não resolvidas. Não são reclamações óbvias — são o espaço onde pessoas JÁ SÃO CONSCIENTES do problema mas ainda não encontraram solução satisfatória. É onde o cliente já gasta energia emocional sem resultado.
- RASTRO DO DINHEIRO: Onde as pessoas JÁ DECIDIRAM gastar. Não o que elas dizem que querem — o que elas efetivamente pagam. Como diria Eugene Schwartz: não criamos o desejo, apenas o direcionamos.

ESTRUTURA DE SAÍDA OBRIGATÓRIA (em JSON válido):

{
  "resumo_executivo": "2-3 frases descrevendo o estado real do mercado com base nos dados",

  "rastro_raiva": {
    "frustracao_principal": "A maior frustração não resolvida do mercado — específica e visceral",
    "insights": [
      {"texto": "Insight específico 1", "intensidade": "ALTA/MÉDIA/BAIXA", "evidencia": "Trecho ou padrão encontrado nos dados"},
      {"texto": "Insight específico 2", "intensidade": "ALTA/MÉDIA/BAIXA", "evidencia": "Trecho ou padrão encontrado nos dados"},
      {"texto": "Insight específico 3", "intensidade": "ALTA/MÉDIA/BAIXA", "evidencia": "Trecho ou padrão encontrado nos dados"}
    ],
    "o_que_os_clientes_odeiam_dizer_mas_pensam": "A frase que o cliente do nicho pensa mas não diz para o prestador"
  },

  "rastro_dinheiro": {
    "onde_o_dinheiro_esta_indo": "Descrição do fluxo principal de dinheiro no mercado",
    "insights": [
      {"texto": "Onde/como pagam 1", "evidencia": "Padrão encontrado nos dados"},
      {"texto": "Onde/como pagam 2", "evidencia": "Padrão encontrado nos dados"},
      {"texto": "Onde/como pagam 3", "evidencia": "Padrão encontrado nos dados"}
    ],
    "oportunidade_nao_atendida": "O que as pessoas claramente precisam mas ainda não há oferta adequada"
  },

  "analise_seu": {
    "emergencia": "O INCÊNDIO: A situação urgente e real que o especialista do nicho pode revelar ao cliente — baseada nos dados, não em promessas genéricas",
    "unica": "A INVALIDAÇÃO LÓGICA: O argumento específico que destrói as soluções comuns e posiciona o especialista como única saída racional — baseado nas frustrações identificadas",
    "saida": "A MENSAGEM DE POSICIONAMENTO: A frase de 1-2 linhas que o especialista deve usar para ser compreendido em 3 segundos pelo cliente ideal"
  },

  "sugestao_oferta": "Uma sugestão concreta de como estruturar uma oferta premium (R$15k+) baseada nesses dados específicos",

  "alertas": ["Qualquer padrão preocupante ou oportunidade urgente encontrada nos dados"]
}

IMPORTANTE:
- Seja ESPECÍFICO. "Clientes insatisfeitos com atendimento" é inútil. "Clientes de consultores jurídicos odeiam pagar R$500/hora e descobrir na terceira reunião que o problema era simples" é útil.
- Base TUDO nos dados fornecidos. Se um dado não suporta uma afirmação, não faça a afirmação.
- Escreva em português brasileiro direto. Zero jargão acadêmico.
- Retorne APENAS o JSON válido, sem texto antes ou depois."""

# ─── Funções de busca ─────────────────────────────────────────────────────────

def buscar_duckduckgo(query: str, max_results: int = 8) -> list[dict]:
    """Busca via DuckDuckGo sem necessidade de API key."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=max_results, region="br-pt"))
        return resultados
    except Exception as e:
        return [{"title": f"Erro na busca: {str(e)}", "body": "", "href": ""}]

def buscar_reddit(query: str, limite: int = 8) -> list[dict]:
    """Busca no Reddit via API pública (sem autenticação)."""
    try:
        headers = {"User-Agent": "SistemaInteligenciaSEU/1.0 (análise de mercado)"}
        url = f"https://www.reddit.com/search.json?q={requests.utils.quote(query)}&sort=relevance&t=year&limit={limite}&type=link"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            posts = dados.get("data", {}).get("children", [])
            return [
                {
                    "title": p["data"].get("title", ""),
                    "body": p["data"].get("selftext", "")[:400],
                    "href": f"https://reddit.com{p['data'].get('permalink', '')}",
                    "score": p["data"].get("score", 0)
                }
                for p in posts if p["data"].get("score", 0) > 0
            ]
        return []
    except Exception as e:
        return [{"title": f"Erro Reddit: {str(e)}", "body": "", "href": ""}]

def buscar_reclameaqui(nicho: str) -> list[dict]:
    """Busca reclamações via DuckDuckGo filtrado no Reclame Aqui."""
    query = f"site:reclameaqui.com.br {nicho} reclamação problema"
    return buscar_duckduckgo(query, max_results=5)

def coletar_dados(nicho: str, progresso_callback=None) -> dict:
    """Coleta dados de múltiplas fontes para o nicho informado."""

    dados = {
        "nicho": nicho,
        "fontes": {},
        "total_resultados": 0
    }

    buscas = [
        ("raiva_geral",      f"reclamação {nicho} insatisfeito problema decepção",           "DuckDuckGo — Raiva"),
        ("raiva_reclame",    f"site:reclameaqui.com.br {nicho}",                             "Reclame Aqui"),
        ("dinheiro_precos",  f"{nicho} quanto custa preço contratar valor investimento",     "DuckDuckGo — Preço"),
        ("dinheiro_trends",  f"melhor {nicho} recomendação vale a pena contratar 2025",       "DuckDuckGo — Tendências"),
        ("reddit_br",        f"{nicho} experiência reclamação problema Brasil",              "Reddit Brasil"),
        ("raiva_reviews",    f"{nicho} avaliação negativa ruim não recomendo experiência",   "DuckDuckGo — Reviews"),
    ]

    for i, (chave, query, fonte) in enumerate(buscas):
        if progresso_callback:
            progresso_callback(i / len(buscas), f"🔍 Buscando: {fonte}…")

        if chave == "reddit_br":
            resultados = buscar_reddit(query)
        else:
            resultados = buscar_duckduckgo(query)

        dados["fontes"][chave] = {
            "fonte": fonte,
            "query": query,
            "resultados": resultados
        }
        dados["total_resultados"] += len(resultados)
        time.sleep(0.3)  # evitar rate limit

    if progresso_callback:
        progresso_callback(1.0, "✅ Coleta concluída!")

    return dados

def formatar_dados_para_claude(dados: dict) -> str:
    """Formata os dados coletados em texto estruturado para o Claude analisar."""

    texto = f"NICHO ANALISADO: {dados['nicho']}\n"
    texto += f"Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
    texto += "=" * 60 + "\n"
    texto += "DADOS COLETADOS DE MÚLTIPLAS FONTES:\n"
    texto += "=" * 60 + "\n\n"

    for chave, info in dados["fontes"].items():
        texto += f"--- FONTE: {info['fonte']} ---\n"
        texto += f"Busca: \"{info['query']}\"\n\n"

        for r in info["resultados"]:
            titulo = r.get("title", "").strip()
            corpo  = r.get("body", "").strip()
            url    = r.get("href", "")
            if titulo:
                texto += f"• [{titulo}]({url})\n"
            if corpo:
                texto += f"  {corpo[:300]}\n"
            texto += "\n"

        texto += "\n"

    return texto

def analisar_com_claude(dados_formatados: str, api_key: str) -> dict:
    """Chama o Claude para gerar a análise S.E.U."""

    cliente = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Analise os seguintes dados coletados sobre um nicho de mercado e gere a análise S.E.U. completa:

{dados_formatados}

Lembre: retorne APENAS o JSON válido conforme a estrutura definida."""

    resposta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    texto_resposta = resposta.content[0].text.strip()

    # Limpar possíveis ```json ... ``` wrappers
    if texto_resposta.startswith("```"):
        linhas = texto_resposta.split("\n")
        texto_resposta = "\n".join(linhas[1:-1])

    return json.loads(texto_resposta)

# ─── Interface Streamlit ──────────────────────────────────────────────────────

def cor_intensidade(intensidade: str) -> str:
    mapa = {"ALTA": "#C0392B", "MÉDIA": "#E67E22", "BAIXA": "#F1C40F"}
    return mapa.get(intensidade.upper(), "#888888")

def renderizar_resultado(analise: dict, nicho: str):
    """Renderiza o resultado completo da análise."""

    st.markdown("---")
    st.markdown(f"## 📊 Análise S.E.U. — {nicho}")

    # Resumo executivo
    st.markdown(f"""
    <div class="metric-box">
        <div style="color: #8B9CBD; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Resumo Executivo</div>
        <div style="color: #FFFFFF; font-size: 1.05rem; margin-top: 8px; line-height: 1.6;">
            {analise.get('resumo_executivo', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ── Rastro da Raiva ───────────────────────────────────────────────────────
    with col1:
        st.markdown("### 🔴 Rastro da Raiva")
        raiva = analise.get("rastro_raiva", {})

        st.markdown(f"""
        <div class="raiva-box">
            <div style="color: #FF6B6B; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">
                Frustração Principal
            </div>
            <div style="color: #FFFFFF; margin-top: 8px; font-size: 0.95rem; line-height: 1.5;">
                {raiva.get('frustracao_principal', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        for insight in raiva.get("insights", []):
            intensidade = insight.get("intensidade", "MÉDIA")
            cor = cor_intensidade(intensidade)
            st.markdown(f"""
            <div style="background: #1a1a2e; border-radius: 8px; padding: 12px; margin: 6px 0;">
                <span style="background: {cor}; color: white; font-size: 0.7rem; padding: 2px 8px;
                      border-radius: 4px; font-weight: 700;">{intensidade}</span>
                <div style="color: #E0E0E0; margin-top: 8px; font-size: 0.9rem;">{insight.get('texto', '')}</div>
                <div style="color: #6B7DB3; font-size: 0.8rem; margin-top: 6px; font-style: italic;">
                    📍 {insight.get('evidencia', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        frase = raiva.get("o_que_os_clientes_odeiam_dizer_mas_pensam", "")
        if frase:
            st.markdown(f"""
            <div style="background: #2d0a0a; border: 1px dashed #C0392B; border-radius: 8px; padding: 14px; margin-top: 12px;">
                <div style="color: #FF6B6B; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">
                    💬 O que pensam mas não dizem
                </div>
                <div style="color: #FFCDD2; font-style: italic; font-size: 0.95rem;">"{frase}"</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Rastro do Dinheiro ────────────────────────────────────────────────────
    with col2:
        st.markdown("### 💰 Rastro do Dinheiro")
        dinheiro = analise.get("rastro_dinheiro", {})

        st.markdown(f"""
        <div class="dinheiro-box">
            <div style="color: #4CAF50; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">
                Fluxo Principal
            </div>
            <div style="color: #FFFFFF; margin-top: 8px; font-size: 0.95rem; line-height: 1.5;">
                {dinheiro.get('onde_o_dinheiro_esta_indo', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        for insight in dinheiro.get("insights", []):
            st.markdown(f"""
            <div style="background: #0a1a10; border-radius: 8px; padding: 12px; margin: 6px 0;">
                <div style="color: #81C784; font-size: 0.9rem;">{insight.get('texto', '')}</div>
                <div style="color: #4a7c59; font-size: 0.8rem; margin-top: 6px; font-style: italic;">
                    📍 {insight.get('evidencia', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        oportunidade = dinheiro.get("oportunidade_nao_atendida", "")
        if oportunidade:
            st.markdown(f"""
            <div style="background: #0a2d15; border: 1px dashed #27AE60; border-radius: 8px; padding: 14px; margin-top: 12px;">
                <div style="color: #4CAF50; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">
                    🚀 Oportunidade Não Atendida
                </div>
                <div style="color: #C8E6C9; font-size: 0.95rem;">{oportunidade}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Análise S.E.U. ────────────────────────────────────────────────────────
    st.markdown("### 🎯 Análise S.E.U.")
    seu = analise.get("analise_seu", {})

    col_e, col_u, col_s = st.columns(3)

    with col_e:
        st.markdown(f"""
        <div class="seu-box">
            <div style="color: #E74C3C; font-size: 1.1rem; font-weight: 800; margin-bottom: 10px;">
                🔥 EMERGÊNCIA
            </div>
            <div style="color: #E0E0E0; font-size: 0.9rem; line-height: 1.6;">
                {seu.get('emergencia', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_u:
        st.markdown(f"""
        <div class="seu-box">
            <div style="color: #3498DB; font-size: 1.1rem; font-weight: 800; margin-bottom: 10px;">
                🔒 ÚNICA
            </div>
            <div style="color: #E0E0E0; font-size: 0.9rem; line-height: 1.6;">
                {seu.get('unica', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_s:
        st.markdown(f"""
        <div class="seu-box">
            <div style="color: #2ECC71; font-size: 1.1rem; font-weight: 800; margin-bottom: 10px;">
                🚪 SAÍDA
            </div>
            <div style="color: #E0E0E0; font-size: 0.9rem; line-height: 1.6;">
                {seu.get('saida', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Sugestão de Oferta ────────────────────────────────────────────────────
    sugestao = analise.get("sugestao_oferta", "")
    if sugestao:
        st.markdown("### 💡 Sugestão de Oferta Premium")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1B3A6B 0%, #0d2137 100%);
             border: 1px solid #2E5FA3; border-radius: 12px; padding: 20px; margin: 8px 0;">
            <div style="color: #FFFFFF; font-size: 1rem; line-height: 1.7;">{sugestao}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Alertas ───────────────────────────────────────────────────────────────
    alertas = analise.get("alertas", [])
    if alertas:
        st.markdown("### ⚠️ Alertas e Oportunidades Urgentes")
        for alerta in alertas:
            st.warning(alerta)

    # ── Exportar JSON ─────────────────────────────────────────────────────────
    with st.expander("📥 Ver / Exportar JSON completo"):
        st.json(analise)
        st.download_button(
            label="⬇️ Baixar análise em JSON",
            data=json.dumps(analise, ensure_ascii=False, indent=2),
            file_name=f"analise_seu_{nicho.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuração")

    api_key = st.text_input(
        "🔑 Claude API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Obtenha em console.anthropic.com — plano gratuito disponível"
    )

    st.markdown("---")
    st.markdown("### 📖 O que é este sistema?")
    st.markdown("""
    O **Sistema S.E.U.** encontra:

    🔴 **Rastro da Raiva**
    As frustrações reais e não resolvidas dos clientes de um mercado — onde há dor ativa sem solução.

    💰 **Rastro do Dinheiro**
    Onde as pessoas JÁ decidiram gastar — o desejo que só precisa ser redirecionado.

    🎯 **Análise S.E.U.**
    Emergência + Única + Saída — o posicionamento irresistível baseado em dados reais.
    """)

    st.markdown("---")
    st.markdown("### 🔗 Fontes de dados")
    st.markdown("""
    - 🦆 DuckDuckGo (busca web)
    - 🗣️ Reddit Brasil
    - 📋 Reclame Aqui (via busca)
    - 🤖 Claude (síntese S.E.U.)
    """)

    st.markdown("---")
    st.markdown("<div style='color: #555; font-size: 0.75rem;'>Método S.E.U. — Henrique Guimarães © 2026</div>", unsafe_allow_html=True)

# ─── Corpo principal ──────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎯 Sistema de Inteligência Comercial S.E.U.</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Rastro da Raiva + Rastro do Dinheiro → Saída de Emergência Única</div>', unsafe_allow_html=True)

# Formulário de entrada
with st.container():
    col_input, col_btn = st.columns([4, 1])

    with col_input:
        nicho = st.text_input(
            "🏢 Nicho de mercado a analisar",
            placeholder="Ex: consultores de RH, arquitetos residenciais, advogados trabalhistas...",
            help="Quanto mais específico, mais precisa a análise. Ex: 'consultores de marketing digital para clínicas médicas'"
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analisar = st.button("🔍 Analisar", type="primary", use_container_width=True)

# Exemplos rápidos
st.markdown("**Exemplos rápidos:**")
exemplos = ["consultores de TI para PMEs", "advogados trabalhistas", "arquitetos residenciais", "contadores para pequenas empresas", "coaches executivos"]
cols_exemplos = st.columns(len(exemplos))
for i, (col, exemplo) in enumerate(zip(cols_exemplos, exemplos)):
    with col:
        if st.button(f"_{exemplo}_", key=f"ex_{i}", help=f"Analisar: {exemplo}"):
            nicho = exemplo
            analisar = True

# ─── Execução da análise ──────────────────────────────────────────────────────
if analisar and nicho:
    if not api_key:
        st.error("⚠️ Insira sua Claude API Key na barra lateral para continuar.")
        st.info("💡 Obtenha sua chave gratuita em: https://console.anthropic.com")
        st.stop()

    st.markdown("---")
    placeholder_status = st.empty()
    barra_progresso   = st.progress(0)

    try:
        # Fase 1: Coleta
        def atualizar_progresso(valor, mensagem):
            barra_progresso.progress(valor * 0.6)
            placeholder_status.markdown(f"**{mensagem}**")

        with st.spinner(""):
            dados = coletar_dados(nicho, atualizar_progresso)

        # Fase 2: Síntese com Claude
        placeholder_status.markdown("**🤖 Claude analisando os dados com o Método S.E.U.…**")
        barra_progresso.progress(0.75)

        dados_formatados = formatar_dados_para_claude(dados)
        analise = analisar_com_claude(dados_formatados, api_key)

        barra_progresso.progress(1.0)
        placeholder_status.markdown(f"**✅ Análise concluída — {dados['total_resultados']} resultados processados de {len(dados['fontes'])} fontes**")

        # Fase 3: Exibir resultado
        renderizar_resultado(analise, nicho)

    except json.JSONDecodeError as e:
        st.error(f"Erro ao interpretar resposta do Claude: {e}")
        st.info("Tente novamente — o modelo às vezes retorna texto extra. Se persistir, verifique a API key.")

    except anthropic.AuthenticationError:
        st.error("❌ API Key inválida. Verifique sua chave em console.anthropic.com")

    except anthropic.RateLimitError:
        st.error("⏳ Limite de requisições atingido. Aguarde 1 minuto e tente novamente.")

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        with st.expander("Detalhes técnicos"):
            import traceback
            st.code(traceback.format_exc())

elif analisar and not nicho:
    st.warning("⚠️ Digite o nicho que deseja analisar.")
