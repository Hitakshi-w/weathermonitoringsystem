# Weather Monitoring and Alert Application

This application monitors weather data for specified cities using the OpenWeatherMap API, stores it in a local SQLite database, generates alerts when temperature thresholds are exceeded, and visualizes the data using Streamlit.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)


---

## Overview

This application:
1. Fetches weather data for specified cities at set intervals.
2. Stores real-time weather data in an SQLite database.
3. Tracks daily summaries and alerts when temperatures exceed user-defined thresholds.
4. Displays weather data, daily summaries, and alerts in an interactive Streamlit dashboard.

## Features

- **Weather Data Retrieval**: Retrieves weather data from OpenWeatherMap API for cities such as Delhi, Mumbai, Chennai, Bangalore, Kolkata, and Hyderabad.
- **SQLite Database Storage**: Saves real-time data and daily summaries, organized by city and date.
- **Temperature Alerts**: Issues alerts if the temperature exceeds a defined threshold consecutively.
- **Data Visualization**: Shows raw data, daily summaries, and historical alerts through Streamlit.

## Requirements

To run this application, ensure the following dependencies are installed:
- `python3`
- `sqlite3`
- `requests`
- `pandas`
- `streamlit`

You can install the Python packages using the following:
```bash
pip install sqlite3 requests pandas streamlit
```
## Setup

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```
# Obtain an API Key from OpenWeatherMap
1. Sign up at OpenWeatherMap and create an API key.
2. Replace `your_api_key` in the code with your actual API key.

## Configuration
The following parameters can be configured:

- **ALERT_THRESHOLD**: Temperature (in Celsius) above which an alert is triggered.
- **CONSECUTIVE_ALERTS**: Number of consecutive readings above the threshold to trigger an alert.
- **INTERVAL**: Time interval (in seconds) between data fetches (default is 5 minutes).

## Usage

# Run the Application
```bash
streamlit run weather_monitor.py
```
# Access the Streamlit Dashboard
Open your browser and navigate to the URL provided by Streamlit (usually http://localhost:8501).

# Interact with the Dashboard
View live weather data, daily summaries, and alerts.






