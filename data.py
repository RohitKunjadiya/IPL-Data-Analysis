import pymysql
import pandas as pd
import streamlit as st


class IPLDatabase:
    def __init__(self):
        self.conn = pymysql.connect(
            host=st.secrets["DB_HOST"],
            port=int(st.secrets["DB_PORT"]),
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor
        )

        self.cursor = self.conn.cursor()

    def _fetch_df(self, query: str) -> pd.DataFrame:
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        columns = [col[0] for col in self.cursor.description]
        return pd.DataFrame(rows, columns=columns)

    def get_seasons_data(self) -> pd.DataFrame:
        return self._fetch_df("SELECT * FROM ipl_seasons_data")

    def get_ball_by_ball_data(self) -> pd.DataFrame:
        df = self._fetch_df("SELECT * FROM ipl_ball_by_ball_data")
        df.rename(columns={'match_id': 'id'}, inplace=True)
        return df

    def close(self):
        self.cursor.close()
        self.conn.close()