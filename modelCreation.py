import os
import joblib
import pymysql
import warnings
import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor
)
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings("ignore")

MODEL_PATH = "ipl_predictor_models.joblib"


class IPLPredictor:

    SCORE_FEATURES = [
        "overs", "balls_remaining", "cum_runs",
        "run_rate", "wickets_remaining",
        "run_per_wicket",        # NEW: avg partnership size
        "batting_team_enc", "bowling_team_enc",
        "city_enc", "toss_dec_enc", "year"
    ]

    def __init__(self):
        self.conn = pymysql.connect(
            host="gondola.proxy.rlwy.net",
            port=41287,
            user="root",
            password="ShiZuWeCIrkAWgkDpUwcVnDQHAjXmjyX",
            database="railway"
        )
        self.le_team = LabelEncoder()
        self.le_city = LabelEncoder()
        self.le_toss = LabelEncoder()
        self.best_score_model  = None
        self.best_wicket_model = None
        self.score_results = dict()

    def save(self, path=MODEL_PATH):
        payload = {
            "le_team"           : self.le_team,
            "le_city"           : self.le_city,
            "le_toss"           : self.le_toss,
            "best_score_model"  : self.best_score_model,
            "best_wicket_model" : self.best_wicket_model,
            "score_results"     : self.score_results
        }
        joblib.dump(payload, path)
        print(f"✅ Models saved → {path}")

    def load(self, path=MODEL_PATH):
        if not os.path.exists(path):
            return False
        payload = joblib.load(path)
        self.le_team           = payload["le_team"]
        self.le_city           = payload["le_city"]
        self.le_toss           = payload["le_toss"]
        self.best_score_model  = payload["best_score_model"]
        self.best_wicket_model = payload["best_wicket_model"]
        self.score_results     = payload["score_results"]
        print(f"✅ Models loaded from {path}")
        return True

    def _fetch(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows    = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)

    def load_data(self):
        ipl    = self._fetch("SELECT * FROM ipl_seasons_data")
        record = self._fetch("SELECT * FROM ipl_ball_by_ball_data")
        record.rename(columns={"match_id": "id"}, inplace=True)
        return ipl, record

    def build_features(self, ipl, record):
        data = record[record["innings"] == 1].copy()
        data = data.sort_values(["id", "overs", "ball_number"])

        data["cum_runs"]    = data.groupby("id")["total_run"].cumsum()
        data["cum_wickets"] = data.groupby("id")["is_wicket_delivery"].cumsum()

        final_score = data.groupby("id")["total_run"].sum().rename("final_score")
        df = data.merge(final_score, on="id")

        df["balls_bowled_in_match"] = df.groupby("id").cumcount() + 1
        df["balls_remaining"]       = 120 - df["balls_bowled_in_match"]
        df["run_rate"]              = df["cum_runs"] / (df["balls_bowled_in_match"] / 6).clip(lower=0.1)
        df["wickets_remaining"]     = 10 - df["cum_wickets"]

        # Average runs per wicket lost (partnership quality)
        df["run_per_wicket"]  = df["cum_runs"] / (df["cum_wickets"] + 1)

        match_data = ipl[["id", "city", "toss_decision", "toss_winner", "season"]]
        df = df.merge(match_data, on="id", how="left")

        df["batting_team_enc"] = self.le_team.fit_transform(df["batting_team"].fillna("Unknown"))
        df["bowling_team_enc"] = self.le_team.transform(
            df["bowling_team"].fillna("Unknown").map(
                lambda x: x if x in self.le_team.classes_ else self.le_team.classes_[0]
            )
        )
        df["city_enc"]     = self.le_city.fit_transform(df["city"].fillna("Unknown"))
        df["toss_dec_enc"] = self.le_toss.fit_transform(df["toss_decision"].fillna("bat"))
        df["year"] = df["season"].replace({"2007/08": "2008", "2009/10": "2010", "2020/21": "2020"}).astype(int)

        return df

    def train_score_model(self, df):
        score_df = df.dropna(subset=self.SCORE_FEATURES + ["final_score"])

        X = score_df[self.SCORE_FEATURES]
        y = score_df["final_score"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

        models = {
            "RandomForest"     : RandomForestRegressor(n_estimators=200, max_depth=8,  n_jobs=-1, random_state=42),
            "GradientBoosting" : GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42),
        }

        for name, model in models.items():
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            self.score_results[name] = {
                "model": model,
                "mae"  : mean_absolute_error(y_te, preds),
                "r2"   : r2_score(y_te, preds),
            }

        best = min(self.score_results, key=lambda k: self.score_results[k]["mae"])
        self.best_score_model = self.score_results[best]["model"]
        return best

    def fit(self, force_retrain=False, save_path=MODEL_PATH):
        if not force_retrain and self.load(save_path):
            return

        print("🏋️  Training models (this runs only once)…")
        ipl, record = self.load_data()
        df          = self.build_features(ipl, record)
        best_score  = self.train_score_model(df)

        print(f"Score  model → {best_score:<20} MAE={self.score_results[best_score]['mae']:.1f}  R²={self.score_results[best_score]['r2']:.3f}")

        self.save(save_path)

    def _safe_encode(self, le, val):
        return le.transform([val])[0] if val in le.classes_ else 0

    def predict_score(self, over, cum_runs, cum_wickets,
                      batting_team="Mumbai Indians", bowling_team="Chennai Super Kings",
                      city="Mumbai", toss_dec="bat", year=2024):

        if cum_wickets >= 10 or over >= 20:
            return cum_runs

        balls_bowled = over * 6
        row = pd.DataFrame([{
            "overs"            : over,
            "balls_remaining"  : 120 - balls_bowled,
            "cum_runs"         : cum_runs,
            "run_rate"         : cum_runs / max(balls_bowled / 6, 0.1),
            "wickets_remaining": 10 - cum_wickets,
            "run_per_wicket"   : cum_runs / (cum_wickets + 1),
            "batting_team_enc" : self._safe_encode(self.le_team, batting_team),
            "bowling_team_enc" : self._safe_encode(self.le_team, bowling_team),
            "city_enc"         : self._safe_encode(self.le_city, city),
            "toss_dec_enc"     : self._safe_encode(self.le_toss, toss_dec),
            "year"             : year,
        }])

        predicted = self.best_score_model.predict(row)[0]
        return max(predicted, cum_runs)


if __name__ == "__main__":
    predictor = IPLPredictor()
    predictor.fit(force_retrain=True)

    s1 = predictor.predict_score(10, 80, 2, "Mumbai Indians", "Chennai Super Kings")
    s2 = predictor.predict_score(10, 80, 5, "Mumbai Indians", "Chennai Super Kings")
    s3 = predictor.predict_score(10, 80, 7, "Mumbai Indians", "Chennai Super Kings")

    print(f"\nOver 10 | 80 runs:")
    print(f"  2 wickets → {s1:.0f}")
    print(f"  5 wickets → {s2:.0f}")
    print(f"  7 wickets → {s3:.0f}")