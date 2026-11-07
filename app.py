
from pathlib import Path
import json

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Digital DNA | Behavioral Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "curated"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

COLORS = {
    "background": "#0B1220",
    "surface": "#142238",
    "surface_light": "#1B2D46",
    "border": "#294057",
    "primary": "#27D3C3",
    "secondary": "#7C8CFF",
    "text": "#F1F5F9",
    "muted": "#9CAFC5",
    "warning": "#FFCB77"
}

CLUSTER_NAMES = {
    0: "Usage numérique modéré",
    1: "Usage numérique intensif"
}

CLUSTER_COLORS = {
    "Usage numérique modéré": COLORS["primary"],
    "Usage numérique intensif": COLORS["secondary"]
}

METRIC_LABELS = {
    "screen_time_hours": "Temps d'écran",
    "sleep_hours": "Sommeil",
    "steps": "Nombre de pas",
    "social_media_hours": "Réseaux sociaux",
    "productivity_hours": "Productivité",
    "notifications": "Notifications"
}


# ============================================================
# 2. DESIGN GLOBAL
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #0B1220 0%,
            #101D30 100%
        );
        color: #F1F5F9;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        color: #F1F5F9;
        letter-spacing: -0.5px;
    }

    h1 {
        font-weight: 800;
    }

    [data-testid="stSidebar"] {
        background: #101B2D;
        border-right: 1px solid #26354B;
    }

    [data-testid="stMetric"] {
        background: #16263B;
        border: 1px solid #294057;
        border-radius: 15px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #B9C7D8;
    }

    [data-testid="stMetricValue"] {
        color: #27D3C3;
        font-weight: 750;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        background: #16263B;
        border: 1px solid #294057;
        border-radius: 10px;
        padding: 10px 16px;
        color: #B9C7D8;
    }

    .stTabs [aria-selected="true"] {
        color: #27D3C3 !important;
        background: #1B3447;
        border-color: #27D3C3;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #26354B;
    }

    .dna-hero {
        padding: 28px 32px;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            #142A40 0%,
            #172540 55%,
            #20264B 100%
        );
        border: 1px solid #294057;
        margin-bottom: 24px;
    }

    .dna-hero h1 {
        margin: 0 0 10px 0;
        color: #F1F5F9;
        font-size: 2.4rem;
    }

    .dna-hero p {
        color: #B9C7D8;
        margin-bottom: 12px;
        font-size: 1rem;
    }

    .dna-tag {
        display: inline-block;
        padding: 5px 11px;
        margin: 4px 6px 4px 0;
        background: #203B50;
        border: 1px solid #36556B;
        border-radius: 20px;
        color: #7EE9DC;
        font-size: 0.78rem;
    }

    .dna-section {
        color: #F1F5F9;
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 12px;
    }

    .dna-note {
        padding: 14px 18px;
        background: #14283B;
        border-left: 3px solid #27D3C3;
        border-radius: 8px;
        color: #C6D5E5;
        margin-top: 12px;
        margin-bottom: 18px;
    }

    .dna-footer {
        text-align: center;
        color: #8194AA;
        padding-top: 16px;
        font-size: 0.85rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. THEME PLOTLY
# ============================================================

pio.templates.default = "plotly_dark"


def style_chart(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"]),
        margin=dict(l=20, r=20, t=65, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor=COLORS["surface_light"],
            font_color=COLORS["text"]
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(150,170,200,0.10)",
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(150,170,200,0.10)",
        zeroline=False
    )

    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True
    )


def section(title, description=None):
    st.markdown(
        f'<div class="dna-section">{title}</div>',
        unsafe_allow_html=True
    )

    if description:
        st.caption(description)


# ============================================================
# 4. CHARGEMENT DES DONNEES
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv(
        DATA_DIR / "digital_dna_curated.csv",
        parse_dates=["date"]
    )


@st.cache_data
def load_clusters():
    return pd.read_csv(
        DATA_DIR / "user_clusters.csv"
    )


@st.cache_data
def load_pca():
    return pd.read_csv(
        DATA_DIR / "clusters_pca.csv"
    )


@st.cache_resource
def load_model():
    return joblib.load(
        MODEL_DIR / "screen_time_model.joblib"
    )


@st.cache_data
def load_metrics():
    path = REPORT_DIR / "ml_metrics.json"

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


df = load_data()
clusters_df = load_clusters()
pca_df = load_pca()
bundle = load_model()
metrics = load_metrics()

model = bundle["model"]
features = bundle["features"]


# ============================================================
# 5. FONCTIONS DE PREDICTION
# ============================================================

def build_features(user_data, feature_names):
    user_data = user_data.sort_values("date")

    if len(user_data) < 3:
        raise ValueError(
            "Trois jours d'historique sont nécessaires."
        )

    latest = user_data.iloc[-1]
    next_date = latest["date"] + pd.Timedelta(days=1)

    row = {}

    variables = [
        "screen_time_hours",
        "sleep_hours",
        "steps",
        "social_media_hours",
        "notifications",
        "productivity_hours"
    ]

    for variable in variables:
        row[f"{variable}_lag0"] = float(latest[variable])

    for variable in [
        "screen_time_hours",
        "sleep_hours",
        "steps"
    ]:
        row[f"{variable}_rolling3"] = float(
            user_data[variable].tail(3).mean()
        )

    row["target_day_of_week"] = next_date.day_of_week

    X = pd.DataFrame([row])[feature_names]

    return X, next_date


def predict_screen_time(user_data):
    X, next_date = build_features(
        user_data,
        features
    )

    prediction = float(model.predict(X)[0])

    return prediction, next_date


def format_number(value):
    return f"{value:,.0f}".replace(",", " ")


# ============================================================
# 6. BARRE LATERALE
# ============================================================

st.sidebar.title("🧬 Digital DNA")
st.sidebar.caption("BEHAVIORAL INTELLIGENCE")

st.sidebar.divider()

st.sidebar.subheader("Exploration des profils")

user_id = st.sidebar.selectbox(
    "Sélectionner un utilisateur",
    sorted(df["user_id"].unique()),
    format_func=lambda x: f"Utilisateur {x}"
)

user_data = (
    df[df["user_id"] == user_id]
    .sort_values("date")
    .copy()
)

if len(user_data) < 3:
    st.error("Historique insuffisant.")
    st.stop()

cluster_match = clusters_df.loc[
    clusters_df["user_id"] == user_id,
    "cluster"
]

if cluster_match.empty:
    st.error("Profil comportemental introuvable.")
    st.stop()

user_cluster = int(cluster_match.iloc[0])

profile_name = CLUSTER_NAMES.get(
    user_cluster,
    f"Groupe {user_cluster}"
)

cluster_size = int(
    (clusters_df["cluster"] == user_cluster).sum()
)

prediction, prediction_date = predict_screen_time(
    user_data
)

st.sidebar.success(f"Profil : {profile_name}")

st.sidebar.metric(
    "Temps d'écran prédit",
    f"{prediction:.2f} h"
)

st.sidebar.caption(
    f"Prévision du {prediction_date.strftime('%d/%m/%Y')}"
)

st.sidebar.divider()

st.sidebar.write("**Technologies**")
st.sidebar.caption(
    "Python • Pandas • Scikit-learn • "
    "Random Forest • K-Means • PCA • "
    "Plotly • Streamlit"
)

st.sidebar.divider()

st.sidebar.caption(
    "Données synthétiques — Projet académique"
)


# ============================================================
# 7. EN-TETE
# ============================================================

st.markdown(
    """
    <div class="dna-hero">
        <h1>🧬 Digital DNA</h1>
        <p>
            Plateforme intelligente d'analyse,
            de prédiction et de simulation
            des comportements numériques.
        </p>
        <span class="dna-tag">DATA ENGINEERING</span>
        <span class="dna-tag">MACHINE LEARNING</span>
        <span class="dna-tag">DIGITAL TWIN</span>
        <span class="dna-tag">BEHAVIORAL ANALYTICS</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 8. NAVIGATION
# ============================================================

(
    tab_overview,
    tab_profile,
    tab_ml,
    tab_simulation,
    tab_clusters
) = st.tabs([
    "📊 Vue d'ensemble",
    "👤 Profil utilisateur",
    "🧠 Prédictions ML",
    "🎛️ Simulateur",
    "🧬 Clustering & PCA"
])


# ============================================================
# ONGLET 1 — VUE D'ENSEMBLE
# ============================================================

with tab_overview:

    section(
        "Vue d'ensemble",
        "Analyse globale des comportements numériques simulés."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Utilisateurs",
        format_number(df["user_id"].nunique())
    )

    c2.metric(
        "Observations",
        format_number(len(df))
    )

    c3.metric(
        "Jours analysés",
        df["date"].nunique()
    )

    c4.metric(
        "Profils identifiés",
        clusters_df["cluster"].nunique()
    )

    st.divider()

    section("Indicateurs comportementaux globaux")

    g1, g2, g3, g4 = st.columns(4)

    g1.metric(
        "Temps d'écran moyen",
        f"{df['screen_time_hours'].mean():.2f} h"
    )

    g2.metric(
        "Sommeil moyen",
        f"{df['sleep_hours'].mean():.2f} h"
    )

    g3.metric(
        "Pas quotidiens moyens",
        format_number(df["steps"].mean())
    )

    g4.metric(
        "Réseaux sociaux",
        f"{df['social_media_hours'].mean():.2f} h"
    )

    st.divider()

    section("Évolution globale des habitudes")

    daily = (
        df.groupby("date")[
            [
                "screen_time_hours",
                "social_media_hours",
                "sleep_hours"
            ]
        ]
        .mean()
        .reset_index()
    )

    fig_global = px.line(
        daily,
        x="date",
        y=[
            "screen_time_hours",
            "social_media_hours",
            "sleep_hours"
        ],
        color_discrete_sequence=[
            COLORS["primary"],
            COLORS["secondary"],
            COLORS["warning"]
        ],
        labels={
            "date": "Date",
            "value": "Heures",
            "variable": "Indicateur"
        },
        title="Évolution des moyennes quotidiennes"
    )

    show_chart(style_chart(fig_global))

    st.divider()

    section("Répartition des profils comportementaux")

    cluster_counts = (
        clusters_df["cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_counts.columns = [
        "cluster",
        "count"
    ]

    cluster_counts["Profil"] = (
        cluster_counts["cluster"].map(
            CLUSTER_NAMES
        )
    )

    fig_pie = px.pie(
        cluster_counts,
        names="Profil",
        values="count",
        hole=0.55,
        color="Profil",
        color_discrete_map=CLUSTER_COLORS,
        title="Segmentation des 500 utilisateurs"
    )

    fig_pie.update_traces(
        textinfo="percent+label",
        marker=dict(
            line=dict(
                color=COLORS["background"],
                width=3
            )
        )
    )

    show_chart(style_chart(fig_pie, 430))

    st.info(
        "Les comportements présentés sont synthétiques. "
        "Ils ne constituent pas des observations réelles."
    )


# ============================================================
# ONGLET 2 — PROFIL UTILISATEUR
# ============================================================

with tab_profile:

    section(
        f"Profil utilisateur #{user_id}",
        "Analyse individuelle des habitudes numériques."
    )

    st.info(
        f"🧬 Profil comportemental : {profile_name} "
        f"— {cluster_size} utilisateurs dans ce groupe."
    )

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Temps d'écran moyen",
        f"{user_data['screen_time_hours'].mean():.2f} h"
    )

    p2.metric(
        "Sommeil moyen",
        f"{user_data['sleep_hours'].mean():.2f} h"
    )

    p3.metric(
        "Pas quotidiens",
        format_number(user_data["steps"].mean())
    )

    p4.metric(
        "Réseaux sociaux",
        f"{user_data['social_media_hours'].mean():.2f} h"
    )

    st.divider()

    section("Historique des comportements")

    selected_metric = st.selectbox(
        "Choisir un indicateur",
        list(METRIC_LABELS.keys()),
        format_func=lambda x: METRIC_LABELS[x],
        key="history_metric"
    )

    fig_history = px.line(
        user_data,
        x="date",
        y=selected_metric,
        markers=True,
        color_discrete_sequence=[
            COLORS["primary"]
        ],
        title=METRIC_LABELS[selected_metric],
        labels={
            "date": "Date",
            selected_metric: METRIC_LABELS[
                selected_metric
            ]
        }
    )

    fig_history.update_traces(
        line=dict(width=3),
        marker=dict(size=7)
    )

    show_chart(style_chart(fig_history))

    st.divider()

    section("Dernières observations")

    recent = user_data.tail(7)[
        [
            "date",
            "screen_time_hours",
            "sleep_hours",
            "steps",
            "social_media_hours",
            "productivity_hours"
        ]
    ].copy()

    recent["date"] = recent["date"].dt.date

    recent = recent.rename(
        columns={
            "date": "Date",
            "screen_time_hours": "Écran (h)",
            "sleep_hours": "Sommeil (h)",
            "steps": "Pas",
            "social_media_hours": "Réseaux (h)",
            "productivity_hours": "Productivité (h)"
        }
    )

    st.dataframe(
        recent,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# ONGLET 3 — PREDICTIONS ML
# ============================================================

with tab_ml:

    section(
        "Intelligence prédictive",
        "Estimation du temps d'écran du lendemain "
        "avec Random Forest."
    )

    m1, m2, m3 = st.columns(3)

    last_screen = float(
        user_data.iloc[-1]["screen_time_hours"]
    )

    rolling_screen = float(
        user_data["screen_time_hours"]
        .tail(3)
        .mean()
    )

    m1.metric(
        "Dernier temps d'écran",
        f"{last_screen:.2f} h"
    )

    m2.metric(
        "Moyenne sur 3 jours",
        f"{rolling_screen:.2f} h"
    )

    m3.metric(
        f"Prédiction {prediction_date.strftime('%d/%m')}",
        f"{prediction:.2f} h"
    )

    st.divider()

    section("Prédiction vs baseline")

    comparison_prediction = pd.DataFrame({
        "Méthode": [
            "Baseline",
            "Random Forest"
        ],
        "Heures": [
            last_screen,
            prediction
        ]
    })

    fig_prediction = px.bar(
        comparison_prediction,
        x="Méthode",
        y="Heures",
        color="Méthode",
        color_discrete_sequence=[
            COLORS["secondary"],
            COLORS["primary"]
        ],
        text_auto=".2f",
        title="Comparaison des estimations"
    )

    fig_prediction.update_traces(
        textposition="outside"
    )

    show_chart(style_chart(fig_prediction))

    st.caption(
        "La baseline correspond à la dernière "
        "valeur observée, utilisée comme estimation "
        "du lendemain."
    )

    st.divider()

    section("Performances du Random Forest")

    k1, k2, k3 = st.columns(3)

    k1.metric("MAE", "0,6588 h")
    k2.metric("RMSE", "0,8313 h")
    k3.metric("R²", "0,8615")

    st.caption(
        "Évaluation chronologique sur 3 000 "
        "observations de test synthétiques."
    )

    st.divider()

    section("Importance des variables")

    importances = pd.DataFrame({
        "Variable": features,
        "Importance": model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=False
    )

    fig_importance = px.bar(
        importances,
        x="Importance",
        y="Variable",
        orientation="h",
        color="Importance",
        color_continuous_scale=[
            COLORS["surface_light"],
            COLORS["primary"]
        ],
        title="Importance des variables explicatives"
    )

    fig_importance.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        ),
        coloraxis_showscale=False
    )

    show_chart(style_chart(fig_importance, 480))

    st.info(
        "Les performances concernent uniquement "
        "le dataset synthétique du projet. "
        "Elles ne garantissent pas les mêmes "
        "résultats sur des données réelles."
    )


# ============================================================
# ONGLET 4 — SIMULATEUR
# ============================================================

with tab_simulation:

    section(
        "Simulateur comportemental",
        "Explore différents scénarios en modifiant "
        "les dernières habitudes observées."
    )

    st.markdown(
        '<div class="dna-note">'
        "Les curseurs modifient uniquement une copie "
        "des données du dernier jour. "
        "L'historique original reste inchangé."
        '</div>',
        unsafe_allow_html=True
    )

    last = user_data.iloc[-1]

    s1, s2 = st.columns(2)

    with s1:

        sim_screen = st.slider(
            "Temps d'écran (h)",
            min_value=0.0,
            max_value=16.0,
            value=float(last["screen_time_hours"]),
            step=0.1,
            key=f"screen_{user_id}"
        )

        sim_sleep = st.slider(
            "Sommeil (h)",
            min_value=0.0,
            max_value=14.0,
            value=float(last["sleep_hours"]),
            step=0.1,
            key=f"sleep_{user_id}"
        )

    with s2:

        sim_steps = st.slider(
            "Nombre de pas",
            min_value=0,
            max_value=30000,
            value=int(last["steps"]),
            step=100,
            key=f"steps_{user_id}"
        )

        sim_social = st.slider(
            "Réseaux sociaux (h)",
            min_value=0.0,
            max_value=float(sim_screen),
            value=min(
                float(last["social_media_hours"]),
                float(sim_screen)
            ),
            step=0.1,
            key=f"social_{user_id}"
        )

    simulated_data = user_data.copy(deep=True)

    last_index = simulated_data.index[-1]

    simulated_data.loc[
        last_index, "screen_time_hours"
    ] = sim_screen

    simulated_data.loc[
        last_index, "sleep_hours"
    ] = sim_sleep

    simulated_data.loc[
        last_index, "steps"
    ] = sim_steps

    simulated_data.loc[
        last_index, "social_media_hours"
    ] = sim_social

    simulated_prediction, _ = predict_screen_time(
        simulated_data
    )

    delta = simulated_prediction - prediction

    st.divider()

    section("Résultats de la simulation")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Prédiction initiale",
        f"{prediction:.2f} h"
    )

    r2.metric(
        "Prédiction simulée",
        f"{simulated_prediction:.2f} h",
        delta=f"{delta:+.2f} h",
        delta_color="off"
    )

    r3.metric(
        "Écart entre les scénarios",
        f"{delta:+.2f} h"
    )

    simulation_comparison = pd.DataFrame({
        "Scénario": [
            "Initial",
            "Simulé"
        ],
        "Temps d'écran prédit": [
            prediction,
            simulated_prediction
        ]
    })

    fig_simulation = px.bar(
        simulation_comparison,
        x="Scénario",
        y="Temps d'écran prédit",
        color="Scénario",
        text_auto=".2f",
        color_discrete_sequence=[
            COLORS["secondary"],
            COLORS["primary"]
        ],
        title="Impact sur la prédiction du modèle"
    )

    fig_simulation.update_traces(
        textposition="outside"
    )

    show_chart(style_chart(fig_simulation))

    st.warning(
        "Cette simulation mesure la sensibilité "
        "du modèle aux changements de variables. "
        "Elle ne démontre aucune relation causale."
    )


# ============================================================
# ONGLET 5 — CLUSTERING ET PCA
# ============================================================

with tab_clusters:

    section(
        "Segmentation comportementale",
        "Analyse non supervisée avec K-Means "
        "et visualisation PCA."
    )

    st.info(
        f"Utilisateur {user_id} : {profile_name}"
    )

    st.caption(
        f"Cluster {user_cluster} — "
        f"{cluster_size} utilisateurs."
    )

    st.divider()

    section("Comparaison avec le groupe")

    comparison_variables = [
        "screen_time_hours",
        "social_media_hours",
        "sleep_hours",
        "productivity_hours"
    ]

    cluster_profiles = clusters_df[
        clusters_df["cluster"] == user_cluster
    ]

    comparison = pd.DataFrame({
        "Indicateur": [
            "Temps d'écran (h)",
            "Réseaux sociaux (h)",
            "Sommeil (h)",
            "Productivité (h)"
        ],
        "Utilisateur": [
            user_data[col].mean()
            for col in comparison_variables
        ],
        "Moyenne du groupe": [
            cluster_profiles[col].mean()
            for col in comparison_variables
        ]
    })

    st.dataframe(
        comparison.round(2),
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    section("Cartographie des utilisateurs")

    pca_chart = pca_df.copy()

    pca_chart["Profil"] = (
        pca_chart["cluster"].map(
            CLUSTER_NAMES
        )
    )

    fig_pca = px.scatter(
        pca_chart,
        x="PCA_1",
        y="PCA_2",
        color="Profil",
        hover_data=["user_id"],
        color_discrete_map=CLUSTER_COLORS,
        title="Projection PCA des 500 utilisateurs",
        labels={
            "PCA_1": "Composante principale 1",
            "PCA_2": "Composante principale 2"
        }
    )

    fig_pca.update_traces(
        marker=dict(
            size=9,
            opacity=0.75
        )
    )

    selected = pca_chart[
        pca_chart["user_id"] == user_id
    ]

    fig_pca.add_trace(
        go.Scatter(
            x=selected["PCA_1"],
            y=selected["PCA_2"],
            mode="markers",
            marker=dict(
                size=19,
                color="#FF5C7A",
                symbol="star",
                line=dict(
                    color="white",
                    width=2
                )
            ),
            name=f"Utilisateur {user_id}"
        )
    )

    show_chart(style_chart(fig_pca, 520))

    st.caption(
        "Les deux composantes PCA expliquent "
        "76,97 % de la variance des variables "
        "normalisées. L'étoile représente "
        "l'utilisateur sélectionné."
    )

    st.divider()

    section("Caractéristiques des clusters")

    cluster_summary = (
        clusters_df.groupby("cluster")[
            [
                "screen_time_hours",
                "social_media_hours",
                "sleep_hours",
                "steps",
                "notifications",
                "productivity_hours"
            ]
        ]
        .mean()
        .round(2)
        .reset_index()
    )

    cluster_summary["Profil"] = (
        cluster_summary["cluster"].map(
            CLUSTER_NAMES
        )
    )

    st.dataframe(
        cluster_summary,
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "Le score silhouette obtenu est de 0,37. "
        "Il indique une séparation modérée "
        "entre les deux groupes identifiés."
    )


# ============================================================
# 9. PIED DE PAGE
# ============================================================

st.divider()

st.markdown(
    """
    <div class="dna-footer">
        🧬 DIGITAL DNA — BEHAVIORAL INTELLIGENCE PLATFORM
        <p>
            Data Engineering • Machine Learning •
            Digital Twin • Streamlit
        </p>
        <p>
            Projet académique — Données synthétiques uniquement
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
