# 🏔️ Ski Resort Optimization Project

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

### 📦 **Install Required Libraries**
Use `pip` to install the required library:
```bash
pip install pulp
