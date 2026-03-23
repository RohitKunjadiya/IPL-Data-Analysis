import streamlit as st
from teamAnalysis import IPL
from modelCreation import IPLPredictor


@st.cache_resource
def load_predictor():
    predictor = IPLPredictor()
    predictor.fit()
    return predictor

@st.cache_resource
def load_ipl():
    return IPL()


def app():
    ipl = load_ipl()
    predictor = load_predictor()

    teams = ipl.playing_teams()
    cities = ipl.cities()

    st.title('🏏 IPL Score Predictor')

    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox('Batting Team', teams)
        over = st.number_input('Over No.', min_value=1.0, max_value=20.0, step=1.0, value=10.0)
        runs = st.number_input('Runs Scored', min_value=0, max_value=400, value=80)

    with col2:
        bowling_team = st.selectbox('Bowling Team', teams)
        wckts = st.number_input('Wickets Fallen', min_value=0, max_value=7, value=2)
        city  = st.selectbox('City / Stadium', cities)

    toss_dec = st.radio('Toss Decision', ['bat', 'field'], horizontal=True)

    if st.button('Predict Score', use_container_width=True):
        if batting_team == bowling_team:
            st.warning('Batting and bowling team cannot be the same.')
        else:
            score = predictor.predict_score(
                batting_team=batting_team,
                bowling_team=bowling_team,
                over=over,
                cum_runs=runs,
                cum_wickets=wckts,
                city=city,
                toss_dec=toss_dec
            )
            st.success(f'🏏 Predicted Final Score: **{score:.0f}**')