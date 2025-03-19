import math

# ==========================
# Hardcoded Parameters
# ==========================

# Cost parameters
FUEL_COST = 3                 # Dollars per mile
MAINTENANCE_FACTOR = 0.10     # 10%

# Travel time parameters
DRIVING_EXPERIENCE_FACTOR = 0.1  # Intermediate level
SNOWFALL_TIME_FACTOR = 0.5   # Random weight added per inch of snowfall

# Normalization range [1, 5]
NORM_MIN = 1
NORM_MAX = 5

# User input parameters
num_people = 4
user_max_budget = 60         # Per person budget (dollars) # increased budget to 2000
user_max_time = 5            # Maximum allowed trip time (hours)
min_required_snow = 1       # Minimum required fresh powder (inches) # changed to 0

# User-defined weights for the objective function
w1 = 5   # Weight for snowfall conditions
w2 = -8   # Weight for budget importance, made it negative
w3 = -2   # Weight for travel time importance, made it negative

# ==========================
# Hardcoded Data for 10 Resorts
# ==========================

# Attributes for each resort: miles (both-ways), accidents, snowfall_start, snowfall_end, current_time (seconds)
colorado_ski_resorts = [
    "Arapahoe Basin",
    "Aspen Highlands",
    "Aspen Mountain",
    "Beaver Creek",
    "Breckenridge",
    "Buttermilk",
    "Copper Mountain",
    "Crested Butte",
    "Echo Mountain",
    "Eldora Mountain"
]

miles =          [60, 21, 40, 67, 56, 105, 72, 93, 185, 320]
accidents =      [3,  1,  2,  0,  5,   1,  0,  2,  0,  15]
snowfall_start = [1, 2, 2, 6, 4, 3, 2, 5, 1, 2]
snowfall_end =   [12, 7, 14, 8, 6, 18, 9, 11, 4, 15]
current_time =   [3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 6480]  # In seconds

# snowfall_dest = [15, 9, 20, 11, 10, 25, 13, 14, 8, 18]  # Fresh powder at destination - Get from API giving snowfall in last 1 hour (commented for now)

num_resorts = len(miles)

# ==========================
# Helper Functions
# ==========================

def calculate_base_fee(miles):
    """Calculate base fee based on round-trip miles (scales between $5-$30)."""
    round_trip_miles = miles
    if round_trip_miles >= 200:
        return 30
    else:
        return 5 + (15 * round_trip_miles / 200)

def round_up_to_nearest_10(x):
    """Round up a number to the nearest 10."""
    return math.ceil(x / 10.0) * 10

def normalize(values):
    """Normalize a list of values to the range [NORM_MIN, NORM_MAX]."""
    min_val = min(values)
    max_val = max(values)
    return [
        NORM_MIN + (NORM_MAX - NORM_MIN) * ((v - min_val) / (max_val - min_val))
        if max_val != min_val else NORM_MIN for v in values
    ]

# ==========================
# Calculated Values for Each Resort
# ==========================

# 1. Calculate cost per person
cost_per_person = []
for i in range(num_resorts):
    base_fee = calculate_base_fee(miles[i])
    total_cost = miles[i] * FUEL_COST * (1 + MAINTENANCE_FACTOR)
    per_person_cost = base_fee + (total_cost / num_people)
    cost_per_person.append(round_up_to_nearest_10(per_person_cost))

# 2. Calculate travel time
travel_time = []
for i in range(num_resorts):
    time_hours = current_time[i] / 3600  # Convert seconds to hours
    total_time = 2* (time_hours + DRIVING_EXPERIENCE_FACTOR*(accidents[i] + SNOWFALL_TIME_FACTOR*(snowfall_start[i] + snowfall_end[i])))
    travel_time.append(total_time)

# 3. Normalize cost and time
normalized_snowfall = normalize(snowfall_end)
normalized_cost = normalize(cost_per_person)
normalized_time = normalize(travel_time)

# ==========================
# Formulation
# ==========================

all_resort_scores = []
selected_resorts = []
# Define the optimization problem
for i in range(num_resorts):
    Objective =  w1 * normalized_snowfall[i] + w2 * normalized_cost[i] + w3 * normalized_time[i] 
    all_resort_scores.append(Objective)

    if cost_per_person[i] > user_max_budget or travel_time[i] > user_max_time:
        # Resort does not meet the criteria, skip it
        print(f"Resort {i} removed: Budget or time exceeded.")
    else:
        # Resort meets the criteria, keep it
        selected_resorts.append((i, Objective))

# Rank resorts by objective score and keep only the top 3
selected_resorts.sort(key=lambda x: x[1], reverse=True)
top_3_resorts = selected_resorts[:3]


# ==========================
# Output Results
# ==========================


# Debug prints
print("=== Debugging Values ===")

for i in range(num_resorts):
    print(f"Resort #{i}:")
    print(f"  Score: {all_resort_scores[i]:.2f}")
    print(f"  Cost per Person: ${cost_per_person[i]}")
    print(f"  Travel Time: {travel_time[i]} hrs")
    print(f"  Fresh Snowfall at Resort: {snowfall_end[i]} inches")
    print(f"  Normalized Cost: {normalized_cost[i]}")
    print(f"  Normalized Time: {normalized_time[i]}")
    print()

# Final Output
if top_3_resorts:
    print("\n=== Optimal Ski Resorts ===")
    for rank, (resort_idx, score) in enumerate(top_3_resorts, start=1):
        print(f"\nRank #{rank}:")
        print(f"  {colorado_ski_resorts[resort_idx]}")
        print(f"  Score: {score:.2f}")
        print(f"  Cost per Person: ${cost_per_person[resort_idx]}")
        print(f"  Travel Time: {travel_time[resort_idx]} hrs")
        print(f"  Fresh Snowfall at Resort: {snowfall_end[resort_idx]} inches")
        print(f"  Normalized Cost: {normalized_cost[resort_idx]}")
        print(f"  Normalized Time: {normalized_time[resort_idx]}")
else:
    print("No resorts fit your criteria. Lower your expectations XD.")
