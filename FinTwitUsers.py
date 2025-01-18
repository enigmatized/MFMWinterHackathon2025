from collections import defaultdict
import pandas as pd
import os
from datetime import datetime


class FinTwitUser:
    def __init__(self, name, user_id):
        """
        Initialize a FinTwitUser object with a name and a user ID.
        
        :param name: The name of the user
        :param user_id: The integer ID of the user
        """

        self.name = name
        self.user_id = user_id
        self.lastRetreivalTime = None
        self.newTweetIds = []
        self.oldTweetIds = []
        self.retreivedTweets = defaultdict(str)
        

    def __repr__(self):
        """
        Return a string representation of the FinTwitUser object.
        """
        return f"FinTwitUser(name='{self.name}', user_id={self.user_id})"

def update_csv_with_retweets(csv_filepath, fin_twit_users):
    """
    Reads a CSV file into a DataFrame. Each row has columns: 
        name, twitterId, tweet
    Then iterates over a list of FinTwitUser objects:
      - for each (tweet_id, tweet_text) in user.retreivedTweets,
        checks if that row already exists in the DataFrame 
        (matching user.name, user.user_id, tweet_text)
      - if it does not exist, it appends a new row
    
    Finally, writes the updated DataFrame back to the CSV file.

    :param csv_filepath: The path to the CSV file (str)
    :param fin_twit_users: A list of FinTwitUser instances
    """

    if not os.path.isfile(csv_filepath):
        df = pd.DataFrame(columns=['name', 'twitterId', 'tweetId', 'tweet'])
    else:
        # File exists, so read from CSV into a DataFrame (all columns as string).
        df = pd.read_csv(csv_filepath, dtype=str)

    # # 1. Read from CSV into a DataFrame. 
    # #    Ensure columns are read as strings so comparisons are straightforward.
    # df = pd.read_csv(csv_filepath, dtype=str)

    # 2. For each user, check whether each tweet is already in the DataFrame.
    rows_to_add = []
    for user in fin_twit_users:
        for tweet_id, tweet_text in user.retreivedTweets.items():
            # Prepare strings for comparison
            name_str = str(user.name)
            user_id_str = str(user.user_id)
            tweet_id_str = str(tweet_id)
            tweet_str = str(tweet_text)

            # Check if this combination already exists
            # (df['name'] == name) & (df['twitterId'] == user_id) & (df['tweet'] == tweet_text)
            mask = (
                (df['name'] == name_str) & 
                (df['twitterId'] == user_id_str) & 
                (df['tweetId'] == tweet_id_str) & 
                (df['tweet'] == tweet_str)
            )

            if not mask.any():
                # If none match, we need to add a new row
                new_row = {
                    'name':      name_str,
                    'twitterId': user_id_str,
                    'tweetId':   tweet_id_str,
                    'tweet':     tweet_str
                }
                rows_to_add.append(new_row)

    # 3. Append new rows (if any) to the DataFrame.
    if rows_to_add:
        df = pd.concat([df, pd.DataFrame(rows_to_add)], ignore_index=True)

    # 4. Write the DataFrame back to CSV (overwrite existing file).
    df.to_csv(csv_filepath, index=False)

def sort_fin_twit_users(fin_twit_users):
    """
    Returns a new list sorted such that:
      - Users with lastRetreivalTime=None come first.
      - Among non-None times, most recent datetime comes first.
    """
    def sort_key(user):
        if user.lastRetreivalTime is None:
            # Priority 0 => these are at the front
            # Second element of tuple can be anything (e.g., 0) because
            # all None times are tied.
            return (0, 0)  
        else:
            # Priority 1 => these come after None
            # Then sort descending by negative timestamp
            return (1, -user.lastRetreivalTime.timestamp())
    
    return sorted(fin_twit_users, key=sort_key)


def create_fintwit_users_from_csv(csv_filepath):
    """
    Reads a CSV with columns: [name, twitterId, tweet]
    and creates a list of FinTwitUser objects from it.
    
    Because the CSV does not contain a dedicated Tweet ID, 
    we'll use the row index (e.g., 'row_0') as the dictionary key in retreivedTweets.
    
    :param csv_filepath: The path to the CSV file (str)
    :return: A list of FinTwitUser objects
    """
    # 1. Read from CSV into a DataFrame.
    df = pd.read_csv(csv_filepath, dtype=str)
    
    # 2. We'll collect users in a dict keyed by (name, user_id) so we don't create duplicates.
    users_map = {}
    
    for _, row in df.iterrows():
        name = row["name"]
        user_id = row["twitterId"]  # This might be numeric, but we keep it as str for simplicity
        tweetId = row["tweetId"]
        tweet_text = row["tweet"]

        # Check if we already have a FinTwitUser with (name, user_id)
        key = (name, user_id)
        if key not in users_map:
            # Create a new FinTwitUser
            users_map[key] = FinTwitUser(name=name, user_id=user_id)
        
        # Store the tweet in this user's retreivedTweets
        # Using 'row_i' as the artificial tweet ID key.
        users_map[key].retreivedTweets[tweetId] = tweet_text
    
    # 3. Return the list of FinTwitUser objects
    return list(users_map.values())




usernames = [
    "aclenow",
    "AdamMancini4",
    "alifarhat79",
    "allstarcharts",
    "AlphaGammaHQ",
    "amlivemon",
    "AnalystDC",
    "AndreasSteno",
    "AndrewThrasher",
    "AswathDamodaran",
    "austinhankwitz",
    "awealthofcs",
    "BarChart",
    "barronsonline",
    "Benzinga",
    "BillAckman",
    "Biohazard3737",
    "breadcrumbsre",
    "BrianFeroldi",
    "BuccoCapital",
    "BullishRippers",
    "business",
    "business",
    "BusinessInsider",
    "Carl_C_Icahn",
    "CasinoCapital",
    "Chariot_Invest",
    "charliebilello",
    "CNBC",
    "Cokedupoptions",
    "ComposerTrade",
    "ContrarianShort",
    "CramerTracke",
    "CullenFrost",
    "cullenroche",
    "dailydirtnap",
    "daniel_toloko",
    "darjohn25",
    "DataDInvesting",
    "DavidKass3",
    "DeItaone",
    "dirtcheapstocks",
    "DividendGrowth",
    "Dividendology",
    "DKellerCMT",
    "DonutShorts",
    "DoombergT",
    "dougboneparth",
    "DV_Situations",
    "EconguyRosie",
    "EconomPic",
    "EddyElfenbein",
    "EdgeCGroup",
    "EpsilonTheory",
    "EricBalchunas",
    "FinancialPost",
    "FinancialReview",
    "FinancialTimes",
    "Forbes",
    "FortuneMagazine",
    "FT",
    "fundstrat",
    "FXStreetNews",
    "garyblack00",
    "GlobalStockPick",
    "Gold_Mansack",
    "GRDecter",
    "gurgavin",
    "GuruFocus",
    "hkuppy",
    "hmeisler",
    "HolyFinance",
    "howardlindzon",
    "HudsonLabs",
    "iancassel",
    "IBDinvestors",
    "insiliconot",
    "InvestorAmnesia",
    "irbezek",
    "jackschwager",
    "Jake__Wujastyk",
    "jasonzweigwsj",
    "JaySinh130",
    "jedimarkus77",
    "JerryCap",
    "Jesse_Livermore",
    "jessefelder",
    "jmackin2",
    "jposhaughnessy",
    "JTSEO9",
    "JulianKlymochko",
    "JulianMI2",
    "KathyJones",
    "kevinmuir",
    "Kiplinger",
    "KrisAbdelmessih",
    "Ksidiii",
    "kylascan",
    "LastBearStanding",
    "leadlagreport",
    "litcapital",
    "LizAnnSonders",
    "LizYoungStrat",
    "LynAldenContact",
    "LynAldenContact",
    "MacroAlf",
    "macrocephalopod",
    "MacroTactical",
    "mark_dow",
    "MarketBeatCon",
    "MarketWatch",
    "markminervini",
    "MarkYusko",
    "masked_investor",
    "masterly_in",
    "matt_levine",
    "michaelbatnick",
    "MichaelGoodwell",
    "michaeljburry",
    "MichaelKitces",
    "MorganCreek_Dig",
    "morganhousel",
    "MorningStarInc",
    "nasdaq",
    "NateGeraci",
    "orthereaboot",
    "PandaValue",
    "ParikPatelCFA",
    "PelosiTracker_",
    "PeterLBrandt",
    "Post_Market",
    "ppearlman",
    "PriapusIQ",
    "profplum99",
    "PythiaR",
    "quakes99",
    "QuiverQuant",
    "RampCapitalLLC",
    "RaoulGMI",
    "RedDogT3",
    "ReformedBroker",
    "ResGloStocks",
    "ReturnsJourney",
    "Reuters",
    "ritholtz",
    "Ross_Report",
    "ruima",
    "RyanDetrick",
    "SallieKrawcheck",
    "SamanthaLaDuc",
    "SamRo",
    "SardonicCanuck",
    "SeekingAlpha",
    "sentimentrader",
    "sinstockpapi",
    "SmallCapWhales",
    "smartasset",
    "SrivatsPrakash",
    "SteadyCompound",
    "Stephanie_Link",
    "stlouisfed",
    "StockJabber",
    "StockMKTNewz",
    "StocksOnSpaces",
    "stocktalkweekly",
    "StockTwits",
    "SwaggyStocks",
    "TaraBull808",
    "TaviCosta",
    "thebalance",
    "TheEconomist",
    "themotleyfool",
    "TheRoaringKitty",
    "therobotjames",
    "TheSpeculator0",
    "TheStalwart",
    "TheStreet",
    "TheTranscript_",
    "TihoBrkan",
    "TikTokInvestors",
    "tolstoybb",
    "TradesTrey",
    "TruthGundlach",
    "tseides",
    "TSOH_Investing",
    "ukarlewitz",
    "unusual_whales",
    "UptrendsAI",
    "ValueSotp",
    "ValueStockGeek",
    "VCBrags",
    "WallStCynic",
    "WallStreetSilv",
    "WOLF_Financial",
    "wolfejosh",
    "WSJ",
    "YahooFinance",
    "zachxbt",
    "ZacksResearch",
    "ZeroHedge"
]


if __name__ == "__main__":
    # Suppose we have a CSV "tweets.csv" with columns: name, twitterId, tweet
    
    # Create some FinTwitUser objects
    user_a = FinTwitUser(name="Alice", user_id=123)
    user_b = FinTwitUser(name="Bob", user_id=456)

    # Populate retreivedTweets
    user_a.retreivedTweets["101"] = "This is Alice's tweet #1"
    user_a.retreivedTweets["102"] = "This is Alice's tweet #2"
    user_b.retreivedTweets["201"] = "This is Bob's tweet #1"

    # List of users
    fin_twit_users_list = [user_a, user_b]

    # Update CSV
    update_csv_with_retweets("tweets.csv", fin_twit_users_list)

    ls = create_fintwit_users_from_csv("tweets.csv" )
    for x in ls:
        print(x)
        print(x.retreivedTweets)
        print()