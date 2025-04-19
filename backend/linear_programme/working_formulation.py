import math
import matplotlib.pyplot as plt

# ==========================
# User Inputs & from API ----------------------> Get from backend
# ==========================

num_people = 4
max_budget = 100
max_time = 5
min_snowfall = 1
w1, w2, w3 = 5, -5, -5
DRIVING_EXPERIENCE_FACTOR = 0.1  # Intermediate level

# ==========================
# Hardcoded Parameters
# ==========================

FUEL_COST = 3                 # Dollars per gallon
MAINTENANCE_FACTOR = 0.10     # 10%
SNOWFALL_TIME_FACTOR = 0.5   # Random weight added per inch of snowfall
NORM_MIN = 1 # Normalization range
NORM_MAX = 5

# ==========================
# Hardcoded Data for 10 Resorts -----------------> Get from backend
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

miles =          [30, 21, 40, 57, 46, 105, 72, 83, 85, 220]
accidents =      [0,  0,  0,  0,  0,   1,  0,  2,  0,  1]
snowfall_start = [1, 2, 2, 6, 4, 3, 2, 5, 1, 2]
snowfall_end =   [12, 7, 14, 8, 6, 18, 9, 11, 4, 10]
current_time =   [3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480]  # In seconds
# snowfall_dest = [15, 9, 20, 11, 10, 25, 13, 14, 8, 18]  # Fresh powder at destination - Get from API giving snowfall in last 1 hour (commented for now)

# ==========================
# Helper Functions
# ==========================

def calculate_base_fee(miles):
    """Calculate base fee based on round-trip miles (scales between $5-$30)."""
    round_trip_miles = 2*miles
    if round_trip_miles >= 200:
        return 30
    else:
        return 5 + (round_trip_miles / 100)

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

def calculate_cost_per_person(num_people):
    """Calculate cost per person for each resort."""
    cost_per_person = []
    
    for i in range(len(miles)):
        base_fee = calculate_base_fee(miles[i])
        one_way_cost = miles[i] * FUEL_COST * (1 + MAINTENANCE_FACTOR)
        per_person_cost = base_fee + 2* (one_way_cost / num_people)
        cost_per_person.append(round_up_to_nearest_10(per_person_cost))
    
    return cost_per_person

def calculate_travel_time():
    """Calculate travel time for each resort for to and fro."""
    travel_time = []
    
    for i in range(len(miles)):
        time_hours = current_time[i] / 3600
        total_time = 2 * (time_hours + DRIVING_EXPERIENCE_FACTOR * (accidents[i] + SNOWFALL_TIME_FACTOR * (snowfall_start[i] + snowfall_end[i])))
        travel_time.append(total_time)
    
    return travel_time

# ==========================
# Formulation
# ==========================

def optimize_ski_resorts(num_people, max_budget, max_time, min_snowfall, w1, w2, w3):
    """Optimize ski resorts and return the top 3 choices."""
    
    # Calculate costs and times
    cost_per_person = calculate_cost_per_person(num_people)
    travel_time = calculate_travel_time()

    # Normalize values
    normalized_snowfall = normalize(snowfall_end)
    normalized_cost = normalize(cost_per_person)
    normalized_time = normalize(travel_time)

    all_scores = []
    selected_resorts = []
    
    print("\n=== Debugging Values ===")
    for i in range(len(miles)):
        score = w1 * normalized_snowfall[i] + w2 * normalized_cost[i] + w3 * normalized_time[i]

        all_scores.append(score)

        print(f"\nResort #{i}: {colorado_ski_resorts[i]}")
        print(f"  Score: {score:.2f}")
        print(f"  Cost per Person: ${cost_per_person[i]}")
        print(f"  Travel Time: {travel_time[i]:.2f} hrs")
        print(f"  Snowfall: {snowfall_end[i]} inches")
        print(f"  Normalized Cost: {normalized_cost[i]:.2f}")
        print(f"  Normalized Time: {normalized_time[i]:.2f}")

        if cost_per_person[i] <= max_budget and travel_time[i] <= max_time and snowfall_end[i] >= min_snowfall:
            selected_resorts.append((i, score))

    # Rank resorts by score
    selected_resorts.sort(key=lambda x: x[1], reverse=True)
    top_3_resorts = selected_resorts[:3]

    # Rank resorts by score
    selected_resorts.sort(key=lambda x: x[1], reverse=True)
    top_3_resorts = selected_resorts[:3]

    return top_3_resorts, cost_per_person, travel_time, all_scores

# ==========================
# Plotting Function
# ==========================

def plot_resort_scores(cost_per_person, travel_time, scores, resort_names, top_resort_indices, rank):
    """Plot resorts on a graph; x-axis = budget, y-axis = travel time."""
    
    plt.figure(figsize=(12, 8))

    # Plot all resorts with default color
    plt.scatter(cost_per_person, travel_time, color='lightgray', edgecolors='black', s=150)

    # Highlight the top resorts with a distinct color
    i = 1
    for idx in top_resort_indices:
        plt.scatter(cost_per_person[idx], travel_time[idx], 
                    color='blue', edgecolors='black', s=150, 
                    label=f'Top Resort #{i}: {resort_names[idx]}')
        i+=1
        
    # Annotate all resorts
    for i, name in enumerate(resort_names):
        plt.annotate(f"{name} ({scores[i]:.2f})", 
                     (cost_per_person[i] + 0.5, travel_time[i] + 0.1), 
                     fontsize=9)

    # Labels and title
    plt.xlabel('Cost per Person ($)', fontsize=12)
    plt.ylabel('Travel Time (hrs)', fontsize=12)
    plt.title('Ski Resorts: Cost vs. Time (Top Resorts Highlighted)', fontsize=14)
    
    # Add legend for top resorts
    plt.legend(loc='upper right')

    plt.grid(True)
    plt.show()

# ==========================
# Output Results
# ==========================

# Optimize
top_3, cost, time, scores = optimize_ski_resorts(num_people, max_budget, max_time, min_snowfall, w1, w2, w3)

# Extract the top resort indices
top_resort_indices = [idx for idx, _ in top_3]

# Print the top resorts in the terminal
print("\n=== Top 3 Ski Resorts ===")
for rank, (resort_idx, score) in enumerate(top_3, start=1):
    print(f"\nRank #{rank}:")
    print(f"  {colorado_ski_resorts[resort_idx]}")
    print(f"  Score: {score:.2f}")
    print(f"  Cost per Person: ${cost[resort_idx]}")
    print(f"  Travel Time: {time[resort_idx]:.2f} hrs")
    print(f"  Snowfall: {snowfall_end[resort_idx]} inches")

# Plot the resorts
plot_resort_scores(cost, time, scores, colorado_ski_resorts, top_resort_indices, rank)


