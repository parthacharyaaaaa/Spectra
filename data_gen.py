from typing import Literal
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_random_date(start_date: str, end_date: str, date_format: str = "%d/%m/%y") -> str:
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)

    random_days = random.randint(0, (end - start).days)
    random_date = start + timedelta(days=random_days)
    return random_date.strftime(date_format)

def generate_random_nigga() -> str:
    global fnames, lnames;
    return random.choice(fnames) + " " + random.choice(lnames)

fnames = []
lnames = []
companies = []
company_suffixes = ["LLC", "Group", "Inc", "Ltd.", ""]
indices = ["Date", "Payment Type", "Transaction Name", "Category", "Amount (INR)"]

with open("companies.txt", "r") as file:
    companies = file.read().split(",")

with open("fnames.txt", "r") as file:
    fnames = file.read().split(",")

with open("lnames.txt", "r") as file:
    lnames = file.read().split(",")


class DataMaker:
    PAYMENT_TYPES = ["Credit", "Debit", "UPI"]

    GENERATION_METADATA = {
            "Digital Insurance": [(1000, 1_000_000), PAYMENT_TYPES[1:]],
            "Mutual Funds": [(500, 100_000), PAYMENT_TYPES],
            "Digital Gold": [(1000, 10_000_000), PAYMENT_TYPES],
            "ETFs": [(1000, 1_000_000), PAYMENT_TYPES],
            "REITs": [(10_000, 2_000_000), PAYMENT_TYPES],
            "P2P": [(100, 50_000), PAYMENT_TYPES[:2]],
            "Lifestyle": [(500, 50_000), PAYMENT_TYPES],
            "Medical Bills": [(100, 500_000), PAYMENT_TYPES],
            "Bonds": [(5_000, 1_000_000), PAYMENT_TYPES[:3]]
        }
    
    SE_CLASS_BEHAVIOR = {
        "Digital Insurance": ((0.1, 0.5, 0.5), (0.0001, 0.2, 1)),
        "Mutual Funds": ((0.3, 0.5, 0.2), (0.01, 0.4, 1)),
        "Digital Gold": ((0.2, 0.5, 0.3), (0.005, 0.5, 1)),
        "ETFs": ((0.1, 0.4, 0.5), (0.005, 0.3, 1)),
        "REITs": ((0.05, 0.2, 0.75), (0.01, 0.2, 1)),
        "P2P": ((0.4, 0.5, 0.1), (0.02, 0.3, 1)),
        "Lifestyle": ((0.3, 0.5, 0.2), (0.1, 0.6, 1)),
        "Medical Bills": ((0.4, 0.4, 0.2), (0.05, 0.7, 1)),
        "Bonds": ((0.2, 0.5, 0.3), (0.01, 0.5, 1))
    }


    categories : tuple[str] = GENERATION_METADATA.keys()
    PROFILES = {1 : "poor",
              2 : "middle-class",
              3 : "rich"}

    def __init__(self, profile : Literal[1, 2, 3]):
        self.profile = profile

    def generateEntries(self, limit : int = 30) -> list[pd.Series]:
        currentCount : int = 0
        entries : list[pd.Series] = []
        while(currentCount < limit):
            for category, behavior in DataMaker.SE_CLASS_BEHAVIOR.items():
                if random.randint(0, 101) <= behavior[0][self.profile - 1]:
                    data = (generate_random_date("01/01/24", "31/12/24"),
                            random.choice(DataMaker.GENERATION_METADATA[category][-1]),
                            f"{category} - {random.choice(companies)} {random.choice(company_suffixes)}" if category.upper() != "P2P" else f"{category} - {generate_random_nigga()}",
                            category,
                            random.randint(DataMaker.GENERATION_METADATA[category][0][0], DataMaker.GENERATION_METADATA[category][0][1] * behavior[1][self.profile - 1])
                            )
                    entries.append(pd.Series(data, index=indices))
                    currentCount+=1;
        entries.sort(key = lambda x : x[0])
        csv_data : pd.DataFrame = pd.DataFrame(entries)
        csv_data.to_csv("output.csv", index = False)


gen : DataMaker = DataMaker(int(input("Enter profile: 1) Poor, 2) Middle-Class, 3) Rich: ")))
if gen.profile == 3:
    print("I hate rich niggas, goddamnit\nCause I ain't never had a lot, damnit")

gen.generateEntries()