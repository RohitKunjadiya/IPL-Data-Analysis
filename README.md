# 🏏 IPL Data Analysis & Match Prediction (2008–2025)

An end-to-end **Data Engineering + Data Analysis + Machine Learning** project built on **Indian Premier League (IPL)** data from **2008 to 2025**.

This project demonstrates the complete lifecycle of a real-world data product:

- **Scraping IPL match data** from ESPN Cricinfo
- **Extracting ball-by-ball data** from Cricsheet
- **Storing structured data** in a **Railway Cloud MySQL** database
- **Querying and exporting data** into CSV format
- Performing **Exploratory Data Analysis (EDA)** and **Feature Engineering**
- Building a **Machine Learning model** for IPL-related insights/predictions
- Deploying the final application on **Streamlit Cloud**

---

## 📌 Project Highlights

- Collected **IPL match-level data (2008–2025)** from **ESPN Cricinfo**
- Integrated **ball-by-ball IPL data** from **Cricsheet**
- Designed a **cloud-based MySQL data pipeline** using **Railway**
- Performed **data cleaning, transformation, and analysis**
- Built an **ML-powered IPL analytics/prediction system**
- Deployed an **interactive Streamlit app**

---

## 🚀 Project Workflow

```text
ESPN Cricinfo (Match Data 2008–2025)
            │
            ▼
     Web Scraping (Python)
            │
            ▼
   Match-Level Data Extracted
            │
            ├──────────────────────┐
            │                      │
            ▼                      ▼
   Cricsheet Ball-by-Ball Data   Data Integration
            │                      │
            └──────────────┬───────┘
                           ▼
                Railway Cloud MySQL Database
                           │
                           ▼
                 SQL Queries + Data Extraction
                           │
                           ▼
                   Convert Data into CSV Files
                           │
                           ▼
             EDA + Data Cleaning + Feature Engineering
                           │
                           ▼
                 Machine Learning Model Building
                           │
                           ▼
                  Streamlit Cloud Deployment
