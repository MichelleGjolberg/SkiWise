## Overview
This project uses **Integer Linear Programming (ILP)** to rank and select the top ski resorts based on multiple factors:
- **Cost per person**
- **Travel time**
- **Snowfall conditions**

### **Functionality**
- The ILP model considers **user-defined constraints** (budget, time, snowfall) and finds the top 3 resorts that maximize the weighted score.
- Uses **Big-M formulation** to properly enforce constraints during optimization.
- Outputs the selected resorts along with detailed information on cost, travel time, and scores.

---

## **Prerequisites**

Ensure you have the following installed:

- Python 3.x
- Required libraries:
  - `pulp` → For solving the ILP
  - `math` → For rounding operations

### **Install Required Libraries**
Use `pip` to install the required library:
```bash
pip install pulp
```

---

### **Sample Output**

```
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

Resort #2:
  Score: -1.51
  Cost per Person: $50
  Travel Time: 2.4 hrs
  Fresh Snowfall at Resort: 14 inches
  Normalized Cost: 1.2962962962962963
  Normalized Time: 2.5675675675675675
```