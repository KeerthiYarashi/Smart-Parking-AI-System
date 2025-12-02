# DDCO Project: Smart Parking System - Concept Mapping

This document outlines how the software logic in this project maps to Digital Design and Computer Organization (DDCO) hardware concepts.

## 1. Arithmetic Logic Unit (ALU)
*   **Software Component:** `BillingALU` class (`controller.py`)
*   **Hardware Concept:** The ALU performs arithmetic operations.
*   **Implementation:** 
    *   The `calculate_upfront_cost` method acts as a multiplier circuit.
    *   **Input:** `Duration` (Operand A) and `Rate` (Operand B).
    *   **Operation:** Multiplication (`A * B`).
    *   **Output:** `Total Cost`.
*   **Web Interface:** Visible in the **Simulation Logs** ("Paid: $20.0") and **Reservation Notifications** ("Upfront Payment: $40 Received").

## 2. Priority Encoder
*   **Software Component:** `PriorityEncoder` class (`controller.py`)
*   **Hardware Concept:** Converts multiple active input lines into a binary code representing the highest priority input.
*   **Implementation:**
    *   Maps `Vehicle Type` (Input Signal) to a `Priority Level` (Output Code).
    *   **Logic:** `AMBULANCE` (0) > `VIP` (1) > `EV` (2) > `NORMAL` (4).
    *   Lower number indicates higher interrupt priority.
*   **Web Interface:** Represented by the **Vehicle Entry Buttons**. Clicking "Ambulance" or "VIP" triggers higher priority logic than "Normal".

## 3. Multiplexer (MUX)
*   **Software Component:** `_find_best_slot` method (`controller.py`)
*   **Hardware Concept:** Selects one of several analog or digital input signals and forwards the selected input into a single line.
*   **Implementation:**
    *   **Inputs:** All 12 Parking Slots (Memory Addresses).
    *   **Selection Lines:** `Vehicle Type`, `Traffic Mode` (Control Signals).
    *   **Logic:** 
        *   If `Mode == MANUAL`: Select strictly matching type.
        *   If `Mode == PEAK`: Allow `NORMAL` input to select `VIP` address lines (Overflow).
    *   **Output:** Single `Slot ID`.
*   **Web Interface:** Controlled by the **"System Mode" Dropdown** (Manual/Peak/Event). Changing this changes the internal routing logic for slot selection.

## 4. Finite State Machine (FSM)
*   **Software Component:** `Robot` class & `simulation_step` (`controller.py`)
*   **Hardware Concept:** A sequential circuit that transitions between a finite number of states based on inputs and clock cycles.
*   **Implementation:**
    *   **States:** `IDLE` (00), `MOVING_TO_SLOT` (01), `PARKING` (10), `RETURNING` (11).
    *   **Clock:** The `simulation_step` function acts as the rising edge of the clock.
    *   **Transition Logic:** 
        *   `IDLE` + `Queue Not Empty` -> `MOVING`.
        *   `MOVING` + `Next Clock` -> `PARKING`.
        *   `PARKING` + `Write Complete` -> `RETURNING`.
*   **Web Interface:** Visualized in the **"Auto Sim Control" Panel**. The Robot Cards change color and text (IDLE/MOVING/PARKING) as the state changes.

## 5. Registers & Memory (RAM)
*   **Software Component:** `ParkingLot.slots` dictionary (`controller.py`)
*   **Hardware Concept:** Storage locations for data bits.
*   **Implementation:**
    *   **Address Space:** 12 Slots (Addresses 1-12).
    *   **Word Size:** Stores complex object (Vehicle Type, Entry Time, Status).
    *   **Operations:**
        *   `process_vehicle`: **WRITE** operation to specific address.
        *   `exit_vehicle`: **CLEAR/RESET** operation on specific address.
        *   `reserve_slot`: **LOCK** bit set on address.
*   **Web Interface:** The **"Live Slot Status" Grid**. Each card represents a memory address; Red = Data Stored, Green = Empty (0), Yellow = Locked.

## 6. Shift Register (FIFO Buffer)
*   **Software Component:** `waiting_queue` list (`controller.py`)
*   **Hardware Concept:** A cascade of flip-flops sharing the same clock, used for data storage or transfer.
*   **Implementation:**
    *   Acts as a **First-In-First-Out (FIFO)** buffer for incoming vehicles.
    *   **Shift In:** `add_vehicle_to_queue`.
    *   **Shift Out:** Robot assignment logic removes from the head of the list.
*   **Web Interface:** The **"Queue" Display** in the simulation panel. Cars appear on the right and shift left as they are processed.

## 7. Bus Arbitration
*   **Software Component:** Queue sorting logic in `add_vehicle_to_queue`
*   **Hardware Concept:** Mechanism to decide which device gets control of the bus when multiple devices request it simultaneously.
*   **Implementation:**
    *   **Dynamic Priority:** `Base Priority` + `Arrival Timestamp`.
    *   Ensures high-priority signals (VIP) are inserted ahead of low-priority signals (Normal) in the queue, effectively "seizing the bus" (Robot attention) first.
*   **Web Interface:** Observable in the **Logs**. If a VIP car is added while Normal cars are waiting, the VIP car is processed first.

## 8. Interrupt Handler
*   **Software Component:** Ambulance Logic in `_find_best_slot`
*   **Hardware Concept:** A signal that temporarily halts normal processing to handle a high-priority event.
*   **Implementation:**
    *   If `Type == AMBULANCE`:
        *   Bypasses standard search.
        *   Jumps immediately to Address 12 (Emergency Slot).
        *   Ignores standard "Occupied" checks if necessary (conceptually).
*   **Web Interface:** The **"Emergency / Ambulance" Button**. Clicking it bypasses the queue and immediately allocates a slot.

## 9. Branch Prediction / Pipelining
*   **Software Component:** `PredictionEngine` class (`controller.py`)
*   **Hardware Concept:** Guessing the outcome of a conditional operation to improve flow in the instruction pipeline.
*   **Implementation:**
    *   Analyzes `end_time` of currently parked cars (Memory Look-ahead).
    *   Predicts when a "Write Enable" (Free Slot) will occur.
    *   Calculates probability based on `Queue Length` vs `Free Slots`.
*   **Web Interface:** The **"AI Forecast" Panel** (Doughnut Chart) and **"Upcoming Availability" List** showing predicted free times.

## 10. Control Unit (CU)
*   **Software Component:** `ParkingLot` class
*   **Hardware Concept:** Component of a CPU that directs the operation of the processor.
*   **Implementation:**
    *   Orchestrates the flow of data.
    *   Fetches input from API.
    *   Decodes using `PriorityEncoder`.
    *   Executes using `Robots` or `Manual Entry`.
    *   Writes back to `Slots` (Memory).
*   **Web Interface:** The **Dashboard Controls** (Entry Form, Exit Form, Start/Stop Buttons) act as the input interface to the Control Unit.
