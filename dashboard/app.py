import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API = "http://localhost:8000/api/v1"

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="VitaVerse",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp{
    background-color:#0B1120;
    color:white;
}

/* Remove default top padding */
.block-container{
    padding-top:2rem;
}

/* ------------------------------
   FULL WIDTH MODERN TABS
--------------------------------*/

.stTabs [data-baseweb="tab-list"]{
    width:100%;
    display:flex;
    gap:12px;
    background:#111827;
    padding:8px;
    border-radius:16px;
    margin-bottom:20px;
}

.stTabs [data-baseweb="tab"]{
    flex:1;
    justify-content:center;
    align-items:center;
    text-align:center;
    height:65px;
    border-radius:12px;
    font-size:18px;
    font-weight:600;
    color:#94A3B8;
    transition:all .3s ease;
}

.stTabs [data-baseweb="tab"]:hover{
    background:#1E293B;
    color:white;
}

.stTabs [aria-selected="true"]{
    background:linear-gradient(
        135deg,
        #2563EB,
        #06B6D4
    ) !important;

    color:white !important;

    box-shadow:
    0 0 15px rgba(37,99,235,.4);
}

/* Hide ugly separator */
.stTabs [data-baseweb="tab-border"]{
    display:none;
}

/* KPI Cards */

[data-testid="metric-container"]{
    background:#111827;
    border:1px solid rgba(255,255,255,0.05);
    padding:18px;
    border-radius:18px;
}

/* Sidebar */

section[data-testid="stSidebar"]{
    background:#111827;
}

/* Charts */

.js-plotly-plot{
    border-radius:18px;
}

/* Buttons */

.stButton > button{
    width:100%;
    height:55px;
    border:none;
    border-radius:12px;
    background:linear-gradient(
        135deg,
        #2563EB,
        #06B6D4
    );
    color:white;
    font-weight:700;
}

.stButton > button:hover{
    transform:translateY(-2px);
}

/* Cards */

.success-card{
    background:#052E16;
    border-left:6px solid #22C55E;
    padding:20px;
    border-radius:12px;
}

.warning-card{
    background:#451A03;
    border-left:6px solid #F59E0B;
    padding:20px;
    border-radius:12px;
}

.danger-card{
    background:#450A0A;
    border-left:6px solid #EF4444;
    padding:20px;
    border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div style='padding:25px;
background:linear-gradient(135deg,#2563EB,#06B6D4);
border-radius:20px;
text-align:center;'>

<h1 style='color:white;'>VitaVerse Healthcare Digital Twin</h1>

<p style='color:white;font-size:18px'>
Predict • Forecast • Simulate • Explain
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Patient Digital Twin")

with st.sidebar.expander("Demographics", expanded=True):

    age = st.slider("Age",20,80,45)

    gender = st.selectbox(
        "Gender",
        [("Male",1),("Female",0)],
        format_func=lambda x:x[0]
    )[1]

with st.sidebar.expander("Clinical Measurements", expanded=True):

    bmi = st.slider("BMI",15.0,50.0,31.0,step=0.5)

    glucose = st.slider(
        "Glucose (mg/dL)",
        70,
        250,
        155
    )

    bp = st.slider(
        "Blood Pressure",
        60,
        180,
        130
    )

    hba1c = st.slider(
        "HbA1c (%)",
        4.0,
        14.0,
        8.2,
        step=0.1
    )

    chol = st.slider(
        "Cholesterol",
        100,
        400,
        240
    )

    insulin = st.slider(
        "Insulin",
        10,
        300,
        120
    )

with st.sidebar.expander("Lifestyle"):

    exercise = st.slider(
        "Exercise (min/day)",
        0,
        120,
        10
    )

    smoking = st.selectbox(
        "Smoking",
        [("Yes",1),("No",0)],
        format_func=lambda x:x[0]
    )[1]

    alcohol = st.selectbox(
        "Alcohol",
        [("Yes",1),("No",0)],
        format_func=lambda x:x[0]
    )[1]

    sleep = st.slider(
        "Sleep Hours",
        3.0,
        12.0,
        5.5,
        step=0.5
    )

    med_adh = st.slider(
        "Medication Adherence",
        0.0,
        1.0,
        0.6,
        step=0.05
    )

patient = {
    "Age": age,
    "Gender": gender,
    "BMI": bmi,
    "Glucose": glucose,
    "BloodPressure": bp,
    "HbA1c": hba1c,
    "Cholesterol": chol,
    "Insulin": insulin,
    "Exercise_min_day": exercise,
    "Smoking": smoking,
    "Alcohol": alcohol,
    "SleepHours": sleep,
    "MedAdherence": med_adh
}

# --------------------------------------------------
# TOP DASHBOARD KPIs
# --------------------------------------------------

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("BMI", bmi)
col2.metric("HbA1c", hba1c)
col3.metric("Glucose", glucose)
col4.metric("Blood Pressure", bp)
col5.metric("Sleep", sleep)

st.divider()

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1,tab2,tab3,tab4 = st.tabs([
    "Risk Analysis",
    "Forecast",
    "Intervention Simulator",
    "Explainability"
])

# ==================================================
# TAB 1
# ==================================================

with tab1:

    st.subheader("Current Disease Risk Assessment")

    if st.button("Analyze Risk", use_container_width=True):

        with st.spinner("Running AI Risk Engine..."):

            try:

                res = requests.post(
                    f"{API}/risk",
                    json=patient,
                    timeout=15
                )

                data = res.json()["data"]

                risk = data["risk_percent"]

                c1,c2 = st.columns([1,1])

                with c1:

                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=risk,
                        title={'text':"Risk Score"},
                        gauge={
                            'axis':{'range':[0,100]},
                            'bar':{'color':'#EF4444'},
                            'steps':[
                                {'range':[0,33],'color':'#22C55E'},
                                {'range':[33,66],'color':'#F59E0B'},
                                {'range':[66,100],'color':'#EF4444'}
                            ]
                        }
                    ))

                    fig.update_layout(
                        template="plotly_dark",
                        height=450
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                with c2:

                    st.metric(
                        "Risk Probability",
                        f"{risk:.2f}%"
                    )

                    st.metric(
                        "Classification",
                        data["risk_label"]
                    )

                    if risk > 70:

                        st.markdown("""
                        <div class='danger-card'>
                        High risk detected. Immediate intervention recommended.
                        </div>
                        """, unsafe_allow_html=True)

                    elif risk > 40:

                        st.markdown("""
                        <div class='warning-card'>
                        Moderate risk. Lifestyle changes advised.
                        </div>
                        """, unsafe_allow_html=True)

                    else:

                        st.markdown("""
                        <div class='success-card'>
                        Healthy profile. Continue current habits.
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:

                st.error(e)

# ==================================================
# TAB 2
# ==================================================

with tab2:

    months = st.slider(
        "Forecast Horizon",
        3,
        36,
        12
    )

    if st.button("Generate Forecast"):

        body = {
            "patient":patient,
            "months":months
        }

        try:

            res = requests.post(
                f"{API}/forecast",
                json=body
            )

            data = res.json()["data"]

            df = pd.DataFrame({
                "Month":data["months"],
                "HbA1c":data["HbA1c"],
                "Glucose":data["Glucose"],
                "BloodPressure":data["BloodPressure"]
            })

            fig = px.line(
                df,
                x="Month",
                y=["HbA1c","Glucose","BloodPressure"],
                markers=True,
                template="plotly_dark",
                title="Patient Health Trajectory"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        except Exception as e:
            st.error(e)

# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.subheader("Lifestyle What-If Analysis")

    c1,c2 = st.columns(2)

    with c1:

        new_exercise = st.slider(
            "Exercise",
            0,
            120,
            45
        )

        new_smoking = st.selectbox(
            "Smoking Status",
            [("Quit",0),("Continue",1)],
            format_func=lambda x:x[0]
        )[1]

    with c2:

        new_med = st.slider(
            "Medication Adherence",
            0.0,
            1.0,
            0.95,
            step=0.05
        )

        new_bmi = st.slider(
            "Target BMI",
            15.0,
            45.0,
            bmi-2,
            step=0.5
        )

    if st.button("Simulate Outcome"):

        body = {
            "patient":patient,
            "interventions":{
                "Exercise_min_day":new_exercise,
                "Smoking":new_smoking,
                "MedAdherence":new_med,
                "BMI":new_bmi
            }
        }

        try:

            res = requests.post(
                f"{API}/simulate",
                json=body
            )

            data = res.json()["data"]

            before = data["original_risk"]["risk_percent"]
            after = data["new_risk"]["risk_percent"]

            fig = go.Figure()

            fig.add_bar(
                x=["Current"],
                y=[before]
            )

            fig.add_bar(
                x=["Improved"],
                y=[after]
            )

            fig.update_layout(
                title="Risk Reduction Analysis",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.success(
                data["recommendation"]
            )

        except Exception as e:
            st.error(e)

# ==================================================
# TAB 4
# ==================================================

with tab4:

    if st.button("Generate Explainability Report"):

        try:

            res = requests.post(
                f"{API}/explain",
                json=patient
            )

            data = res.json()["data"]

            st.info(
                data["explanation_summary"]
            )

            drivers = pd.DataFrame(
                data["top_risk_drivers"]
            )

            fig = px.bar(
                drivers,
                x="impact",
                y="feature",
                orientation="h",
                color="impact",
                template="plotly_dark",
                title="Top Risk Drivers"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(e)