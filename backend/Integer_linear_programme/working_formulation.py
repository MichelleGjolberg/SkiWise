from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpBinary, value
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
user_max_budget = 100         # Per person budget (dollars)
user_max_time = 3            # Maximum allowed trip time (hours)
min_required_snow = 1       # Minimum required fresh powder (inches)

# User-defined weights for the objective function
w1 = 1   # Weight for snowfall conditions
w2 = 8   # Weight for budget importance
w3 = 2   # Weight for travel time importance 

# ==========================
# Hardcoded Data for 10 Resorts
# ==========================

# Attributes for each resort: miles (both-ways), accidents, snowfall_start, snowfall_end, current_time (seconds)
miles =          [60, 21, 40, 67, 56, 105, 72, 93, 185, 320]
accidents =      [30,  1,  2,  0,  5,   1,  0,  2,  0,  15]
snowfall_start = [1, 2, 0, 6, 4, 0, 2, 5, 1, 2]
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
    total_time = time_hours + DRIVING_EXPERIENCE_FACTOR*(accidents[i] + SNOWFALL_TIME_FACTOR*(snowfall_start[i] + snowfall_end[i])    )
    travel_time.append(total_time)

# 3. Normalize snowfall, cost, and time between [1, 100]
# normalized_snowfall = normalize(snowfall_end)
normalized_cost = normalize(cost_per_person)
normalized_time = normalize(travel_time)

# ==========================
# ILP Formulation
# ==========================

# Define the optimization problem
prob = LpProblem("SkiResortSelection", LpMaximize)

# Binary decision variables: 1 if resort is selected, 0 otherwise
x = [LpVariable(f"x{i}", cat=LpBinary) for i in range(num_resorts)]

# Objective Function: Weighted sum of normalized snowfall, cost (negative), and travel time (negative)
prob += lpSum(
    w1 * snowfall_end[i] * x[i] - 
    w2 * normalized_cost[i] * x[i] - 
    w3 * normalized_time[i] * x[i] for i in range(num_resorts)
)

BIG_M = 1000  # Large number to deactivate constraint when x[i] = 0

for i in range(num_resorts):
    # Enforce budget only for selected resorts
    prob += cost_per_person[i] <= user_max_budget + (1 - x[i]) * BIG_M

    # Enforce time constraint only for selected resorts
    prob += travel_time[i] <= user_max_time + (1 - x[i]) * BIG_M

    # Enforce minimum snowfall constraint only for selected resorts
    prob += snowfall_start[i] >= min_required_snow - (1 - x[i]) * BIG_M

# # Constraints
# prob += lpSum(x) == 3  # Select exactly 3 resorts
# for i in range(num_resorts):
#     prob += cost_per_person[i] * x[i] <= user_max_budget  # Budget constraint
#     prob += travel_time[i] * x[i] <= user_max_time        # Time constraint
#     prob += snowfall_start[i] * x[i] >= min_required_snow # Minimum snowfall constraint

# ==========================
# Solve the ILP
# ==========================
prob.solve()

# ==========================
# Output Results
# ==========================

selected_resorts = [i for i in range(num_resorts) if value(x[i]) == 1]

# Debug prints
print("=== Debugging Values ===")

resort_scores = []

for i in range(num_resorts):
    score = (
        w1 * snowfall_end[i] - 
        w2 * normalized_cost[i] - 
        w3 * normalized_time[i])
        
    resort_scores.append(score)

for i in range(num_resorts):
    # score = (
    # w1 * normalized_snowfall[i] - 
    # w2 * normalized_cost[i] - 
    # w3 * normalized_time[i])
    
    # resort_scores.append(score)

    
    print(f"Resort #{i}:")
    print(f"  Score: {resort_scores[i]:.2f}")
    # print(f"  Base Fee: ${calculate_base_fee(miles[i])}")
    print(f"  Cost per Person: ${cost_per_person[i]}")
    print(f"  Travel Time: {travel_time[i]} hrs")
    print(f"  Fresh Snowfall at Resort: {snowfall_end[i]} inches")
    print(f"  Normalized Cost: {normalized_cost[i]}")
    print(f"  Normalized Time: {normalized_time[i]}")
    print()

# Final Output
print("\n=== Optimal Ski Resorts ===")
for i in selected_resorts:
    print(f"Resort {i} - Optimization Score: {resort_scores[i]:.2f}, Miles: {miles[i]}, Cost per Person: ${cost_per_person[i]}, Time: {round(travel_time[i], 2)} hrs")
