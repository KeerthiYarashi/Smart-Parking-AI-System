# Smart Parking AI System - User Guide

Welcome to the **Smart Parking AI System**. This web interface allows you to interact with the underlying Digital Design (DDCO) logic, including the Priority Encoder, FSM Robots, and ALU Billing.

---

## 1. Dashboard Overview

The dashboard is divided into three main glass panels:

*   **Left Panel (AI Forecast):** Displays real-time predictions and probability analysis.
*   **Center Panel (Controls):** The main command center for System Mode selection and Manual Vehicle Entry.
*   **Right Panel (Simulation & Tools):** Controls for the automated robot simulation, reservation, and quick exit.

---

## 2. System Modes (Traffic Patterns)

Located at the top of the **Center Panel**, the **System Mode** dropdown defines the global logic for slot allocation. This affects both manual entries and the simulation.

*   **MANUAL MODE (Strict Types):**
    *   **Logic:** Strict confinement. Normal cars *must* go to Normal slots, VIP to VIP, etc.
    *   **Behavior:** If Normal slots are full, a Normal car will be rejected, even if VIP slots are empty.
    
*   **PEAK HOURS (Normal ➔ VIP Overflow):**
    *   **Scenario:** Morning rush hour where standard parking fills up quickly.
    *   **Logic:** If all **Normal** slots are full, the system allows Normal cars to "overflow" into empty **VIP** slots.
    
*   **EVENT DAY (VIP ➔ Normal Overflow):**
    *   **Scenario:** A concert or game where many VIP guests arrive.
    *   **Logic:** If all **VIP** slots are full, the system allows VIP cars to "overflow" into empty **Normal** slots.

---

## 3. Manual Vehicle Entry

Use the **Center Panel** to park a specific vehicle immediately.

1.  **Set Duration:** Enter the parking duration in hours (e.g., `2.5`).
2.  **Select Vehicle Type:** Click one of the colored buttons:
    *   **🚑 EMERGENCY:** Highest priority. Bypasses queues and takes the Emergency Slot (12) or any available slot immediately.
    *   **👑 VIP:** High priority. Targets Slots 1-2.
    *   **⚡ EV:** Targets Charging Stations (Slots 3-4).
    *   **👴 SENIOR:** Targets Wide Spaces (Slots 5-6).
    *   **🚗 NORMAL:** Targets Standard Slots (7-11).
3.  **Feedback:** A floating notification will appear confirming the assigned slot and the upfront cost calculated by the ALU.

---

## 4. AI Forecast & Analytics (Left Panel)

This panel uses the **Prediction Engine** (Pipelining concept) to look ahead in memory.

*   **Probability Score:** A percentage indicating how likely a new driver is to find a spot immediately. It factors in current free slots, queue length, and simulated "peak time" penalties.
*   **Doughnut Chart:** Visual representation of the risk/success factor.
*   **Upcoming Availability:** A list showing exactly when currently occupied slots will become free (e.g., *"Slot 7 free at 14:30 (in 1h 15m)"*).

---

## 5. Simulation & Automation (Right Panel)

This panel demonstrates the **Finite State Machine (FSM)** and **Shift Register (Queue)** concepts.

*   **Controls:**
    *   **▶ Start / ⏸ Pause:** Starts the system clock. Robots will begin processing the queue.
    *   **+Car / +VIP:** Manually adds a vehicle to the *waiting queue* (Shift Register) without parking it immediately.
    *   **↩️ Undo:** Removes the last vehicle added to the queue.
*   **Robot Status:** Watch the cards change color:
    *   **Grey (IDLE):** Waiting for tasks.
    *   **Blue (MOVING):** Moving to pick up a car.
    *   **Green (PARKING):** Writing data to the slot memory.
*   **Queue Viz:** Visualizes cars waiting to be processed.
*   **Logs:** A scrolling console showing detailed system events (e.g., *"Robot 1 picked up Vehicle 5..."*).

---

## 6. Live Slot Status (The Grid)

The bottom section represents the **System Memory (Register File)**. Each card is a memory address (Slot).

*   **Colors & Status:**
    *   🟢 **Green:** Available (Empty).
    *   🔴 **Red:** Occupied (Data stored). Shows Vehicle Type and Exit Time.
    *   🟡 **Yellow:** Reserved (Locked).
    *   🔵 **Blue Pulse:** Robot Incoming (Cache Lock). A robot has claimed this slot but hasn't arrived yet.
*   **Search Bar:** Filter the grid by typing "VIP", "Slot 5", or "Occupied".

---

## 7. Reservation & Exit

Located at the bottom of the **Right Panel**.

*   **Reserve Slot:**
    *   Locks a specific slot type for a duration.
    *   Calculates and charges the bill upfront.
    *   The slot becomes yellow (LOCKED) and cannot be used by others.
*   **Quick Exit:**
    *   Enter a Slot ID (e.g., `5`) and click Exit.
    *   Clears the memory address, making the slot green (Available) again.

---

## 8. Typical Usage Flow

1.  **Start the Simulation:** Click **▶ Start** in the right panel.
2.  **Add Traffic:** Click **+Car** a few times to build a queue.
3.  **Watch Robots:** Observe Robots 1, 2, and 3 picking up cars based on their Serial Number logic (ID % 3).
4.  **Change Mode:** Switch the center dropdown to **PEAK**.
5.  **Fill Normal Slots:** Add many Normal cars until Slots 7-11 are full.
6.  **Observe Overflow:** Add another Normal car. Watch it get assigned to a **VIP** slot (Slots 1-2) due to the Peak Mode logic.
