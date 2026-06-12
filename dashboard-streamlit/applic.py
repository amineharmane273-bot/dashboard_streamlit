import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard DataViz")
st.caption("Chargez un CSV ou utilisez le dataset de démonstration")

# ── Dataset démo (120 lignes, 20 colonnes) ────────────────────────────────────
@st.cache_data
def load_demo():
    np.random.seed(0)
    n = 120
    return pd.DataFrame({
        "Date"       : pd.date_range("2023-01-01", periods=n, freq="3D"),
        "Ville"      : np.random.choice(["Paris","Lyon","Marseille","Bordeaux","Lille"], n),
        "Produit"    : np.random.choice(["Ordi","Téléphone","Tablette","Accessoire"], n),
        "Segment"    : np.random.choice(["Premium","Standard","Éco"], n),
        "Région"     : np.random.choice(["Nord","Sud","Est","Ouest"], n),
        "Canal"      : np.random.choice(["Web","Magasin","App"], n),
        "Statut"     : np.random.choice(["Actif","Inactif","Prospect"], n),
        "Saison"     : np.random.choice(["Printemps","Été","Automne","Hiver"], n),
        "Sexe"       : np.random.choice(["Homme","Femme"], n),
        "Satisfaction": np.random.choice(["Satisfait","Neutre","Insatisfait"], n),
        "Ventes"     : np.round(np.random.exponential(500, n) + 100, 2),
        "Bénéfice"   : np.round(np.random.normal(150, 80, n), 2),
        "Coût"       : np.round(np.random.uniform(50, 400, n), 2),
        "Quantité"   : np.random.randint(1, 50, n),
        "Prix"       : np.round(np.random.uniform(10, 200, n), 2),
        "Âge"        : np.random.randint(18, 70, n),
        "Ancienneté" : np.random.randint(0, 15, n),
        "Score"      : np.random.randint(0, 10, n),
        "Taux_retour": np.round(np.random.beta(2, 8, n), 3),
        "Marge"      : np.round(np.random.uniform(5, 60, n), 1),
    })

def get_type(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return "Date"
    if pd.api.types.is_numeric_dtype(series):
        return "Quantitative"
    return "Qualitative"

def suggest(tx, ty):
    if ty == "—":
        if tx == "Quantitative": return "Histogramme"
        if tx == "Qualitative":  return "Bar chart"
        if tx == "Date":         return "Line chart"
    if tx == "Date" or ty == "Date":                    return "Line chart"
    if tx == "Quantitative" and ty == "Quantitative":   return "Scatter plot"
    if tx == "Quantitative" and ty == "Qualitative":    return "Boxplot"
    if tx == "Qualitative"  and ty == "Quantitative":   return "Boxplot"
    return "Bar chart"

# ── Données ───────────────────────────────────────────────────────────────────
st.sidebar.header("📂 Données")
source = st.sidebar.radio("Source", ["Dataset démo", "Importer CSV"])

if source == "Importer CSV":
    f = st.sidebar.file_uploader("Fichier CSV", type="csv")
    if f:
        df = pd.read_csv(f)
        for c in df.columns:
            try: df[c] = pd.to_datetime(df[c])
            except: pass
    else:
        st.info("⬆️ Importe un fichier CSV dans la sidebar.")
        st.stop()
else:
    df = load_demo()

st.sidebar.success(f"✅ {len(df)} lignes · {len(df.columns)} colonnes")

col_types = {c: get_type(df[c]) for c in df.columns}
all_cols   = list(df.columns)
quali_cols = [c for c,t in col_types.items() if t == "Qualitative"]

# ── Filtre simple ─────────────────────────────────────────────────────────────
st.sidebar.header("🔧 Filtre")
filtre_col = st.sidebar.selectbox("Filtrer par", ["—"] + quali_cols)
df_f = df.copy()
if filtre_col != "—":
    vals = st.sidebar.multiselect(
        f"Valeurs de {filtre_col}",
        options=df[filtre_col].unique().tolist(),
        default=df[filtre_col].unique().tolist()
    )
    df_f = df_f[df_f[filtre_col].isin(vals)]

# ── Métriques ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Lignes", len(df_f))
c2.metric("Colonnes", len(df.columns))
c3.metric("Après filtre", f"{len(df_f)} / {len(df)}")

st.divider()

# ── Sélection ─────────────────────────────────────────────────────────────────
st.subheader("🎛️ Choisir les variables")
col1, col2, col3 = st.columns(3)

with col1:
    x = st.selectbox("Variable X", all_cols)
with col2:
    y_opts = ["—"] + [c for c in all_cols if c != x]
    y = st.selectbox("Variable Y (optionnelle)", y_opts)
with col3:
    tx = col_types[x]
    ty = col_types[y] if y != "—" else "—"
    auto = suggest(tx, ty)
    charts = ["Histogramme", "Bar chart", "Scatter plot", "Boxplot", "Line chart"]
    chart = st.selectbox("Type de graphique", charts, index=charts.index(auto))
    st.caption(f"💡 Suggestion : **{auto}**")

# ── Titre dynamique ───────────────────────────────────────────────────────────
titre = f"{chart} — {x}" if y == "—" else f"{chart} — {x} × {y}"
st.subheader(titre)
st.caption(f"X : **{tx}** | Y : **{ty}** | {len(df_f):,} lignes")

# ── Graphique ─────────────────────────────────────────────────────────────────
try:
    kw = dict(template="plotly_white")

    if chart == "Histogramme":
        fig = px.histogram(df_f, x=x, nbins=25, marginal="box", **kw)

    elif chart == "Bar chart":
        tmp = df_f[x].value_counts().reset_index()
        tmp.columns = [x, "Effectif"]
        fig = px.bar(tmp, x=x, y="Effectif", **kw)

    elif chart == "Scatter plot":
        fig = px.scatter(df_f, x=x, y=y, trendline="ols", opacity=0.7, **kw)

    elif chart == "Boxplot":
        quali = x if tx == "Qualitative" else y
        quanti = y if tx == "Qualitative" else x
        fig = px.box(df_f, x=quali, y=quanti, points="outliers", **kw)

    elif chart == "Line chart":
        date_c = x if tx == "Date" else y
        val_c  = y if tx == "Date" else x
        if val_c == "—":
            st.warning("Sélectionne une variable Y pour le Line chart.")
            st.stop()
        agg = df_f.groupby(date_c)[val_c].mean().reset_index()
        fig = px.line(agg, x=date_c, y=val_c, markers=True, **kw)

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur : {e}")
    st.info("💡 Essaie une autre combinaison de variables.")

# ── Aperçu ────────────────────────────────────────────────────────────────────
with st.expander("🗃️ Voir les données"):
    st.dataframe(df_f.head(30), use_container_width=True)