import streamlit as st

def app():
    st.title("About Data")
    st.subheader("The dataset used in this project is a combination of publicly available data and self-collected data. IPL match-level information was scraped from ESPNcricinfo, while detailed ball-by-ball data was sourced from Cricsheet. This combined dataset enables in-depth analysis and predictive modeling.")

    st.write("\n\n\n\n---------------------------------------------------------------------")

    st.title("About Project ")
    st.subheader("""
        The IPL Data Analysis project meticulously examines the Indian Premier League's comprehensive dataset from 2008 to 2025.This project aims to provide an in-depth understanding of various aspects of the tournament through detailed insights and statistical analysis.
        """)
    
    st.markdown("<h4> 1. IPL Score Predictor </h4>", unsafe_allow_html=True)
    st.markdown("""
                \t - This IPL Score Predictor uses Machine Learning models trained on historical match data to estimate the final score of an innings.
                \t - The prediction is based on inputs like batting team, bowling team, current runs, overs completed, and wickets fallen.
            """)
    st.markdown("<h4> 2. Team vs Team Analysis </h4>", unsafe_allow_html=True)
    st.markdown("""
                           \t - Detailed head-to-head records.
                           \t - Win/loss/NR(No Result) Pie Chart of h2h team and individual team 
                           \t - Performance of team till 2024.
            """)
    st.markdown("<h4> 3. Batting Analysis </h4>", unsafe_allow_html=True)

    st.markdown("""
                               \t - Individual player performances.
                               \t - Runs made by batter against each team.
                               \t - Runs made by batter in each season.
                               \t - Statistics on Total Runs and Strike Rates.
                               \t - Orange Cap Holder in each season.
                """)
    st.markdown("<h4> 4. Bowling Analysis </h4>", unsafe_allow_html=True)
    st.markdown("""
                                   \t - Leading wicket-takers.
                                   \t - Wickets of bowler against each team.
                                   \t - Wickets of bowler in each season.
                                   \t - Purple Cap Holder in each season.
                                   \t - Best Bowling figure and total wickets of bowler
                    """)
    st.markdown("<h4> 5. Points Table </h4>", unsafe_allow_html=True)
    st.markdown("""
                                       \t - Yearly standings and points accumulation.
                                       \t - Qualification scenarios and playoff performances.
                                       \t - Team performances across seasons.
                        """)
    st.markdown("<h4> 6. IPL Stats </h4>", unsafe_allow_html=True)
    st.markdown("""
                                           \t - Good Batting Partners: Identifying the most successful batting pairs in IPL history.
                                           \t - Home and Away Win Percentages
                                           \t - Most 4s and 6s
                            """)
