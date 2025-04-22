# ❄️ SkiWise: Colorado Ski Trip Optimizer

[Live Demo](http://35.193.237.204/) *(Note: Live site may load slowly or be temporarily unavailable if the database is paused — due to student cloud credits.)*

## Overview

SkiWise is an intelligent ski resort recommendation tool built for skiers and snowboarders planning trips in Colorado. The application helps users find the most optimal resorts based on a personalized combination of preferences such as:

- Starting location  
- Budget per person  
- Maximum travel time  
- Minimum fresh powder  
- Pass type (Ikon, Epic, both, or neither)  
- Driving experience level  

The app uses real-time weather and traffic data to recommend the **top 3 resorts** using a weighted optimization model.

---

## 🔧 Tech Stack

**Frontend:**  
- React
- Typescript  
- Tailwind CSS  

**Backend:**  
- Flask (Python)  
- PostgreSQL (hosted on Google Cloud)  
- dotenv for secure config loading  

**APIs & Services:**  
- Google Maps API → Driving distance & polyline routes  
- Synoptic Weather API → Live snowfall data (1 hr & 24 hr)  
- Google Cloud Platform → VM instance + Cloud SQL
- Docker and Kubernetes → Deployment

---

## ⚙️ Features

- **Smart Optimization:** Linear scoring model ranks resorts by snowfall, cost, and travel time  
- **Live Conditions:** Real-time snowfall and traffic data dynamically influence recommendations  
- **Polyline Mapping:** Directions from user location to resort shown with encoded polyline  
- **Database-Powered:** Resort and weather data stored in Google Cloud-hosted PostgreSQL instance  

---

## 🏔️ Example User Flow

1. User inputs:
    - Start location city or current location  
    - Trip preferences (budget, time, fresh snowfall importance, etc.)  
2. Flask backend fetches live weather & traffic data  
3. Resorts are filtered and ranked using a custom optimization algorithm  
4. Top 3 resorts are returned to the frontend and displayed as resort cards  
5. Resort cards include logo, snowfall (in inches), distance, and driving route  

---

## ⚠️ Notes

- The live demo may occasionally time out or return incomplete results if the backend database instance is not running.
- This is a student project deployed using cloud credits and not maintained for 24/7 uptime.


