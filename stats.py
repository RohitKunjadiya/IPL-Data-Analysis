import streamlit as st
from statAnalysis import Stats

def app():

    stat = Stats()

    st.title('IPL Stats:')

    st.subheader("Win Percentage of IPL Teams:")
    st.dataframe(stat.win_percentage(),width=620,height=562)

    st.subheader('Batting Partners:')
    st.table(stat.partnerships())

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Most 4's:")
        st.dataframe(stat.fours(),column_config={'BatsmanRun':'Fours'},width=350)

    with col2:
        st.subheader("Most 6's:")
        st.dataframe(stat.sixes(),column_config={'BatsmanRun':'Sixes'},width=350)