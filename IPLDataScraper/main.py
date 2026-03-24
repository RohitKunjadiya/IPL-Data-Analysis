import re
import json
import zipfile
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from IPLDataScraper.database import Database


class IPLScraper:

    BASE_URL = "https://www.espncricinfo.com"
    START_URL = f"{BASE_URL}/series/indian-premier-league-2007-08-313494/match-schedule-fixtures-and-results"

    HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.all_data = list()
        self.db = Database()
        self.scraped_ids = set(self.db.get_all_match_ids())
        if self.scraped_ids:
            print(f"Already scraped {len(self.scraped_ids)} matches in DB. These will be skipped.")


    def get_seasons(self):
        res = requests.get(self.START_URL, headers=self.HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        json_data = json.loads(soup.find("script", id="__NEXT_DATA__").text)
        seasons = json_data["props"]["appPageProps"]["data"]["content"]["recentSimilarSerieses"]

        season_list = [{"year": "2007-08", "season_id": "313494"}]
        for s in seasons:
            season_list.append({"year": s["year"], "season_id": s["objectId"]})

        return sorted(season_list, key=lambda s: int(str(s["year"]).split("-")[0]))

    def _load_ball_by_ball(self, match_id):
        zip_path = Path("IPLDataScraper\\ipl_json.zip")
        if not zip_path.exists():
            return list()

        json_filename = f"{match_id}.json"

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                matching = [n for n in z.namelist() if Path(n).name == json_filename]
                if not matching:
                    print(f"No ball-by-ball JSON found for match {match_id}")
                    return list()

                with z.open(matching[0]) as f:
                    match_data = json.load(f)

        except Exception as e:
            print(f"  Error reading zip for match {match_id}: {e}")
            return list()

        rows = list()
        for innings_idx, inning in enumerate(match_data.get("innings", []), start=1):
            batting_team = inning["team"]
            teams = match_data["info"]["teams"]
            bowling_team = next((t for t in teams if t != batting_team), "")

            for over in inning.get("overs", []):
                over_num = over["over"]
                ball_number = 0
                for delivery in over.get("deliveries", []):
                    ball_number += 1
                    extras = delivery.get("extras", {})
                    extra_type = ", ".join(extras.keys()) if extras else ""
                    extras_run = delivery["runs"].get("extras", 0)
                    wickets = delivery.get("wickets", [])
                    is_wicket = 1 if wickets else 0
                    player_out = ", ".join(w.get("player_out", "") for w in wickets)
                    kind = ", ".join(w.get("kind", "") for w in wickets)
                    fielders = ", ".join(
                        f["name"] for w in wickets
                        for f in w.get("fielders", []) if "name" in f
                    )
                    rows.append({
                        "Innings": innings_idx,
                        "Overs": over_num,
                        "BallNumber": ball_number,
                        "Batter": delivery.get("batter", ""),
                        "Bowler": delivery.get("bowler", ""),
                        "NonStriker": delivery.get("non_striker", ""),
                        "ExtraType": extra_type,
                        "BatsmanRun": delivery["runs"].get("batter", 0),
                        "ExtrasRun": extras_run,
                        "TotalRun": delivery["runs"].get("total", 0),
                        "IsWicketDelivery": is_wicket,
                        "PlayerOut": player_out,
                        "Kind": kind,
                        "FieldersInvolved": fielders,
                        "BattingTeam": batting_team,
                        "BowlingTeam": bowling_team,
                    })

        return rows

    def scrape_match(self, match_url):
        try:
            res = requests.get(match_url, headers=self.HEADERS)
            sp = BeautifulSoup(res.text, "html.parser")
            json_data = json.loads(sp.find("script", id="__NEXT_DATA__").text)
            match_info = json_data["props"]["appPageProps"]["data"]["match"]

            dd = dict()
            dd["url"] = match_url
            dd["id"] = json_data["query"]["matchId"]
            dd["city"] = match_info["ground"]["smallName"]
            dd["date"] = match_info["startDate"].split("T")[0]
            dd["season"] = match_info["season"]
            dd["match_number"] = match_info["title"]
            dd["team1"] = match_info["teams"][0]["team"]["longName"]
            dd["team2"] = match_info["teams"][1]["team"]["longName"]

            team1_id = match_info["teams"][0]["team"]["id"]
            team2_id = match_info["teams"][1]["team"]["id"]

            team_map = {
                team1_id: dd["team1"],
                team2_id: dd["team2"]
            }

            dd["toss_winner"] = team_map.get(match_info.get("tossWinnerTeamId"), None)

            toss_choice = match_info.get("tossWinnerChoice")
            if toss_choice == 1:
                dd["toss_decision"] = "bat"
            elif toss_choice == 2:
                dd["toss_decision"] = "field"
            else:
                dd["toss_decision"] = None

            dd["winning_team"] = team_map.get(match_info.get("winnerTeamId"), "NR")

            status_text = match_info["statusText"]
            m = re.search(r"won by (\d+) (runs|wickets)", status_text)
            dd["margin"] = int(m.group(1)) if m else None
            dd["won_by"] = m.group(2) if m else None

            awards = json_data["props"]["appPageProps"]["data"]["content"]["matchPlayerAwards"]
            dd["player_of_match"] = awards[0]["player"]["longName"] if awards else ""

            team_players_info = json_data['props']['appPageProps']['data']['content']['matchPlayers']['teamPlayers']
            dd['team1players'] = json.dumps({i+1: j['player']['name'] for i, j in enumerate(team_players_info[0]['players'])})
            dd['team2players'] = json.dumps({i+1: j['player']['name'] for i, j in enumerate(team_players_info[1]['players'])})

            dd["ball_by_ball"] = self._load_ball_by_ball(int(dd["id"]))

            return dd

        except Exception as e:
            print(f"Error scraping {match_url}: {e}")
            return None

    def extract_match_id_from_url(self, url):
        parts = url.rstrip('/').split('/')
        for part in reversed(parts):
            match = re.search(r'-(\d+)$', part)
            if match:
                return int(match.group(1))
        return None

    def scrape_season(self, year, season_id):
        if year == "2007-08":
            url = f"{self.BASE_URL}/series/indian-premier-league-2007-08-{season_id}/match-schedule-fixtures-and-results"
        else:
            url = f"{self.BASE_URL}/series/indian-premier-league-{year}-{season_id}/match-schedule-fixtures-and-results"

        print(f"\nScraping season {year} ({season_id}) ...")

        res = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        matches = soup.select('div[class="ds-flex"]')

        match_urls = list()
        for match in matches:
            anchor = match.find("a", class_="ds-no-tap-higlight")
            if anchor and "href" in anchor.attrs:
                match_urls.append(urljoin(self.BASE_URL, anchor["href"]))

        new_match_urls, skipped = list(), 0
        for match_url in match_urls:
            mid = self.extract_match_id_from_url(match_url)
            if mid and mid in self.scraped_ids:
                skipped += 1
            else:
                new_match_urls.append(match_url)

        print(f"Total matches: {len(match_urls)} | Skipping {skipped} already in DB | Scraping {len(new_match_urls)} new")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_match, url): url for url in new_match_urls}
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    self.all_data.append(result)
                    self.db.insert_match(result)
                    self.scraped_ids.add(int(result["id"]))


    def run(self):
        seasons = self.get_seasons()
        print(f"{len(seasons)} IPL seasons found")

        for s in seasons:
            self.scrape_season(s["year"], s["season_id"])

        print(f"\nScraping completed. {len(self.all_data)} new matches inserted.")


if __name__ == "__main__":
    scraper = IPLScraper(max_workers=5)
    scraper.run()
































# import re
# import json
# import threading
# import requests
# from concurrent.futures import ThreadPoolExecutor, as_completed

# from database import Database

# db = Database()


# class IPLAPIScraper:

#     COMPETITION_URL = "https://scores.iplt20.com/ipl/mc/competition.js"

#     HEADERS = {
#         'Accept': '*/*',
#         'User-Agent': 'Mozilla/5.0'
#     }

#     def __init__(self, max_workers=10):

#         self.max_workers = max_workers
#         self.db_lock = threading.Lock()

#         self.existing_ids = set(db.get_all_match_ids())
#         print(f"{len(self.existing_ids)} matches already in database")

#     def get_competition_ids(self):

#         res = requests.get(self.COMPETITION_URL, headers=self.HEADERS)

#         text = res.text

#         json_text = re.search(r'\((.*)\)', text, re.S).group(1)

#         data = json.loads(json_text)

#         competitions = data['competition']

#         ids = [c['CompetitionID'] for c in competitions]

#         return ids

#     def parse_margin(self, comment):

#         margin = None
#         won_by = None

#         run_match = re.search(r'by (\d+)\s*Runs', comment, re.I)
#         wicket_match = re.search(r'by (\d+)\s*Wickets', comment, re.I)

#         if run_match:
#             margin = int(run_match.group(1))
#             won_by = "runs"

#         elif wicket_match:
#             margin = int(wicket_match.group(1))
#             won_by = "wickets"

#         return margin, won_by

#     def parse_toss(self, toss_text):

#         if not toss_text:
#             return None

#         toss_text = toss_text.lower()

#         if "bat" in toss_text:
#             return "bat"

#         if "field" in toss_text or "bowl" in toss_text:
#             return "field"

#         return None

#     def scrape_match(self, m):

#         try:

#             match_id = int(m.get("MatchID"))

#             with self.db_lock:
#                 if match_id in self.existing_ids:
#                     print(f"Match {match_id} already exists")
#                     return

#             comment = m.get("Comments", "")

#             margin, won_by = self.parse_margin(comment)

#             toss_decision = self.parse_toss(m.get("TossDetails"))

#             winning_team = (
#                 m.get("HomeTeamName")
#                 if str(m.get("WinningTeamID")) == str(m.get("HomeTeamID"))
#                 else m.get("AwayTeamName")
#             )

#             row = {
#                 "url": f"https://www.iplt20.com/match/{match_id}",
#                 "id": match_id,
#                 "city": m.get("city"),
#                 "date": m.get("MatchDate"),
#                 "season": m.get("CompetitionID"),
#                 "match_number": m.get("MatchOrder"),
#                 "team1": m.get("FirstBattingTeamName"),
#                 "team2": m.get("SecondBattingTeamName"),
#                 "toss_winner": m.get("TossTeam"),
#                 "toss_decision": toss_decision,
#                 "winning_team": winning_team,
#                 "margin": margin,
#                 "won_by": won_by,
#                 "player_of_match": m.get("MOM"),
#             }

#             print(f"Scraped match {match_id}")

#             with self.db_lock:
#                 db.insert_match(row)
#                 self.existing_ids.add(match_id)

#         except Exception as e:
#             print(f"Error scraping match {m.get('MatchID')} : {e}")

#     def scrape_season(self, competition_id):

#         print(f"\nScraping season {competition_id}")

#         url = f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/{competition_id}-matchschedule.js"

#         headers = {
#             'Accept': '*/*',
#             'Referer': 'https://www.iplt20.com/',
#             'User-Agent': 'Mozilla/5.0'
#         }

#         res = requests.get(url, headers=headers)

#         text = res.text

#         json_text = re.search(r'\((.*)\)', text).group(1)

#         data = json.loads(json_text)

#         matches = data["Matchsummary"]

#         with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

#             futures = [
#                 executor.submit(self.scrape_match, m)
#                 for m in matches
#             ]

#             for _ in as_completed(futures):
#                 pass

#     def run(self):

#         ids = self.get_competition_ids()

#         print(f"{len(ids)} seasons found")

#         for cid in ids:
#             self.scrape_season(cid)

#         print("\nScraping completed")


# if __name__ == "__main__":

#     scraper = IPLAPIScraper(max_workers=10)

#     scraper.run()