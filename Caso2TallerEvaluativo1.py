import tkinter as tk


def build_ui():
    window = tk.Tk()
    window.geometry("420x360")
    window.title("Activity One")

    result = tk.Label(window, text="Result: ")
    result.pack(pady=5)

    # 1
    list_a = ["Coconut", "Watermelon", "Apple", "Cherry", "Strawberry"]
    list_b = [
        ["Minecraft", "Terraria", "Pac-Man"],
        ["Hollow Knight", "Celeste", "Doom"],
        ["The Forest", "Raft", "Subnautica"],
    ]

    # 2
    tk.Label(window, text="List_1 (1x5)", font=("Arial", 10, "bold")).pack(pady=5)
    interactive_box_a = []
    frame_a = tk.Frame(window)
    frame_a.pack(pady=5)

    for i, value in enumerate(list_a):
        entry = tk.Entry(frame_a, width=10)
        entry.grid(row=0, column=i, padx=2)
        entry.insert(0, value)
        interactive_box_a.append(entry)

    tk.Label(window, text="List_2 (3x3)", font=("Arial", 10, "bold")).pack(pady=5)
    interactive_box_b = []
    frame_b = tk.Frame(window)
    frame_b.pack(pady=5)

    for f, row_values in enumerate(list_b):
        row_box = []
        for c, value in enumerate(row_values):
            entry = tk.Entry(frame_b, width=10)
            entry.grid(row=f, column=c, padx=2, pady=2)
            entry.insert(0, value)
            row_box.append(entry)
        interactive_box_b.append(row_box)

    # 3
    def save_data():
        try:
            saved_list_a = [e.get() for e in interactive_box_a]
            saved_list_b = [[e.get() for e in row] for row in interactive_box_b]
            result.config(text=f"list_create:\nA: {saved_list_a}\nB: {saved_list_b}")
        except Exception:
            result.config(text="mistake")

    button_save = tk.Button(window, text="save and show list", command=save_data, bg="lightgreen")
    button_save.pack(pady=10)

    return window


if __name__ == "__main__":
    window = build_ui()
    window.mainloop()
    
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


VALID_TYPES = ["PORTABLE", "KIT", "MULTIMETER"]
VALID_STATES = ["IN_CART", "LOANED", "UNDER_REVIEW", "MAINTENANCE"]
RULE_MESSAGES = {
    "R1": "R1: A student cannot have two equipment items of the same type at the same time or be queued twice for the same type.",
    "R2": "R2: A normal loan must deliver the equipment on top of the cart.",
    "R3": "R3: If the cart is empty, the request goes to the waiting queue for that type.",
    "R4": "R4: Directed loan must preserve the original order of the cart.",
    "R5": "R5: All returned equipment first enters the review queue.",
    "R6": "R6: An overdue student cannot request more equipment until returning the current equipment.",
    "R7": "R7: A cart has a maximum capacity; if a reviewed item does not fit, it remains in the storage queue.",
    "R8": "R8: Any equipment with 5 loans enters preventive maintenance when returned.",
}


@dataclass
class Equipment:
    code: str
    type: str
    state: str = "IN_CART"
    loans: int = 0
    owner: Optional[str] = None
    loan_start: Optional[int] = None
    loaned_at: Optional[int] = None
    last_return_hour: Optional[int] = None


class Node:
    def __init__(self, value: Any):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value: Any):
        node = Node(value)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove_by_code(self, code: str):
        current = self.head
        previous = None
        while current is not None:
            if current.value.code == code:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if self.tail == current:
                    self.tail = previous
                self.size -= 1
                return current.value
            previous = current
            current = current.next
        return None

    def find_by_code(self, code: str):
        current = self.head
        while current is not None:
            if current.value.code == code:
                return current.value
            current = current.next
        return None

    def all(self):
        result = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result


class Queue:
    def __init__(self):
        self.items: List[Any] = []

    def enqueue(self, item: Any):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise ValueError("Queue is empty")
        return self.items.pop(0)

    def front(self):
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return list(self.items)


class Stack:
    def __init__(self):
        self.items: List[Any] = []

    def push(self, item: Any):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            raise ValueError("Stack is empty")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return list(self.items)

    def find_position_from_top(self, code: str):
        for index, item in enumerate(reversed(self.items)):
            if item.code == code:
                return index
        return None


class LabSystem:
    def __init__(self, capacity: int = 5, overdue_hours: int = 8):
        self.capacity = capacity
        self.overdue_hours = overdue_hours
        self.inventory = LinkedList()
        self.carts = {item_type: Stack() for item_type in VALID_TYPES}
        self.waiting_queues = {item_type: Queue() for item_type in VALID_TYPES}
        self.review_queue = Queue()
        self.storage_queue = Queue()
        self.logs: List[str] = []
        self.directed_loans = 0
        self.directed_moves_total = 0
        self.queued_requests = 0
        self.immediate_requests = 0
        self.wait_minutes_total = 0
        self.issued_waited_requests = 0
        self.last_directed_trace: List[str] = []
        self.student_active_loans: Dict[str, List[str]] = {}
        self.student_waiting: Dict[str, List[str]] = {}
        self.loan_start_hours: Dict[str, int] = {}
        self.return_record: Dict[str, Dict[str, Any]] = {}
        self._sample_loaded = False

    def log(self, message: str):
        self.logs.append(message)

    def _student_is_overdue(self, student: str):
        for code, start_hour in self.loan_start_hours.items():
            equipment = self.inventory.find_by_code(code)
            if equipment and equipment.owner == student:
                current_hour = start_hour
                if current_hour is not None:
                    elapsed = max(0, 0)
                    if equipment.last_return_hour is not None:
                        elapsed = equipment.last_return_hour - start_hour
                    if elapsed > self.overdue_hours:
                        return True
        return False

    def _student_has_type(self, student: str, item_type: str):
        for equipment in self.inventory.all():
            if equipment.owner == student and equipment.type == item_type and equipment.state == "LOANED":
                return True
        return False

    def _student_waiting_for_type(self, student: str, item_type: str):
        for request in self.waiting_queues[item_type].to_list():
            if request.get("student") == student:
                return True
        return False

    def _equipment_in_cart(self, code: str):
        for item_type in VALID_TYPES:
            cart = self.carts[item_type]
            for equipment in cart.to_list():
                if equipment.code == code:
                    return equipment
        return None

    def add_equipment(self, code: str, item_type: str, state: str = "IN_CART", loans: int = 0, owner: Optional[str] = None):
        if item_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {item_type}")
        if state not in VALID_STATES:
            raise ValueError(f"Invalid state: {state}")
        if self.inventory.find_by_code(code) is not None:
            raise ValueError(f"Equipment {code} already exists")

        equipment = Equipment(code=code, type=item_type, state=state, loans=loans, owner=owner)
        self.inventory.append(equipment)

        if state == "IN_CART":
            if self.carts[item_type].size() < self.capacity:
                self.carts[item_type].push(equipment)
            else:
                self.storage_queue.enqueue(equipment)
                self.log(f"Equipment {code} stored in the storage queue because the cart for {item_type} is full.")

        self.log(f"Added equipment {code} of type {item_type} with state {state}.")
        return equipment

    def remove_equipment(self, code: str):
        equipment = self.inventory.find_by_code(code)
        if equipment is None:
            raise ValueError(f"Equipment {code} does not exist")

        for item_type in VALID_TYPES:
            if equipment in self.carts[item_type].to_list():
                # Remove from stack without changing stack order by reconstructing the stack
                current = self.carts[item_type]
                temp = Stack()
                while not current.is_empty():
                    item = current.pop()
                    if item.code != code:
                        temp.push(item)
                while not temp.is_empty():
                    current.push(temp.pop())
                break

        self.inventory.remove_by_code(code)
        self.log(f"Removed equipment {code} from the inventory.")
        return equipment

    def inventory_snapshot(self, item_type: Optional[str] = None, state: Optional[str] = None):
        items = self.inventory.all()
        if item_type is not None:
            items = [item for item in items if item.type == item_type]
        if state is not None:
            items = [item for item in items if item.state == state]
        return [
            {
                "code": item.code,
                "type": item.type,
                "state": item.state,
                "loans": item.loans,
                "owner": item.owner,
            }
            for item in items
        ]

    def cart_snapshot(self, item_type: str):
        return [
            {
                "code": item.code,
                "type": item.type,
                "state": item.state,
                "loans": item.loans,
                "owner": item.owner,
            }
            for item in self.carts[item_type].to_list()
        ]

    def waiting_snapshot(self, item_type: str):
        return list(self.waiting_queues[item_type].to_list())

    def review_snapshot(self):
        return list(self.review_queue.to_list())

    def storage_snapshot(self):
        return list(self.storage_queue.to_list())

    def load_sample_data(self):
        self.inventory = LinkedList()
        self.carts = {item_type: Stack() for item_type in VALID_TYPES}
        self.waiting_queues = {item_type: Queue() for item_type in VALID_TYPES}
        self.review_queue = Queue()
        self.storage_queue = Queue()
        self.logs = []
        self.directed_loans = 0
        self.directed_moves_total = 0
        self.queued_requests = 0
        self.immediate_requests = 0
        self.wait_minutes_total = 0
        self.issued_waited_requests = 0
        self.last_directed_trace = []
        self.student_active_loans = {}
        self.student_waiting = {}
        self.loan_start_hours = {}
        self.return_record = {}

        sample = [
            {"code": "PORT-01", "type": "PORTABLE", "state": "IN_CART", "loans": 2},
            {"code": "PORT-02", "type": "PORTABLE", "state": "IN_CART", "loans": 1},
            {"code": "PORT-03", "type": "PORTABLE", "state": "IN_CART", "loans": 3},
            {"code": "PORT-04", "type": "PORTABLE", "state": "LOANED", "loans": 4, "owner": "S-101", "loan_start": 80},
            {"code": "KIT-01", "type": "KIT", "state": "IN_CART", "loans": 2},
            {"code": "KIT-02", "type": "KIT", "state": "IN_CART", "loans": 2},
            {"code": "KIT-03", "type": "KIT", "state": "LOANED", "loans": 5, "owner": "S-104", "loan_start": 75},
            {"code": "MULT-01", "type": "MULTIMETER", "state": "IN_CART", "loans": 1},
            {"code": "MULT-02", "type": "MULTIMETER", "state": "IN_CART", "loans": 0},
            {"code": "MULT-03", "type": "MULTIMETER", "state": "IN_CART", "loans": 1},
        ]

        for item in sample:
            equipment = Equipment(
                code=item["code"],
                type=item["type"],
                state=item["state"],
                loans=item["loans"],
                owner=item.get("owner"),
                loan_start=item.get("loan_start"),
            )
            self.inventory.append(equipment)
            if item["state"] == "IN_CART":
                self.carts[item["type"]].push(equipment)
            elif item["state"] == "LOANED":
                self.student_active_loans.setdefault(item["owner"], []).append(item["code"])
                self.loan_start_hours[item["code"]] = item["loan_start"]
                equipment.state = "LOANED"
        self._sample_loaded = True
        self.log("Sample data loaded successfully.")

    def _validate_request(self, student: str, item_type: str):
        if self._student_has_type(student, item_type):
            raise ValueError(RULE_MESSAGES["R1"])
        if self._student_waiting_for_type(student, item_type):
            raise ValueError(RULE_MESSAGES["R1"])
        for equipment in self.inventory.all():
            if equipment.owner == student and equipment.state == "LOANED":
                if equipment.type != item_type and equipment.loans > self.overdue_hours:
                    raise ValueError(RULE_MESSAGES["R6"])
                if equipment.last_return_hour is not None and (equipment.last_return_hour - self.loan_start_hours.get(equipment.code, 0)) > self.overdue_hours:
                    raise ValueError(RULE_MESSAGES["R6"])
        if self._student_has_overdue_loan(student):
            raise ValueError(RULE_MESSAGES["R6"])

    def _student_has_overdue_loan(self, student: str):
        for equipment in self.inventory.all():
            if equipment.owner == student and equipment.state == "LOANED":
                if self.loan_start_hours.get(equipment.code) is not None:
                    if (equipment.last_return_hour or 0) - self.loan_start_hours[equipment.code] > self.overdue_hours:
                        return True
        return False

    def solicitar(self, student: str, item_type: str, hour: int):
        self._validate_request(student, item_type)
        if self.carts[item_type].is_empty():
            self.waiting_queues[item_type].enqueue({"student": student, "type": item_type, "hour": hour})
            self.queued_requests += 1
            self.issued_waited_requests += 1
            self.log(f"Request queued for student {student} on {item_type} at hour {hour}.")
            return {"status": "queued", "rule": "R3"}

        equipment = self.prestar(item_type)
        equipment.owner = student
        equipment.state = "LOANED"
        equipment.loan_start = hour
        self.loan_start_hours[equipment.code] = hour
        self.student_active_loans.setdefault(student, []).append(equipment.code)
        self.immediate_requests += 1
        self.log(f"Immediate loan delivered to {student} for {equipment.code}.")
        return {"status": "issued", "code": equipment.code, "type": item_type, "student": student}

    def prestar(self, item_type: str):
        if self.carts[item_type].is_empty():
            raise ValueError(RULE_MESSAGES["R2"])
        equipment = self.carts[item_type].pop()
        equipment.state = "LOANED"
        self.log(f"Equipment {equipment.code} was loaned from the {item_type} cart.")
        return equipment

    def prestar_dirigido(self, code: str):
        equipment = self.inventory.find_by_code(code)
        if equipment is None:
            raise ValueError(f"Equipment {code} does not exist")
        if equipment.state != "IN_CART":
            raise ValueError("R4: The equipment is not available in a cart to be borrowed directly.")
        cart = self.carts[equipment.type]
        if cart.is_empty():
            raise ValueError("R4: The cart is empty.")

        auxiliary = Stack()
        trace = []
        while not cart.is_empty() and cart.peek().code != code:
            moved = cart.pop()
            auxiliary.push(moved)
            trace.append(f"Moved {moved.code} from main cart to auxiliary cart.")

        if cart.is_empty():
            raise ValueError(f"Equipment {code} not found in the {equipment.type} cart.")

        target = cart.pop()
        trace.append(f"Removed {target.code} from the main cart.")
        target.state = "LOANED"
        self.directed_loans += 1

        while not auxiliary.is_empty():
            restored = auxiliary.pop()
            cart.push(restored)
            trace.append(f"Restored {restored.code} to the main cart.")

        self.last_directed_trace = trace
        self.directed_moves_total += len(trace)
        self.log(f"Directed loan for {code} completed in {len(trace)} movements.")
        return {"code": code, "movements": len(trace), "trace": trace}

    def devolver(self, code: str, hour: int):
        equipment = self.inventory.find_by_code(code)
        if equipment is None:
            raise ValueError(f"Equipment {code} does not exist")
        if equipment.state != "LOANED":
            raise ValueError("The equipment is not currently loaned.")

        duration = hour - self.loan_start_hours.get(code, hour)
        equipment.last_return_hour = hour
        equipment.state = "UNDER_REVIEW"
        equipment.owner = None
        self.return_record[code] = {"student": equipment.owner, "hour": hour, "duration": duration}
        self.review_queue.enqueue(equipment)
        self.log(f"Equipment {code} returned at hour {hour} and sent to the review queue.")
        return duration

    def revisar(self, decision: str):
        if self.review_queue.is_empty():
            raise ValueError("The review queue is empty.")

        equipment = self.review_queue.dequeue()
        equipment.owner = None
        if decision == "APPROVE":
            if equipment.loans >= 5:
                equipment.state = "MAINTENANCE"
                self.log(f"Equipment {equipment.code} entered preventive maintenance because it exceeded 5 loans.")
                return {"status": "maintenance", "code": equipment.code}
            if self.carts[equipment.type].size() < self.capacity:
                self.carts[equipment.type].push(equipment)
                equipment.state = "IN_CART"
                self.log(f"Equipment {equipment.code} approved and returned to the {equipment.type} cart.")
                self._serve_waiting_if_possible(equipment.type)
                return {"status": "approved", "code": equipment.code}
            self.storage_queue.enqueue(equipment)
            equipment.state = "IN_CART"
            self.log(f"Equipment {equipment.code} was approved but stored in the waiting storage queue because the cart is full.")
            return {"status": "stored", "code": equipment.code}

        if decision == "DAMAGED":
            equipment.state = "MAINTENANCE"
            self.log(f"Equipment {equipment.code} was reported as damaged and moved to maintenance.")
            return {"status": "damaged", "code": equipment.code}

        raise ValueError("The review decision must be APPROVE or DAMAGED.")

    def _serve_waiting_if_possible(self, item_type: str):
        waiting_queue = self.waiting_queues[item_type]
        if waiting_queue.is_empty() or self.carts[item_type].is_empty():
            return None

        request = waiting_queue.dequeue()
        student = request["student"]
        equipment = self.carts[item_type].pop()
        equipment.owner = student
        equipment.state = "LOANED"
        self.loan_start_hours[equipment.code] = request["hour"]
        self.student_active_loans.setdefault(student, []).append(equipment.code)
        self.log(f"Waiting request served for student {student} using equipment {equipment.code}.")
        return equipment

    def atender_espera(self, item_type: str):
        if item_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {item_type}")
        self._serve_waiting_if_possible(item_type)
        return self.waiting_queues[item_type].to_list()

    def buscar(self, code: str):
        equipment = self.inventory.find_by_code(code)
        if equipment is None:
            raise ValueError(f"Equipment {code} does not exist")

        position = None
        if equipment.state == "IN_CART":
            position = self.carts[equipment.type].find_position_from_top(code)

        return {
            "code": equipment.code,
            "type": equipment.type,
            "state": equipment.state,
            "loans": equipment.loans,
            "owner": equipment.owner,
            "position_from_top": position,
        }

    def generate_report(self):
        states = {state: 0 for state in VALID_STATES}
        by_type = {item_type: 0 for item_type in VALID_TYPES}
        cart_usage = {}

        for equipment in self.inventory.all():
            states[equipment.state] = states.get(equipment.state, 0) + 1
            by_type[equipment.type] = by_type.get(equipment.type, 0) + 1

        for item_type in VALID_TYPES:
            cart_usage[item_type] = {
                "count": self.carts[item_type].size(),
                "capacity": self.capacity,
                "occupied": (self.carts[item_type].size() / self.capacity) * 100,
            }

        immediate = self.immediate_requests
        queued = self.queued_requests
        average_wait = 0 if queued == 0 else self.wait_minutes_total / queued

        damaged = sum(1 for item in self.inventory.all() if item.state == "MAINTENANCE" and item.loans >= 1)
        overdue_students = 0
        for student in self.student_active_loans:
            if self._student_has_overdue_loan(student):
                overdue_students += 1

        most_borrowed = None
        max_loans = -1
        for item in self.inventory.all():
            if item.loans > max_loans:
                max_loans = item.loans
                most_borrowed = item.code

        preventive = sum(1 for item in self.inventory.all() if item.loans >= 5 and item.state == "MAINTENANCE")

        return {
            "equipment_by_state": states,
            "equipment_by_type": by_type,
            "cart_usage": cart_usage,
            "requests": {"immediate": immediate, "queued": queued, "average_wait_minutes": average_wait},
            "directed_loans": self.directed_loans,
            "directed_moves_total": self.directed_moves_total,
            "damaged_returns": damaged,
            "maintenance_items": sum(1 for item in self.inventory.all() if item.state == "MAINTENANCE"),
            "overdue_students": overdue_students,
            "most_borrowed": most_borrowed,
            "preventive_maintenance": preventive,
        }

    def get_log_text(self):
        return "\n".join(self.logs[-20:]) if self.logs else "No operations recorded yet."

    def get_last_directed_result(self):
        return self.last_directed_trace


class ActivityOneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity One")
        self.root.geometry("1366x768")
        self.root.configure(bg="#f5f5f5")
        self.system = LabSystem(capacity=5, overdue_hours=8)

        self.nav = tk.Frame(self.root, bg="#111827", padx=12, pady=10)
        self.nav.pack(fill="x")

        self.pages = {}
        self.make_nav_button("Inventory", "inventory")
        self.make_nav_button("Loan Counter", "loan")
        self.make_nav_button("Carts", "carts")
        self.make_nav_button("Review & Reports", "review")

        tk.Button(self.nav, text="Load sample data", command=self.load_sample_data, bg="#d4edda", fg="#111827").pack(side="right", padx=5)

        self.page_container = tk.Frame(self.root)
        self.page_container.pack(fill="both", expand=True)

        self.build_inventory_page()
        self.build_loan_page()
        self.build_carts_page()
        self.build_review_page()

        self.current_page = "inventory"
        self.show_page("inventory")
        self.refresh_all()

    def make_nav_button(self, label, page_name):
        btn = tk.Button(self.nav, text=label, command=lambda: self.show_page(page_name), bg="#1f2937", fg="white")
        btn.pack(side="left", padx=5)

    def show_page(self, page_name):
        self.current_page = page_name
        for name, frame in self.pages.items():
            frame.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)

    def build_inventory_page(self):
        page = tk.Frame(self.page_container)
        self.pages["inventory"] = page

        controls = tk.Frame(page, padx=14, pady=10)
        controls.pack(fill="x")

        tk.Label(controls, text="Filter by type:", font=("Arial", 10, "bold")).pack(side="left")
        self.inventory_type_var = tk.StringVar(value="ALL")
        type_options = ["ALL"] + VALID_TYPES
        type_combo = ttk.Combobox(controls, textvariable=self.inventory_type_var, values=type_options, state="readonly", width=15)
        type_combo.pack(side="left", padx=(8, 14))

        tk.Label(controls, text="Filter by state:", font=("Arial", 10, "bold")).pack(side="left")
        self.inventory_state_var = tk.StringVar(value="ALL")
        state_options = ["ALL"] + VALID_STATES
        state_combo = ttk.Combobox(controls, textvariable=self.inventory_state_var, values=state_options, state="readonly", width=18)
        state_combo.pack(side="left", padx=(8, 14))
        tk.Button(controls, text="Apply filters", command=self.refresh_inventory_table, bg="#dbeafe").pack(side="left", padx=4)

        search_frame = tk.Frame(controls)
        search_frame.pack(side="right")
        tk.Label(search_frame, text="Search by code:", font=("Arial", 10, "bold")).pack(side="left")
        self.search_code_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_code_var, width=16).pack(side="left", padx=(4, 6))
        tk.Button(search_frame, text="Find", command=self.search_equipment, bg="#fef3c7").pack(side="left")

        add_frame = tk.Frame(page, padx=14, pady=8)
        add_frame.pack(fill="x")
        tk.Label(add_frame, text="Add equipment", font=("Arial", 10, "bold")).pack(anchor="w")

        self.new_code_var = tk.StringVar()
        self.new_type_var = tk.StringVar(value="PORTABLE")
        self.new_state_var = tk.StringVar(value="IN_CART")
        self.new_loans_var = tk.StringVar(value="0")

        for label, variable, widget in [
            ("Code", self.new_code_var, tk.Entry(add_frame, width=12)),
            ("Type", self.new_type_var, ttk.Combobox(add_frame, textvariable=self.new_type_var, values=VALID_TYPES, state="readonly", width=14)),
            ("State", self.new_state_var, ttk.Combobox(add_frame, textvariable=self.new_state_var, values=VALID_STATES, state="readonly", width=16)),
            ("Loans", self.new_loans_var, tk.Entry(add_frame, width=8)),
        ]:
            tk.Label(add_frame, text=label).pack(side="left", padx=(6, 2))
            widget.pack(side="left", padx=(0, 10))

        tk.Button(add_frame, text="Add", command=self.add_equipment_ui, bg="#bbf7d0").pack(side="left", padx=10)
        tk.Button(add_frame, text="Remove by code", command=self.remove_equipment_ui, bg="#fecaca").pack(side="left")

        self.inventory_result_var = tk.StringVar(value="")
        tk.Label(page, textvariable=self.inventory_result_var, fg="#1d4ed8", font=("Arial", 10, "bold"), anchor="w", justify="left").pack(anchor="w", padx=16)

        columns = ("code", "type", "state", "loans", "owner")
        self.inventory_table = ttk.Treeview(page, columns=columns, show="headings")
        for column, title in [("code", "Code"), ("type", "Type"), ("state", "State"), ("loans", "Loans"), ("owner", "Owner")]:
            self.inventory_table.heading(column, text=title)
            self.inventory_table.column(column, width=150, anchor="center")
        self.inventory_table.pack(fill="both", expand=True, padx=14, pady=(6, 12))

    def build_loan_page(self):
        page = tk.Frame(self.page_container)
        self.pages["loan"] = page

        request_frame = tk.LabelFrame(page, text="Request equipment", padx=12, pady=10)
        request_frame.pack(fill="x", padx=14, pady=(12, 8))

        self.request_student_var = tk.StringVar()
        self.request_type_var = tk.StringVar(value="PORTABLE")
        self.request_hour_var = tk.StringVar(value="120")

        for label, variable, widget in [
            ("Student", self.request_student_var, tk.Entry(request_frame, width=15)),
            ("Type", self.request_type_var, ttk.Combobox(request_frame, textvariable=self.request_type_var, values=VALID_TYPES, state="readonly", width=15)),
            ("Hour", self.request_hour_var, tk.Entry(request_frame, width=10)),
        ]:
            tk.Label(request_frame, text=label, font=("Arial", 10, "bold")).pack(side="left", padx=(0, 6))
            widget.pack(side="left", padx=(0, 12))

        tk.Button(request_frame, text="Request equipment", command=self.request_equipment_ui, bg="#bfdbfe").pack(side="left")

        return_frame = tk.LabelFrame(page, text="Return equipment", padx=12, pady=10)
        return_frame.pack(fill="x", padx=14, pady=(0, 12))

        self.return_code_var = tk.StringVar()
        self.return_hour_var = tk.StringVar(value="180")

        tk.Label(return_frame, text="Code", font=("Arial", 10, "bold")).pack(side="left")
        tk.Entry(return_frame, textvariable=self.return_code_var, width=12).pack(side="left", padx=(6, 12))
        tk.Label(return_frame, text="Hour", font=("Arial", 10, "bold")).pack(side="left")
        tk.Entry(return_frame, textvariable=self.return_hour_var, width=10).pack(side="left", padx=(6, 12))
        tk.Button(return_frame, text="Return equipment", command=self.return_equipment_ui, bg="#d1fae5").pack(side="left")

        self.loan_message_var = tk.StringVar(value="")
        tk.Label(page, textvariable=self.loan_message_var, fg="#b91c1c", font=("Arial", 10, "bold"), wraplength=900, justify="left").pack(anchor="w", padx=14)

        queue_frame = tk.Frame(page)
        queue_frame.pack(fill="both", expand=True, padx=14, pady=(10, 0))

        waiting_title = tk.Label(queue_frame, text="Waiting queues by type", font=("Arial", 10, "bold"))
        waiting_title.pack(anchor="w")

        self.waiting_labels = {}
        for item_type in VALID_TYPES:
            panel = tk.LabelFrame(queue_frame, text=item_type, padx=8, pady=8)
            panel.pack(fill="x", pady=4)
            label = tk.Label(panel, text="FRONT -> ... <- END", justify="left", wraplength=1100)
            label.pack(anchor="w")
            self.waiting_labels[item_type] = label

        review_panel = tk.LabelFrame(page, text="Review queue", padx=10, pady=8)
        review_panel.pack(fill="x", padx=14, pady=(10, 6))
        self.review_label = tk.Label(review_panel, text="Queue empty", justify="left", wraplength=1100)
        self.review_label.pack(anchor="w")

    def build_carts_page(self):
        page = tk.Frame(self.page_container)
        self.pages["carts"] = page

        self.cart_labels = {}
        for item_type in VALID_TYPES:
            panel = tk.LabelFrame(page, text=item_type, padx=10, pady=10)
            panel.pack(side="left", fill="y", expand=True, padx=12, pady=12)
            label = tk.Label(panel, text="Top ->\n", justify="left", anchor="n", wraplength=180)
            label.pack(fill="both", expand=True)
            self.cart_labels[item_type] = label

        directed_panel = tk.LabelFrame(page, text="Directed loan auxiliary cart", padx=10, pady=8)
        directed_panel.pack(fill="x", side="bottom", padx=12, pady=10)

        self.directed_entry = tk.Entry(directed_panel, width=20)
        self.directed_entry.pack(side="left", padx=(4, 8))
        tk.Button(directed_panel, text="Run directed loan", command=self.direct_loan_ui, bg="#fef3c7").pack(side="left")
        self.directed_result_var = tk.StringVar(value="")
        tk.Label(directed_panel, textvariable=self.directed_result_var, font=("Arial", 10, "bold"), justify="left", wraplength=900).pack(side="left", padx=(12, 0))

    def build_review_page(self):
        page = tk.Frame(self.page_container)
        self.pages["review"] = page

        review_section = tk.LabelFrame(page, text="Review queue", padx=12, pady=10)
        review_section.pack(fill="x", padx=14, pady=(12, 6))
        self.review_queue_display = tk.Label(review_section, text="Empty", justify="left", wraplength=1100)
        self.review_queue_display.pack(anchor="w")

        actions = tk.Frame(page)
        actions.pack(fill="x", padx=14, pady=8)
        tk.Button(actions, text="Approve first item", command=self.approve_review_ui, bg="#bbf7d0").pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Mark damaged", command=self.damage_review_ui, bg="#fecaca").pack(side="left")
        tk.Button(actions, text="Serve waiting list", command=self.serve_waiting_ui, bg="#dbeafe").pack(side="left", padx=(8, 0))

        storage_section = tk.LabelFrame(page, text="Equipment to be stored", padx=12, pady=10)
        storage_section.pack(fill="x", padx=14, pady=(0, 8))
        self.storage_queue_display = tk.Label(storage_section, text="Empty", justify="left", wraplength=1100)
        self.storage_queue_display.pack(anchor="w")

        metrics_frame = tk.LabelFrame(page, text="Metrics", padx=12, pady=10)
        metrics_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.metrics_display = tk.Label(metrics_frame, text="", justify="left", anchor="nw", wraplength=1100, font=("Arial", 10))
        self.metrics_display.pack(fill="both", expand=True)

        log_section = tk.LabelFrame(page, text="Operations log", padx=12, pady=10)
        log_section.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.log_display = tk.Label(log_section, text="", justify="left", anchor="nw", wraplength=1100, font=("Arial", 9), fg="#1f2937")
        self.log_display.pack(fill="both", expand=True)

    def load_sample_data(self):
        self.system.load_sample_data()
        self.refresh_all()

    def refresh_inventory_table(self):
        item_type_filter = self.inventory_type_var.get()
        state_filter = self.inventory_state_var.get()
        items = self.system.inventory_snapshot(
            item_type=None if item_type_filter == "ALL" else item_type_filter,
            state=None if state_filter == "ALL" else state_filter,
        )

        for row in self.inventory_table.get_children():
            self.inventory_table.delete(row)
        for item in items:
            self.inventory_table.insert("", "end", values=(item["code"], item["type"], item["state"], item["loans"], item["owner"] or "-"))

    def search_equipment(self):
        code = self.search_code_var.get().strip()
        try:
            result = self.system.buscar(code)
            self.inventory_result_var.set(f"Code: {result['code']} | Type: {result['type']} | State: {result['state']} | Position from top: {result['position_from_top'] if result['position_from_top'] is not None else 'Not in cart'}")
        except ValueError as exc:
            self.inventory_result_var.set(str(exc))

    def add_equipment_ui(self):
        code = self.new_code_var.get().strip()
        item_type = self.new_type_var.get()
        state = self.new_state_var.get()
        loans_value = self.new_loans_var.get().strip()
        try:
            loans = int(loans_value)
            self.system.add_equipment(code, item_type, state=state, loans=loans)
            self.refresh_all()
            self.new_code_var.set("")
            self.new_loans_var.set("0")
        except ValueError as exc:
            self.inventory_result_var.set(str(exc))

    def remove_equipment_ui(self):
        code = self.new_code_var.get().strip()
        try:
            self.system.remove_equipment(code)
            self.refresh_all()
        except ValueError as exc:
            self.inventory_result_var.set(str(exc))

    def request_equipment_ui(self):
        student = self.request_student_var.get().strip()
        item_type = self.request_type_var.get()
        hour = self.request_hour_var.get().strip()
        try:
            result = self.system.solicitar(student, item_type, int(hour))
            self.loan_message_var.set(f"Result: {result}")
            self.refresh_all()
        except ValueError as exc:
            self.loan_message_var.set(str(exc))

    def return_equipment_ui(self):
        code = self.return_code_var.get().strip()
        hour = self.return_hour_var.get().strip()
        try:
            duration = self.system.devolver(code, int(hour))
            self.loan_message_var.set(f"Return processed. Duration: {duration} hours.")
            self.refresh_all()
        except ValueError as exc:
            self.loan_message_var.set(str(exc))

    def direct_loan_ui(self):
        code = self.directed_entry.get().strip()
        try:
            result = self.system.prestar_dirigido(code)
            self.directed_result_var.set(f"Directed loan complete. Movements: {result['movements']}. Trace: {' | '.join(result['trace'])}")
            self.refresh_all()
        except ValueError as exc:
            self.directed_result_var.set(str(exc))

    def approve_review_ui(self):
        try:
            result = self.system.revisar("APPROVE")
            self.loan_message_var.set(f"Review approved: {result}")
            self.refresh_all()
        except ValueError as exc:
            self.loan_message_var.set(str(exc))

    def damage_review_ui(self):
        try:
            result = self.system.revisar("DAMAGED")
            self.loan_message_var.set(f"Review damaged: {result}")
            self.refresh_all()
        except ValueError as exc:
            self.loan_message_var.set(str(exc))

    def serve_waiting_ui(self):
        item_type = self.request_type_var.get()
        try:
            served = self.system.atender_espera(item_type)
            self.loan_message_var.set(f"Waiting queue served for {item_type}. Remaining waiting requests: {served}")
            self.refresh_all()
        except ValueError as exc:
            self.loan_message_var.set(str(exc))

    def refresh_waiting_queue_display(self):
        for item_type in VALID_TYPES:
            queue = self.system.waiting_snapshot(item_type)
            if queue:
                first = queue[0]
                values = [request.get("student") for request in queue]
                self.waiting_labels[item_type].config(text=f"FRONT -> {values} <- END | Total: {len(values)}")
            else:
                self.waiting_labels[item_type].config(text="FRONT -> empty <- END | Total: 0")

    def refresh_review_displays(self):
        review_list = self.system.review_snapshot()
        self.review_queue_display.config(text=f"FRONT -> {[item.code for item in review_list]} <- END | Total: {len(review_list)}" if review_list else "FRONT -> empty <- END | Total: 0")

        storage = self.system.storage_snapshot()
        self.storage_queue_display.config(text=f"FRONT -> {[item.code for item in storage]} <- END | Total: {len(storage)}" if storage else "FRONT -> empty <- END | Total: 0")

    def refresh_cart_display(self):
        for item_type in VALID_TYPES:
            cart_items = self.system.cart_snapshot(item_type)
            if cart_items:
                order = "\n".join([f"{index + 1}. {item['code']}" for index, item in enumerate(reversed(cart_items))])
                text = f"TOP\n{order}\nTotal: {len(cart_items)}/{self.system.capacity}"
            else:
                text = f"TOP\n(empty)\nTotal: 0/{self.system.capacity}"
            self.cart_labels[item_type].config(text=text)

    def refresh_metrics(self):
        report = self.system.generate_report()
        metric_lines = [
            f"Equipment by state: {report['equipment_by_state']}",
            f"Equipment by type: {report['equipment_by_type']}",
            f"Cart occupation: {report['cart_usage']}",
            f"Requests: immediate={report['requests']['immediate']}, queued={report['requests']['queued']}, average waiting={report['requests']['average_wait_minutes']} min",
            f"Directed loans: {report['directed_loans']}; total movements: {report['directed_moves_total']}",
            f"Damaged returns: {report['damaged_returns']}; maintenance items: {report['maintenance_items']}; overdue students: {report['overdue_students']}",
            f"Most borrowed: {report['most_borrowed']}; preventive maintenance: {report['preventive_maintenance']}",
        ]
        self.metrics_display.config(text="\n".join(metric_lines))

    def refresh_logs(self):
        self.log_display.config(text=self.system.get_log_text())

    def refresh_all(self):
        self.refresh_inventory_table()
        self.refresh_waiting_queue_display()
        self.refresh_review_displays()
        self.refresh_cart_display()
        self.refresh_metrics()
        self.refresh_logs()


if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityOneApp(root)
    root.mainloop()
    