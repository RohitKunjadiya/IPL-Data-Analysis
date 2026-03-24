import pymysql
import pandas as pd


class Database:

    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="host,
                port='port,
                user="username",
                password="password",
                database="db_name"
            )

            self.cursor = self.conn.cursor()
            print('Connection Established!')

            self.cursor.execute('USE railway;')

            create_table_query_1 = """
            CREATE TABLE IF NOT EXISTS ipl_seasons_data (
                url VARCHAR(255),
                id INT PRIMARY KEY,
                city VARCHAR(255),
                date DATE,
                season VARCHAR(255),
                match_number VARCHAR(255),
                team1 VARCHAR(255),
                team2 VARCHAR(255),
                toss_winner VARCHAR(255),
                toss_decision VARCHAR(255),
                winning_team VARCHAR(255),
                margin VARCHAR(255),
                won_by VARCHAR(255),
                player_of_match VARCHAR(255),
                team1players json,
                team2players json
            );
            """
            self.cursor.execute(create_table_query_1)

            create_table_query_2 = """
            CREATE TABLE IF NOT EXISTS ipl_ball_by_ball_data (
                match_id INT,
                innings INT,
                overs INT,
                ball_number INT,
                batter VARCHAR(255),
                bowler VARCHAR(255),
                non_striker VARCHAR(255),
                extra_type VARCHAR(255),
                batsman_run INT,
                extras_run INT,
                total_run INT,
                is_wicket_delivery INT,
                player_out VARCHAR(255),
                kind VARCHAR(255),
                fielders_involved VARCHAR(255),
                batting_team VARCHAR(255),
                bowling_team VARCHAR(255),
                PRIMARY KEY (match_id, innings, overs, ball_number),
                FOREIGN KEY (match_id) REFERENCES ipl_seasons_data(id)
            );
            """

            self.cursor.execute(create_table_query_2)

        except pymysql.MySQLError as err:
            print(f'Error connecting to MySQL: {err}')
            exit()

    def insert_match(self, data):
        try:
            insert_query_1 = """
            INSERT INTO ipl_seasons_data 
            (url, id, city, date, season, match_number, team1, team2, toss_winner, toss_decision, 
            winning_team, margin, won_by, player_of_match, team1players, team2players)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id;
            """

            values = (
                data["url"],
                data["id"],
                data["city"],
                data["date"],
                data["season"],
                data["match_number"],
                data["team1"],
                data["team2"],
                data["toss_winner"],
                data["toss_decision"],
                data["winning_team"],
                data["margin"],
                data["won_by"],
                data["player_of_match"],
                data['team1players'],
                data['team2players']
            )

            self.cursor.execute(insert_query_1, values)

            insert_query_2 = """
            INSERT INTO ipl_ball_by_ball_data
            (match_id, innings, overs, ball_number, batter, bowler, non_striker, extra_type, batsman_run, extras_run, total_run, is_wicket_delivery, player_out, kind, fielders_involved, batting_team, bowling_team)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE match_id=match_id;
            """
            ball_values_list = [
                (
                    data["id"],
                    ball.get("Innings"),
                    ball.get("Overs"),
                    ball.get("BallNumber"),
                    ball.get("Batter"),
                    ball.get("Bowler"),
                    ball.get("NonStriker"),
                    ball.get("ExtraType"),
                    ball.get("BatsmanRun"),
                    ball.get("ExtrasRun"),
                    ball.get("TotalRun"),
                    ball.get("IsWicketDelivery"),
                    ball.get("PlayerOut"),
                    ball.get("Kind"),
                    ball.get("FieldersInvolved"),
                    ball.get("BattingTeam"),
                    ball.get("BowlingTeam")
                )
                for ball in data["ball_by_ball"]
            ]

            if ball_values_list:
                self.cursor.executemany(insert_query_2, ball_values_list)

            self.conn.commit()
            print(f"Inserted match {data['id']}")

        except pymysql.MySQLError as err:
            print(f"Error inserting data: {err}")

    def get_all_match_ids(self):
        try:
            query = "SELECT id FROM ipl_seasons_data"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except pymysql.MySQLError as err:
            print(f"Error fetching ids: {err}")
            return list()
        
    def fetch_match_data(self, match_id=None):
        try:
            if match_id:
                query = "SELECT * FROM ipl_seasons_data WHERE id = %s"
                self.cursor.execute(query, (match_id,))
            else:
                query = "SELECT * FROM ipl_seasons_data"
                self.cursor.execute(query)

            rows = self.cursor.fetchall()

            columns = [col[0] for col in self.cursor.description]

            df = pd.DataFrame(rows, columns=columns)

            return df

        except pymysql.MySQLError as err:
            print(f"Error fetching data: {err}")
            return None
        
    def fetch_ball_by_ball_data(self, match_id=None):
        try:
            if match_id:
                query = "SELECT * FROM ipl_ball_by_ball_data WHERE id = %s"
                self.cursor.execute(query, (match_id,))
            else:
                query = "SELECT * FROM ipl_ball_by_ball_data"
                self.cursor.execute(query)

            rows = self.cursor.fetchall()

            columns = [col[0] for col in self.cursor.description]

            df = pd.DataFrame(rows, columns=columns)

            return df

        except pymysql.MySQLError as err:
            print(f"Error fetching data: {err}")
            return None
