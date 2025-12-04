# 🚗 Smart Parking AI - Complete Features Guide

> A comprehensive guide to all features available in the Smart Parking AI System

![Smart Parking AI](https://img.shields.io/badge/DDCO-Project-blue) ![Version](https://img.shields.io/badge/Version-2.0-green) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📑 Table of Contents

1. [System Overview](#-system-overview)
2. [Getting Started](#-getting-started)
3. [User Authentication](#-user-authentication)
4. [Parking Slot Booking](#-parking-slot-booking)
5. [Slot Reservation](#-slot-reservation)
6. [Quick Exit](#-quick-exit)
7. [User Dashboard](#-user-dashboard)
8. [AI Prediction Engine](#-ai-prediction-engine)
9. [Robot Simulation](#-robot-simulation)
10. [Traffic Modes](#-traffic-modes)
11. [Notifications System](#-notifications-system)
12. [Activity Tracking](#-activity-tracking)
13. [Billing System](#-billing-system)
14. [Search & Filter](#-search--filter)
15. [DDCO Concepts](#-ddco-concepts-implemented)
16. [Troubleshooting](#-troubleshooting)

---

## 🏠 System Overview

The **Smart Parking AI System** is an intelligent parking management solution that demonstrates key **Digital Design and Computer Organization (DDCO)** concepts through a practical, real-world application.

### ✨ Key Features at a Glance

| Feature | Description | Status |
|---------|-------------|:------:|
| 🔐 User Authentication | Register & Login with JWT tokens | ✅ |
| 🅿️ Slot Booking | Book parking slots by vehicle type | ✅ |
| 🔒 Slot Reservation | Reserve slots for future use | ✅ |
| 📊 User Dashboard | View bookings, notifications, activity | ✅ |
| 🧠 AI Prediction | Probability of finding a spot | ✅ |
| 🤖 Robot Simulation | Automated parking demonstration | ✅ |
| 🔔 Notifications | Real-time alerts and updates | ✅ |
| 📋 Activity Log | Track all user actions | ✅ |
| 💳 Billing System | Upfront payment calculation | ✅ |
| 🔍 Search & Filter | Find specific slots quickly | ✅ |

### 🏗️ System Architecture

![System Architecture](https://via.placeholder.com/800x400.png?text=System+Architecture+Diagram)

- **Client-Server Model**: The system follows a client-server architecture where the client (user's browser) communicates with the server (backend API) to perform actions like booking a slot, registering a user, etc.
- **Database**: All data related to users, bookings, slots, etc., is stored in a secure database.
- **AI Module**: The AI prediction engine runs as a separate module that analyzes data and provides predictions on parking availability.
- **Notification Service**: A dedicated service to handle real-time notifications to users.

---

## 🔑 Getting Started

### Prerequisites

- **Web Browser**: Chrome, Firefox, or Edge (latest version)
- **Internet Connection**: Stable internet connection for real-time updates
- **Account**: Register for a new account to access all features

### Installation

No installation is required. The Smart Parking AI System is a web-based application accessible through your browser.

### Accessing the System

1. Open your web browser
2. Go to the Smart Parking AI System URL (provided by the administrator)
3. Log in with your registered credentials

---

## 🔐 User Authentication

### Registration

Create a new account to access booking features.

**Steps:**
1. Navigate to `/login`
2. Click **"Register"** tab
3. Fill in the form:
   - **Full Name**: Your display name
   - **Email**: Valid email address (used for login)
   - **Phone**: Contact number
   - **Password**: 8-72 characters
4. Click **"Create Account"**

**Validation Rules:**
- Email must be unique
- Password: minimum 8 characters, maximum 72 characters
- No special characters (`< > { } $ \ script`) in name/phone

### Login

Access your account with registered credentials.

**Steps:**
1. Navigate to `/login`
2. Enter **Email** and **Password**
3. Click **"Login"**
4. Redirected to home page on success

**Session Details:**
- JWT token stored in browser localStorage
- Token expires after **60 minutes**
- Auto-logout on token expiry

### Logout

End your current session.

**Steps:**
1. Click **"Logout"** button in navigation bar
2. Token cleared from browser
3. Redirected to login page

---

## 🅿️ Parking Slot Booking

### Available Vehicle Types

| Type | Icon | Slots | Rate | Priority |
|------|------|-------|------|----------|
| 🚑 AMBULANCE | Ambulance | Slot 12 (Emergency) | FREE | Highest (0) |
| 👑 VIP | Crown | Slots 1-2 | $20/hr | High (1) |
| ⚡ EV | Bolt | Slots 3-4 | $15/hr | Medium (2) |
| 👴 SENIOR | Person | Slots 5-6 | $5/hr | Low (3) |
| 🚗 NORMAL | Car | Slots 7-11 | $10/hr | Lowest (4) |

### How to Book

1. **Login** to your account (required)
2. On home page, find **"Vehicle Entry"** section
3. Set **Duration** (hours) - minimum 0.5 hours
4. Click vehicle type button (AMBULANCE, VIP, EV, SENIOR, or NORMAL)
5. System assigns best available slot
6. See confirmation with slot number and cost

### Booking Rules

- **Type Matching**: Vehicles are assigned to matching slot types first
- **Overflow (Manual Mode)**: 
  - NORMAL cars can use VIP slots if normal slots are full
  - VIP cars can use NORMAL slots if VIP slots are full
- **Emergency Priority**: AMBULANCE always gets priority

### After Booking

- ✅ Booking saved to database
- ✅ Notification sent
- ✅ Activity logged
- ✅ Slot turns red on grid
- ✅ Countdown timer starts

---

## 🔒 Slot Reservation

Reserve a slot for future use without immediately parking.

### How to Reserve

1. Find **"Reserve Slot"** section (right panel)
2. Set **Duration** (hours)
3. Choose type: **VIP**, **EV**, or **Standard**
4. Slot is locked with 🔒 icon

### Reserved vs Booked

| Aspect | Booking | Reservation |
|--------|---------|-------------|
| Purpose | Immediate parking | Future use |
| Display | Vehicle icon | Lock icon 🔒 |
| Status text | Vehicle type | "LOCKED" |
| Color | Red | Yellow |

---

## ⚡ Quick Exit

### Overview

The Quick Exit feature allows users to leave the parking facility without going through the regular checkout process. This is ideal for users who have time-sensitive departures.

### How to Use

1. **Approach Exit**: Drive to the exit of the parking facility.
2. **Automatic Detection**: The system will automatically detect your vehicle and the slot you occupied.
3. **Quick Exit Button**: Press the **"Quick Exit"** button on the exit terminal.
4. **Confirmation**: A confirmation message will be displayed, showing the total cost.
5. **Payment**: The payment will be processed using the registered payment method.
6. **Exit Barrier**: The exit barrier will open automatically upon successful payment.

### Benefits

- **Time-Saving**: Bypasses the need to stop and pay at a kiosk.
- **Convenience**: Ideal for users in a hurry or with time-sensitive appointments.
- **Automated**: No need to interact with staff or wait in lines.

---

## 📊 User Dashboard

Access at `/dashboard` after login.

### Profile Card

Displays your account information:
- **Avatar**: First letter of your name
- **Name**: Your registered name
- **Email**: Your email address
- **Phone**: Your phone number
- **Book New Slot**: Quick link to home page

### Active Sessions

Shows all your currently active bookings:

| Field | Description |
|-------|-------------|
| Slot Number | Which slot is assigned |
| Status | ACTIVE (green badge) |
| Vehicle Type | NORMAL, VIP, EV, etc. |
| Ends At | When parking time expires |
| Cost | Total billing amount |
| Countdown | Live timer ⏱️ updating every second |
| Extend Button | Add more time to booking |

### Booking History

Table showing all past bookings:
- **Date**: When booking was made
- **Slot**: Slot number
- **Type**: Vehicle type
- **Cost**: Amount paid
- **Status**: ACTIVE / COMPLETED / EXPIRED

### Extend Booking

Add more time to an active booking:

1. Find your active booking card
2. Click **"Extend (+1 Hour)"**
3. Confirm the extension
4. Additional cost calculated and added
5. End time updated

**Extension Limits:**
- Minimum: 0.5 hours
- Maximum: 4 hours per extension

---

## 🧠 AI Prediction Engine

### What It Shows

The AI panel displays:

1. **Probability Percentage**: Chance of finding a parking spot (0-100%)
2. **Doughnut Chart**: Visual representation
3. **Upcoming Availability**: List of slots freeing up soon

### How Probability is Calculated

The probability of finding a parking spot is calculated using a machine learning model that takes into account various factors such as:
- **Historical Data**: Past parking data to identify trends
- **Time of Day**: Peak and off-peak hours
- **Special Events**: Impact of local events on parking availability
- **Weather Conditions**: How weather affects parking patterns

### Using the Prediction

1. Navigate to the AI Prediction section on the dashboard.
2. View the probability percentage and chart.
3. Check the list of upcoming available slots.
4. Plan your visit or booking accordingly.

---

## 🤖 Robot Simulation

### Overview

The Robot Simulation feature allows users to visualize how the parking robot will park their vehicle. This is purely a simulation and does not affect the actual parking process.

### How to Use

1. **Book a Slot**: Ensure you have a confirmed booking for a slot.
2. **Navigate to Simulation**: Go to the Robot Simulation section on the dashboard.
3. **Start Simulation**: Click on the **"Start Simulation"** button.
4. **View Animation**: Watch the animation of the robot parking your vehicle.
5. **Stop Simulation**: Click on **"Stop Simulation"** to end the simulation.

### Benefits

- **Visualization**: See exactly how the robot will park your vehicle.
- **Safety**: Understand the safety measures in place during automated parking.
- **Convenience**: Get a preview of the parking process.

---

## 🚦 Traffic Modes

### Overview

The Traffic Modes feature allows the system to adapt to different traffic conditions in real-time. This ensures optimal performance of the parking system under varying circumstances.

### Modes

1. **Normal Mode**: Regular operation mode under normal traffic conditions.
2. **Heavy Traffic Mode**: Adjusts parameters to manage high volume of vehicles.
3. **Emergency Mode**: Prioritizes emergency vehicles like ambulances.

### How to Switch Modes

- The system automatically detects and switches modes based on real-time traffic data.
- Manual override is also possible by admin through the backend system.

### Impact of Traffic Modes

- **Normal Mode**: Standard operation, no changes to booking or parking procedures.
- **Heavy Traffic Mode**: 
  - Increased security checks
  - Possible delays in slot availability
  - Notifications sent to users about potential delays
- **Emergency Mode**: 
  - Immediate slot reservation for emergency vehicles
  - Suspension of ongoing bookings if

