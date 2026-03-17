import streamlit as st
from bowlingAnalysis import Bowlers
import plotly.express as px

def app():

    # st.title("Bowler's Performance")
    player=Bowlers()

    ip1 = st.sidebar.selectbox('Enter Batter Name:', player.batter())
    ip = st.sidebar.selectbox('Enter Bowler Name:', player.bowler())

    btn = st.sidebar.button('Show')
    if btn:
        st.subheader('Batter Vs Bowler')
        st.write(ip1,'Vs',ip)
        st.write(player.batterVsbowler(ip1,ip))

        st.subheader("Bowler's Performance in IPL till 2024")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Total Wickets:')
            st.subheader(player.bowler_wickets(ip))

        with col2:
            st.subheader('Best Bowling Figure:')
            st.write(player.best_figure(ip))

        fig = px.bar(player.wicket_against_teamChart(ip), x='batting_team', y='Wickets',
                     title="Visual Representation of Bowler's Performance Against Each Team")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig)


        fig = px.bar(player.wickets_seasonwiseChart(ip), x='season', y='Wickets',
                     title="Visual Representation of Bowler's Wickets Each Season")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top-10 Wicket-Takers in IPL till 2024: ')
            st.dataframe(player.wickets(),column_config={'Kind':'Wickets'},width=290)

        with col2:
            st.subheader('Top-10 Battles in IPL till 2024:')
            st.dataframe(player.h2h_bowler(),column_config={'BatsmanRun':'Runs'},width=410)

        st.subheader('Purple-Cap Holder:')
        st.dataframe(player.purple_cap(),column_config={'IsWicketDelivery':'Wickets','bowlers_run':'Runs Conceded','islegelball':'Balls'},width=800,height=633)