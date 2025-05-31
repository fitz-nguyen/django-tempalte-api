import csv
import random
from datetime import datetime, timedelta

# Define the possible values for each field
HIRE_PREDICTIONS = ["Very Likely", "Likely", "Possible", "Unlikely", "Less Likely"]
ROOF_MATERIALS = ["Composition Shingle", "Metal", "Tile", "Unknown"]
ZIP_CODES = ["85001", "85002", "85003", "87001", "87002", "84790", "84791"]  # Phoenix, Albuquerque, St. George

# Define coordinates for each zip code (approximate center points)
ZIP_COORDINATES = {
    "85001": {"lat": (33.4, 33.5), "lon": (-112.1, -112.0)},  # Downtown Phoenix
    "85002": {"lat": (33.4, 33.5), "lon": (-112.1, -112.0)},  # Central Phoenix
    "85003": {"lat": (33.4, 33.5), "lon": (-112.1, -112.0)},  # Central City
    "87001": {"lat": (35.0, 35.1), "lon": (-106.6, -106.5)},  # Downtown Albuquerque
    "87002": {"lat": (35.0, 35.1), "lon": (-106.6, -106.5)},  # Central Albuquerque
    "84790": {"lat": (37.1, 37.2), "lon": (-113.5, -113.4)},  # St. George
    "84791": {"lat": (37.1, 37.2), "lon": (-113.5, -113.4)},  # St. George
}

# Define the headers (excluding Status, Reason, SaleRepresentativeID, and SaleRepresentativeName)
HEADERS = [
    "RMID",
    "FirstName",
    "LastName",
    "Address",
    "Latitude",
    "Longitude",
    "City",
    "State",
    "Zip",
    "LandlinePhoneNumber",
    "CellPhone",
    "BirthDate",
    "MaritalStatus",
    "HirePrediction",
    "HomePurchaseYear",
    "HomeYearBuilt",
    "HomeEstCurrentValue",
    "HouseholdNetWorth",
    "RoofMaterial",
    "LastStormDamage",
    "HomeSize",
]

# Sample data for other fields
CITIES = {
    "85001": ["Downtown Phoenix", "Central Business District", "Government District"],
    "85002": ["Central Phoenix", "Roosevelt", "Garfield"],
    "85003": ["Central City", "Historic District", "Arts District"],
    "87001": ["Downtown Albuquerque", "Old Town", "Historic District"],
    "87002": ["Central Albuquerque", "Nob Hill", "University Area"],
    "84790": ["St. George", "Downtown", "Historic District"],
    "84791": ["St. George", "Sunset", "Dixie Downs"],
}

FIRST_NAMES = ["John", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Elizabeth", "David", "Susan"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Taylor", "Anderson", "Martinez"]
STREET_TYPES = ["Street", "Avenue", "Drive", "Court", "Lane", "Circle", "Way", "Road"]
STREET_NAMES = ["Oak", "Pine", "Maple", "Elm", "Birch", "Cedar", "Spruce", "Walnut", "Hickory", "Poplar"]
MARITAL_STATUSES = ["Married", "Single", "Divorced", "Widowed"]


def generate_random_date(start_year=1960, end_year=1990):
    """Generate a random date between start_year and end_year"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def generate_random_datetime(start_date, days_ahead):
    """Generate a random datetime within the specified range"""
    random_days = random.randint(0, days_ahead)
    random_hours = random.randint(9, 17)
    random_minutes = random.randint(0, 59)
    return (start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_random_coordinates(zip_code):
    """Generate random coordinates based on the zip code"""
    coords = ZIP_COORDINATES[zip_code]
    lat = random.uniform(coords["lat"][0], coords["lat"][1])
    lon = random.uniform(coords["lon"][0], coords["lon"][1])
    return f"{lat:.4f}", f"{lon:.4f}"


def generate_random_phone():
    """Generate a random phone number"""
    return f"919-{random.randint(100,999)}-{random.randint(1000,9999)}"


def generate_random_value():
    """Generate a random home value"""
    return f"${random.randint(350000, 520000):,}"


def generate_random_net_worth():
    """Generate a random household net worth"""
    return f"${random.randint(300000, 1200000):,}"


def generate_random_home_size():
    """Generate a random home size"""
    return random.randint(1800, 2800)


def generate_record(rmid):
    """Generate a single record with the specified RMID"""
    zip_code = random.choice(ZIP_CODES)
    lat, lon = generate_random_coordinates(zip_code)
    city = random.choice(CITIES[zip_code])
    street_number = random.randint(100, 999)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    address = f"{street_number} {street_name} {street_type}"

    # Determine state based on zip code
    if zip_code.startswith("85"):
        state = "AZ"
    elif zip_code.startswith("87"):
        state = "NM"
    else:  # 847
        state = "UT"

    # Generate dates
    birth_date = generate_random_date()
    last_storm_damage = generate_random_date(2023, 2024)

    # Generate other fields
    home_purchase_year = random.randint(2008, 2020)
    home_year_built = random.randint(1990, 2020)

    return [
        rmid,
        random.choice(FIRST_NAMES),
        random.choice(LAST_NAMES),
        address,
        lat,
        lon,
        city,
        state,  # Dynamic state based on zip code
        zip_code,
        generate_random_phone(),
        generate_random_phone(),
        birth_date,
        random.choice(MARITAL_STATUSES),
        random.choice(HIRE_PREDICTIONS),
        str(home_purchase_year),
        str(home_year_built),
        generate_random_value(),
        generate_random_net_worth(),
        random.choice(ROOF_MATERIALS),
        last_storm_damage,
        str(generate_random_home_size()),
    ]


def generate_csv(filename, start_rmid=1220, num_records=1000):
    """Generate the CSV file with the specified number of records"""
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t")
        writer.writerow(HEADERS)

        for i in range(num_records):
            rmid = str(start_rmid + i).zfill(5)
            writer.writerow(generate_record(rmid))


if __name__ == "__main__":
    generate_csv("csv_admin_1000.txt")
    print("CSV file generated successfully!")
