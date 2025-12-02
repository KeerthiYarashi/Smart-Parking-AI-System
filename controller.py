import random
from datetime import datetime, timedelta

class BillingALU:
    """
    DDCO Concept: Arithmetic Logic Unit (ALU)
    Performs mathematical operations for billing based on rates and time.
    """
    RATES = {
        "VIP": 20,      # High rate ($20/hr)
        "EV": 15,       # Electricity cost ($15/hr)
        "NORMAL": 10,   # Standard ($10/hr)
        "SENIOR": 5,    # Discounted ($5/hr)
        "AMBULANCE": 0  # Free
    }

    def calculate_upfront_cost(self, vehicle_type, duration_hours):
        """
        Calculates bill BEFORE entry based on requested duration.
        """
        rate = self.RATES.get(vehicle_type, 10)
        total = float(duration_hours) * rate
        return round(total, 2)

    def calculate_fee(self, vehicle_type, entry_time):
        # Legacy method for exit-based billing (if needed)
        if not entry_time: return 0.0
        simulated_hours = random.uniform(1.0, 5.0) 
        rate = self.RATES.get(vehicle_type, 10)
        return round(simulated_hours * rate, 2)

class PriorityEncoder:
    """
    DDCO Concept: Priority Encoder & Bus Arbitration
    Maps input signals (Vehicle Types) to Priority Levels.
    Lower number = Higher Priority (Interrupt logic).
    """
    PRIORITIES = {
        "AMBULANCE": 0,
        "VIP": 1,
        "EV": 2,
        "SENIOR": 3,
        "NORMAL": 4,
        "RESERVED": 5 # Reservation placeholder
    }

    def get_priority(self, vehicle_type):
        return self.PRIORITIES.get(vehicle_type, 4)

class PredictionEngine:
    """
    DDCO Concept: Pipelining / Co-processor
    Runs 'concurrently' to forecast slot availability based on 'Memory' (logs).
    """
    def predict(self, slots_data, queue_length=0):
        # Analyze occupied slots to find when they free up
        upcoming_availability = []
        now = datetime.now()
        
        free_count = 0
        for s in slots_data.values():
            if s['vehicle'] is None:
                free_count += 1
            elif s['end_time']:
                # Calculate remaining time
                remaining_seconds = (s['end_time'] - now).total_seconds()
                
                if remaining_seconds > 0:
                    hours = int(remaining_seconds // 3600)
                    mins = int((remaining_seconds % 3600) // 60)
                    
                    upcoming_availability.append({
                        "slot": s['id'],
                        "free_at": s['end_time'].strftime("%H:%M"),
                        "hours_left": hours,
                        "mins_left": mins,
                        "total_seconds": remaining_seconds
                    })
        
        # Sort by soonest available
        upcoming_availability.sort(key=lambda x: x['total_seconds'])

        # Enhanced Probability Logic
        # 1. Effective free slots considers the queue
        effective_free = free_count - queue_length
        
        # 2. Time-based factor (Simulated "Peak Hours")
        current_hour = datetime.now().hour
        is_peak = (8 <= current_hour <= 10) or (17 <= current_hour <= 19)
        
        base_prob = 0.0
        if effective_free > 2: base_prob = 0.9
        elif effective_free > 0: base_prob = 0.4
        else: base_prob = 0.05
        
        # Penalties
        if is_peak: base_prob -= 0.2 # Harder to find spots in peak time
        if queue_length > 0: base_prob -= (queue_length * 0.1)
        
        final_prob = max(0, min(int(base_prob * 100), 100))

        return {
            "probability": final_prob,
            "free_slots": free_count,
            "queue_impact": queue_length,
            "is_peak": is_peak,
            "upcoming": upcoming_availability[:4] # Top 4 soonest freeing slots
        }

class Vehicle:
    """
    DDCO Concept: Register (Stores Vehicle State)
    """
    def __init__(self, v_id, v_type, duration):
        self.id = v_id
        self.type = v_type
        self.duration = duration
        self.state = "WAITING" # WAITING, MOVING, PARKED
        self.assigned_slot = None

class Robot:
    """
    DDCO Concept: Finite State Machine (FSM) Agent
    """
    def __init__(self, r_id):
        self.id = r_id
        self.state = "IDLE" # IDLE, MOVING_TO_SLOT, PARKING, RETURNING
        self.current_vehicle = None
        self.target_slot = None

class ParkingLot:
    def __init__(self, total_slots=12):
        self.total_slots = total_slots
        
        # DDCO Concept: Memory / Register File
        # Added 'robot_assigned' to track robot interaction
        # Added 'is_auto' to track if parked by robot
        self.slots = {
            1: {"id": 1, "type": "VIP", "vehicle": None, "attr": "Near Entrance", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            2: {"id": 2, "type": "VIP", "vehicle": None, "attr": "Near Entrance", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            3: {"id": 3, "type": "EV", "vehicle": None, "attr": "Charging Station", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            4: {"id": 4, "type": "EV", "vehicle": None, "attr": "Charging Station", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            5: {"id": 5, "type": "SENIOR", "vehicle": None, "attr": "Wide Space", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            6: {"id": 6, "type": "SENIOR", "vehicle": None, "attr": "Wide Space", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            7: {"id": 7, "type": "NORMAL", "vehicle": None, "attr": "Standard", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            8: {"id": 8, "type": "NORMAL", "vehicle": None, "attr": "Standard", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            9: {"id": 9, "type": "NORMAL", "vehicle": None, "attr": "Standard", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            10: {"id": 10, "type": "NORMAL", "vehicle": None, "attr": "Standard", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            11: {"id": 11, "type": "NORMAL", "vehicle": None, "attr": "Standard", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False},
            12: {"id": 12, "type": "EMERGENCY", "vehicle": None, "attr": "Exit Ramp", "entry_time": None, "end_time": None, "robot_assigned": None, "is_auto": False}
        }
        
        self.history_log = [] # Sequential Memory
        self.sim_log = [] # Dedicated Simulation Log
        self.encoder = PriorityEncoder()
        self.predictor = PredictionEngine()
        self.alu = BillingALU() # New ALU Module
        self.state = "IDLE" # FSM State

        # Simulation Components
        self.robots = [Robot(1), Robot(2), Robot(3)] # Updated: Added Robot 3
        self.waiting_queue = [] # FIFO Queue (Shift Register)
        self.vehicle_counter = 0
        self.traffic_mode = "MANUAL" # MANUAL, PEAK, EVENT
        self.auto_gen_count = 0 # Track total auto-generated vehicles
        
        # Counters for dynamic priority assignment
        self.type_counters = {
            "AMBULANCE": 0,
            "VIP": 0,
            "EV": 0,
            "SENIOR": 0,
            "NORMAL": 0,
            "RESERVED": 0
        }

    def set_traffic_mode(self, mode):
        self.traffic_mode = mode
        return f"Traffic Pattern set to: {mode}"

    def get_ai_prediction(self):
        return self.predictor.predict(self.slots, len(self.waiting_queue))

    def _find_best_slot(self, vehicle_type, priority):
        # DDCO Concept: Multiplexer (MUX) Logic
        # Selects best output line based on selection inputs (Priority & Type)
        
        # Filter out slots that are occupied OR have a robot assigned
        available_slots = [s for s in self.slots.values() if s['vehicle'] is None and s['robot_assigned'] is None]
        
        if not available_slots:
            return None

        # 1. Emergency Override (Interrupt Handler)
        if vehicle_type == "AMBULANCE":
            # Priority 1: Emergency Slot (ID 12)
            for s in available_slots:
                if s['type'] == "EMERGENCY": return s['id']
            # Priority 2: Any available slot
            return available_slots[0]['id']

        # 2. Strict Type Matching (Comparator Logic)
        # Users requested strict confinement: NORMAL -> NORMAL, VIP -> VIP, EV -> EV
        matching_slots = [s for s in available_slots if s['type'] == vehicle_type]
        
        if matching_slots:
            # Return the first matching slot found
            return matching_slots[0]['id']

        # 3. Adaptive Logic for Peak/Event Modes (Overflow Handling)
        
        # NORMAL CARS: Allow overflow to VIP slots
        # "make this mode available for all vechicle car not only auto cAR"
        # We allow this in PEAK mode AND MANUAL mode (for manual entries)
        if vehicle_type == "NORMAL" and (self.traffic_mode == "PEAK" or self.traffic_mode == "MANUAL"):
            vip_slots = [s for s in available_slots if s['type'] == "VIP"]
            if vip_slots:
                return vip_slots[0]['id']

        # VIP CARS: Allow overflow to NORMAL slots
        # Applies in EVENT mode AND MANUAL mode (for manual entries)
        if vehicle_type == "VIP" and (self.traffic_mode == "EVENT" or self.traffic_mode == "MANUAL"):
            normal_slots = [s for s in available_slots if s['type'] == "NORMAL"]
            if normal_slots:
                return normal_slots[0]['id']

        # If no matching slot is found, return None (Do not allow overflow to other types)
        return None

    def add_vehicle_to_queue(self, v_type, duration):
        """
        Adds a vehicle to the waiting queue (Shift Register Input)
        """
        self.vehicle_counter += 1
        
        # Increment type-specific counter for dynamic priority
        if v_type in self.type_counters:
            self.type_counters[v_type] += 1
        else:
            self.type_counters[v_type] = 1
            
        new_vehicle = Vehicle(self.vehicle_counter, v_type, duration)
        
        # DDCO Concept: Bus Arbitration / Priority Sorting
        # Base Priority from Encoder (Lower is better)
        base_priority = self.encoder.get_priority(v_type)
        
        # Dynamic Priority: Base + (Arrival Order * 0.01)
        # This ensures VIP #1 (1.01) > VIP #2 (1.02) > Normal #1 (4.01)
        # We use the type_counters to track arrival order per type
        arrival_order = self.type_counters.get(v_type, 0)
        final_priority = base_priority + (arrival_order * 0.01)
        
        # Store this calculated priority on the vehicle object for reference if needed
        # (Python allows dynamic attribute assignment)
        new_vehicle.dynamic_priority = final_priority
        
        inserted = False
        for i, v in enumerate(self.waiting_queue):
            # Compare dynamic priorities
            # If new vehicle has lower value (higher priority), insert before current v
            if final_priority < getattr(v, 'dynamic_priority', 999):
                self.waiting_queue.insert(i, new_vehicle)
                inserted = True
                break
        
        if not inserted:
            self.waiting_queue.append(new_vehicle)
            
        # Robot Logging
        # Updated log to include Priority
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] QUEUE ADD: {v_type} #{arrival_order} | Priority: {final_priority:.2f} | Duration: {duration}h"
        self.sim_log.append(log_entry)

        return f"Vehicle {new_vehicle.id} ({v_type}) [Prio: {final_priority:.2f}] added."

    def remove_last_vehicle(self):
        """
        Removes the most recently added vehicle from the waiting queue (Undo operation)
        """
        if not self.waiting_queue:
            return "Queue is empty. Nothing to undo."
        
        # Find vehicle with highest ID (newest)
        last_vehicle = max(self.waiting_queue, key=lambda v: v.id)
        self.waiting_queue.remove(last_vehicle)
        
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ↩️ UNDO: Removed Vehicle {last_vehicle.id} ({last_vehicle.type}) from queue."
        self.sim_log.append(log_entry)
        
        return f"↩️ Undo: Vehicle {last_vehicle.id} removed from queue."

    def simulation_step(self):
        """
        DDCO Concept: System Clock Cycle
        Executes one step of the FSM for all robots.
        """
        logs = []
        
        # 1. Traffic Generation (Arrival Pattern Customization)
        if self.traffic_mode != "MANUAL":
            chance = random.random()
            spawn = False
            v_type = "NORMAL"
            
            if self.traffic_mode == "PEAK":
                # Reduced frequency (20% per tick) to slow down logs
                if chance < 0.2: spawn = True 
            
            elif self.traffic_mode == "EVENT":
                # Reduced frequency (15% per tick)
                if chance < 0.15: 
                    spawn = True
                    if random.random() < 0.7: v_type = "VIP" # 70% VIP on event days

            if spawn:
                self.auto_gen_count += 1
                dur = round(random.uniform(1.0, 4.0), 1)
                msg = self.add_vehicle_to_queue(v_type, dur)
                logs.append(f"⚡ Auto-Gen #{self.auto_gen_count}: {msg}")

        # 2. FSM State Updates (Process existing tasks first)
        for robot in self.robots:
            if robot.state == "MOVING_TO_SLOT":
                robot.state = "PARKING"
                logs.append(f"🤖 Robot {robot.id} arriving at Slot {robot.target_slot}...")

            elif robot.state == "PARKING":
                # FSM Transition: PARKING -> RETURNING
                # Commit to Memory (Write)
                slot_id = robot.target_slot
                vehicle = robot.current_vehicle
                
                # Calculate Cost using ALU
                cost = self.alu.calculate_upfront_cost(vehicle.type, vehicle.duration)

                self.slots[slot_id]['vehicle'] = vehicle.type
                self.slots[slot_id]['is_auto'] = True # Mark as Automated
                self.slots[slot_id]['entry_time'] = datetime.now()
                self.slots[slot_id]['end_time'] = datetime.now() + timedelta(hours=float(vehicle.duration))
                self.slots[slot_id]['robot_assigned'] = None # Unlock
                
                robot.state = "RETURNING"
                robot.current_vehicle = None
                robot.target_slot = None
                
                logs.append(f"✅ Robot {robot.id} parked Vehicle {vehicle.id} in Slot {slot_id}. 💳 Paid: ${cost}")

            elif robot.state == "RETURNING":
                # FSM Transition: RETURNING -> IDLE
                robot.state = "IDLE"
                logs.append(f"🤖 Robot {robot.id} returned to base.")

        # 3. Assign Idle Robots to Waiting Vehicles (MODIFIED: Serial Number Dependency)
        # Logic: Vehicle ID % Num_Robots determines the assigned robot.
        
        vehicles_to_remove = []
        
        for vehicle in self.waiting_queue:
            # Determine target robot based on Vehicle ID (Serial No)
            # ID 1 -> Index 0 (Robot 1)
            # ID 2 -> Index 1 (Robot 2)
            # ID 3 -> Index 2 (Robot 3)
            # ID 4 -> Index 0 (Robot 1)
            target_robot_index = (vehicle.id - 1) % len(self.robots)
            target_robot = self.robots[target_robot_index]
            
            # Only assign if the SPECIFIC robot is IDLE
            if target_robot.state == "IDLE":
                priority = self.encoder.get_priority(vehicle.type)
                slot_id = self._find_best_slot(vehicle.type, priority)
                
                if slot_id:
                    # FSM Transition: IDLE -> MOVING_TO_SLOT
                    target_robot.state = "MOVING_TO_SLOT"
                    target_robot.current_vehicle = vehicle
                    target_robot.target_slot = slot_id
                    
                    # Lock the slot
                    self.slots[slot_id]['robot_assigned'] = target_robot.id
                    logs.append(f"🤖 Robot {target_robot.id} [Serial Match] picked up Vehicle {vehicle.id} ({vehicle.type}) -> Slot {slot_id}")
                    
                    vehicles_to_remove.append(vehicle)
                else:
                    # Log warning only if it's the first vehicle to avoid spam
                    if vehicle == self.waiting_queue[0]:
                        logs.append(f"⚠️ No slot for Vehicle {vehicle.id}. Waiting...")
            
            # If target robot is busy, this vehicle waits in queue.
            # We continue loop to see if other vehicles match other idle robots?
            # Yes, this allows out-of-order processing if R2 is free but R1 is busy with V1.
            # V2 (mapped to R2) can be processed.
        
        # Remove assigned vehicles
        for v in vehicles_to_remove:
            self.waiting_queue.remove(v)

        return {
            "logs": logs,
            "robots": [{"id": r.id, "state": r.state, "vehicle": r.current_vehicle.type if r.current_vehicle else None} for r in self.robots],
            "queue_len": len(self.waiting_queue),
            "total_gen": self.auto_gen_count
        }

    def reserve_slot(self, vehicle_type, duration):
        """
        DDCO Concept: Cache Line Locking with Upfront Billing
        """
        priority = self.encoder.get_priority(vehicle_type)
        slot_id = self._find_best_slot(vehicle_type, priority)
        
        if slot_id is None:
            return "❌ Cannot Reserve: No suitable slot available."
            
        # Calculate Upfront Cost
        cost = self.alu.calculate_upfront_cost(vehicle_type, duration)
        
        self.slots[slot_id]['vehicle'] = "RESERVED"
        self.slots[slot_id]['is_auto'] = False
        self.slots[slot_id]['entry_time'] = datetime.now()
        self.slots[slot_id]['end_time'] = datetime.now() + timedelta(hours=float(duration))
        
        return f"🔒 Slot {slot_id} LOCKED for {duration} hrs. 💳 Upfront Payment: ${cost} Received."

    def process_vehicle(self, vehicle_type, duration):
        priority = self.encoder.get_priority(vehicle_type)
        self.state = "ALLOCATE"
        
        slot_id = self._find_best_slot(vehicle_type, priority)

        if slot_id is None:
            self.state = "FULL"
            return f"⛔ Parking FULL! No suitable slot for {vehicle_type}."

        # Calculate Upfront Cost
        cost = self.alu.calculate_upfront_cost(vehicle_type, duration)

        self.state = "GATE_OPEN"
        
        # Write to Register (Memory)
        self.slots[slot_id]['vehicle'] = vehicle_type
        self.slots[slot_id]['is_auto'] = False # Manual Entry
        self.slots[slot_id]['entry_time'] = datetime.now()
        self.slots[slot_id]['end_time'] = datetime.now() + timedelta(hours=float(duration))
        
        self.history_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": vehicle_type,
            "action": "ENTRY",
            "slot": slot_id,
            "duration": duration,
            "cost": cost
        })

        self.state = "IDLE"
        
        return f"✅ Slot {slot_id} Assigned. 💳 Bill Paid: ${cost} (for {duration} hrs)."

    def exit_vehicle(self, slot_id):
        if slot_id not in self.slots:
            return "Invalid Slot"
        
        if self.slots[slot_id]['vehicle'] is None:
            return "Slot already empty"

        v_type = self.slots[slot_id]['vehicle']
        
        # Clear Register
        self.slots[slot_id]['vehicle'] = None
        self.slots[slot_id]['is_auto'] = False
        self.slots[slot_id]['entry_time'] = None
        self.slots[slot_id]['end_time'] = None
        
        self.history_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": v_type,
            "action": "EXIT",
            "slot": slot_id
        })
        
        return f"👋 Vehicle exited Slot {slot_id}. Slot is now FREE."

    def get_status(self):
        return self.slots
