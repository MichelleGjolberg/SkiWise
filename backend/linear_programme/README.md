## Overview
This project uses **Linear Programming (LP)** to rank and select the top ski resorts based on multiple factors:
- **Cost per person**
- **Travel time**
- **Snowfall conditions** (experimental)

### **Functionality**
- The LP model considers **user-defined constraints** (budget, time, snowfall) and finds the top 3 resorts that maximize the weighted score.
- Outputs the selected resorts along with detailed information on cost, travel time, and scores.

---

## **Prerequisites**

Ensure you have the following installed:

- Python 3.x
- Required libraries:
  - `math` → For rounding operations

---

### **Sample Output**

```
.
.
.
Resort 9 removed: Budget or time exceeded.
=== Debugging Values ===
Resort #0:
  Score: -9.56
  Cost per Person: $60
  Travel Time: 4.65 hrs
  Fresh Snowfall at Resort: 12 inches
  Normalized Cost: 1.4444444444444444
  Normalized Time: 5.0

Resort #1:
  Score: -3.22
  Cost per Person: $30
  Travel Time: 1.05 hrs
  Fresh Snowfall at Resort: 7 inches
  Normalized Cost: 1.0
  Normalized Time: 1.1081081081081081

.
.
.

=== Optimal Ski Resorts ===

Rank #1:
  Aspen Mountain
  Score: 3.04
  Cost per Person: $50
  Travel Time: 5.0 hrs
  Fresh Snowfall at Resort: 14 inches
  Normalized Cost: 1.2962962962962963
  Normalized Time: 2.9375

Rank #2:
  Arapahoe Basin
  Score: 0.37
  Cost per Person: $60
  Travel Time: 3.9000000000000004 hrs
  Fresh Snowfall at Resort: 12 inches
  Normalized Cost: 1.4444444444444444
  Normalized Time: 2.25

Rank #3:
  Aspen Highlands
  Score: -0.96
  Cost per Person: $30
  Travel Time: 2.1 hrs
  Fresh Snowfall at Resort: 7 inches
  Normalized Cost: 1.0
  Normalized Time: 1.125
```