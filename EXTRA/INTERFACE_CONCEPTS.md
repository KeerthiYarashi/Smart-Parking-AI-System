# 🖥️ Interface Working & Concept Mapping

This document provides a quick reference for explaining the Web Interface elements during a demo.

---

### 1. Center Panel: Vehicle Entry (Input Unit)
*   **Vehicle Buttons (Ambulance/VIP/Normal):** Clicking these sends a specific signal to the controller. **(Concept: Priority Encoder / Interrupts)**
*   **Duration Input:** User enters time, system calculates cost immediately. **(Concept: ALU - Arithmetic Logic Unit)**
*   **System Mode Dropdown (Manual/Peak/Event):** Changes the internal routing logic for where cars are allowed to park. **(Concept: Multiplexer / Control Signals)**

### 2. Right Panel: Simulation (Control Unit)
*   **Start/Pause Button:** Toggles the system clock on or off. **(Concept: System Clock / Clock Cycle)**
*   **Queue List:** Shows cars waiting to be processed in order. **(Concept: Shift Register / FIFO Buffer)**
*   **Robot Cards (R1, R2, R3):** Visualizes agents changing states (Idle -> Moving -> Parking). **(Concept: Finite State Machine - FSM)**
*   **Logs Console:** Displays the sequential execution of instructions. **(Concept: Instruction Trace / Program Counter)**

### 3. Left Panel: AI Forecast (Pipelining)
*   **Probability Gauge:** Shows the calculated chance of finding a spot based on current memory state. **(Concept: Branch Prediction)**
*   **Upcoming Availability List:** Looks ahead in memory to see when "Write Enable" (free slot) will occur. **(Concept: Pipeline Lookahead)**

### 4. Bottom Grid: Live Status (Memory)
*   **Green Card:** Represents an empty memory address (Bit = 0). **(Concept: Empty Register)**
*   **Red Card:** Represents stored data (Vehicle Type + Time). **(Concept: Occupied Register / Data Word)**
*   **Yellow Card:** Represents a reserved slot that cannot be overwritten. **(Concept: Cache Line Locking)**
*   **Blue Pulse:** Indicates a robot has "claimed" this address before arriving. **(Concept: Bus Arbitration / Lock Signal)**
*   **Search Bar:** Filters the view to show only specific memory addresses. **(Concept: Address Decoder)**

### 5. Actions & Logic
*   **Clicking 'Ambulance':** Bypasses the queue and fills Slot 12 immediately. **(Concept: Hardware Interrupt)**
*   **Clicking 'Reserve':** Pays upfront and locks a specific address. **(Concept: Write Lock)**
*   **Clicking 'Exit':** Clears the data from a slot. **(Concept: Reset Signal / Clear Memory)**
*   **Peak Mode Overflow:** Normal car enters a VIP slot because Normal slots are full. **(Concept: MUX Data Routing)**
