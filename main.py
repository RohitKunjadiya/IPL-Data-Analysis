import streamlit as st
from streamlit_option_menu import option_menu

import team, batter, bowler, points_table, stats, about, model

st.set_page_config(
    page_title="IPL Analysis",
)

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:
            app = option_menu(
                menu_title='IPL Analysis ',
                options=['Score Preditor', 'Points Table','Team Analysis','Batting Analysis','Bowling Analysis','Stats','About'],
                # icons=['trophy-fill', 'house-fill', 'person-circle', 'chat-fill', 'info-circle-fill'],
                menu_icon='cricket',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "15px"},
                    "nav-link": {"color": "white", "font-size": "15px", "text-align": "left", "margin": "0px",
                                 "--hover-color": "#02ab21"},
                    "nav-link-selected": {"background-color": "Blue"}, }
            )

        if app == 'Score Preditor':
            model.app()
        if app == 'Team Analysis':
            team.app()
        if app == 'Batting Analysis':
            batter.app()
        if app == 'Bowling Analysis':
            bowler.app()
        if app == 'Points Table':
            points_table.app()
        if app == 'Stats':
            stats.app()
        if app == 'About':
            about.app()

    run()