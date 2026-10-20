"""
System Architecture & Engineering Specifications.
Provides detailed explanations of Queue, Priority Queue (Binary Heap), Singly Linked List,
time and space complexities, architectural justification, and live interactive runtime state inspection.
"""

import customtkinter as ctk
from typing import Callable
from ui.theme import Theme
from ui.components import CardFrame
from services.hospital_service import HospitalService


class AboutPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            header,
            text="Hospital Emergency Management System Architecture",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Technical architecture, data structures, and algorithmic specifications",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # 1. System Overview & Problem Statement Card
        card_overview = CardFrame(self)
        card_overview.pack(fill="x", pady=(0, 16))
        c_in1 = ctk.CTkFrame(card_overview, fg_color="transparent")
        c_in1.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            c_in1,
            text="1. System Purpose & Triage Architecture",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        ).pack(anchor="w")

        body1 = (
            "Hospital Emergency Departments require rapid, life-critical triage where treatment scheduling "
            "cannot follow a simple First-Come, First-Served order. Delaying treatment for a patient with cardiac "
            "arrest or acute stroke to treat a mild ankle sprain would lead to preventable mortality.\n\n"
            "This system solves this challenge by integrating three foundational data structures:\n"
            "• Priority Queue (Binary Min-Heap): Guarantees that highest urgency patients (Critical P1) are dispatched "
            "immediately ahead of High Priority (P2) and Normal (P3) patients in O(log n) time.\n"
            "• FIFO Arrival Tie-Breaking: Within the same priority level, strict arrival order is maintained, preventing "
            "arbitrary queue jumping.\n"
            "• Singly Linked List: Master in-memory dynamic record repository that dynamically allocates memory as patients arrive "
            "and maintains full patient history across the treatment lifecycle."
        )
        ctk.CTkLabel(
            c_in1,
            text=body1,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MAIN,
            wraplength=840,
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

        # 2. Live Runtime DSA State Inspector
        card_dsa = CardFrame(self)
        card_dsa.pack(fill="x", pady=(0, 16))
        c_in_dsa = ctk.CTkFrame(card_dsa, fg_color="transparent")
        c_in_dsa.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            c_in_dsa,
            text="2. Live Data Structure Memory & Pointer Inspector",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEAL_ACCENT
        ).pack(anchor="w")

        ctk.CTkLabel(
            c_in_dsa,
            text="Click 'Refresh Memory View' to inspect the actual runtime memory structures of the Linked List and Heap:",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(4, 10))

        # Box for Linked List visualization
        box_ll = ctk.CTkFrame(c_in_dsa, fg_color=Theme.BG_CARD_SECONDARY, corner_radius=8)
        box_ll.pack(fill="x", pady=(0, 10))
        b_in_ll = ctk.CTkFrame(box_ll, fg_color="transparent")
        b_in_ll.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(b_in_ll, text="🔗 In-Memory Singly Linked List Node Pointer Chain:", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        self.dsa_ll_text = ctk.CTkLabel(
            b_in_ll,
            text=self.service.master_list.to_pointer_visualization(max_nodes=6),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=11),
            text_color=Theme.PRIMARY_BLUE,
            wraplength=800,
            justify="left"
        )
        self.dsa_ll_text.pack(anchor="w", pady=(4, 0))

        # Box for Binary Min-Heap visualization
        box_hp = ctk.CTkFrame(c_in_dsa, fg_color=Theme.BG_CARD_SECONDARY, corner_radius=8)
        box_hp.pack(fill="x", pady=(0, 12))
        b_in_hp = ctk.CTkFrame(box_hp, fg_color="transparent")
        b_in_hp.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(b_in_hp, text="🌲 Internal Binary Min-Heap Array Representation:", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        self.dsa_hp_text = ctk.CTkLabel(
            b_in_hp,
            text=self.service.waiting_queue.to_heap_array_visualization(),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=11),
            text_color="#0D9488",
            wraplength=800,
            justify="left"
        )
        self.dsa_hp_text.pack(anchor="w", pady=(4, 0))

        btn_refresh_dsa = ctk.CTkButton(
            c_in_dsa,
            text="🔄 Refresh Runtime State",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.TEAL_ACCENT,
            hover_color=Theme.TEAL_HOVER,
            command=self._refresh_dsa_view,
            height=32,
            width=200
        )
        btn_refresh_dsa.pack(anchor="w")

        # 3. Time & Space Complexity Table Card
        card_complexity = CardFrame(self)
        card_complexity.pack(fill="x", pady=(0, 16))
        c_in2 = ctk.CTkFrame(card_complexity, fg_color="transparent")
        c_in2.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            c_in2,
            text="3. Computational Time & Space Complexity Analysis",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        ).pack(anchor="w", pady=(0, 10))

        # Complexity Table
        table_box = ctk.CTkFrame(c_in2, fg_color=Theme.BG_CARD_SECONDARY, corner_radius=8)
        table_box.pack(fill="x")

        rows = [
            ("Data Structure", "Operation", "Time Complexity", "Space Complexity", "Algorithmic Rationale"),
            ("Priority Queue (Heap)", "Enqueue / Insert", "O(log n)", "O(n)", "Inserts at leaf and sifts up along tree height"),
            ("Priority Queue (Heap)", "Pop Highest Priority", "O(log n)", "O(1) extra", "Replaces root with last leaf and sifts down"),
            ("Priority Queue (Heap)", "Peek Next Patient", "O(1)", "O(1)", "Direct index 0 array access of heap root"),
            ("Priority Queue (Heap)", "Remove by ID", "O(n) + O(log n)", "O(1)", "Linear scan to locate node + heap restoration"),
            ("Singly Linked List", "Insert (Append / Tail)", "O(1)", "O(1) per node", "Constant time pointer assignment via tail pointer"),
            ("Singly Linked List", "Insert at Head", "O(1)", "O(1)", "Prepend node and reassign head pointer"),
            ("Singly Linked List", "Search by ID", "O(n)", "O(1)", "Linear pointer traversal from head to target"),
            ("Singly Linked List", "Update Record", "O(n)", "O(1)", "O(n) traversal to find node + O(1) attribute update"),
            ("Singly Linked List", "Delete Node by ID", "O(n)", "O(1)", "Traversal to node and previous node pointer relink"),
            ("FIFO Queue (Nodes)", "Enqueue & Dequeue", "O(1)", "O(1) per node", "Queue pointers maintained at front and rear")
        ]

        for idx, (ds, op, tc, sc, rat) in enumerate(rows):
            is_hdr = (idx == 0)
            r_frame = ctk.CTkFrame(
                table_box,
                fg_color="#E2E8F0" if is_hdr else (Theme.BG_CARD if idx % 2 == 1 else Theme.BG_CARD_SECONDARY),
                height=32
            )
            r_frame.pack(fill="x", pady=1 if not is_hdr else 0)

            font_t = ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold" if is_hdr else "normal")
            text_col = Theme.TEXT_MAIN if is_hdr else Theme.TEXT_MAIN

            ctk.CTkLabel(r_frame, text=ds, width=150, font=font_t, text_color=text_col, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(r_frame, text=op, width=150, font=font_t, text_color=text_col, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(r_frame, text=tc, width=120, font=font_t, text_color=Theme.PRIMARY_BLUE if not is_hdr else text_col, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(r_frame, text=sc, width=100, font=font_t, text_color=text_col, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(r_frame, text=rat, width=280, font=font_t, text_color=Theme.TEXT_MUTED if not is_hdr else text_col, anchor="w").pack(side="left", padx=8)

        # 4. Technical Architecture FAQ
        card_viva = CardFrame(self)
        card_viva.pack(fill="x", pady=(16, 20))
        c_in3 = ctk.CTkFrame(card_viva, fg_color="transparent")
        c_in3.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            c_in3,
            text="4. Architecture & Engineering FAQ",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        ).pack(anchor="w", pady=(0, 10))

        qa_items = [
            (
                "Why use a Singly Linked List for Patient Records instead of an array?",
                "In emergency hospital admissions, total patient volume is dynamic and unpredictable. A Linked List allocates memory dynamically per node without requiring contiguous memory blocks or costly array resizing/copying. Furthermore, inserting or deleting records involves clean pointer updates rather than shifting memory elements."
            ),
            (
                "How does the system guarantee that patients with the same priority are treated in FIFO order?",
                "We use a composite comparison key in our Binary Min-Heap: (priority_level, arrival_sequence). Priority level is the primary key (1 < 2 < 3). If two patients have equal priority, the heap compares arrival_sequence (e.g., 2 < 4). Since arrival sequence strictly increments upon registration, earlier arrivals always possess smaller secondary keys and are dequeued first."
            ),
            (
                "Why not use a standard list sorted on each insertion?",
                "Sorting a list on each insertion requires O(n log n) or O(n) with insertion sort. Our custom Binary Min-Heap Priority Queue executes insertion in O(log n) time and highest-priority extraction in O(log n) time, which is substantially more efficient during emergency surges."
            ),
            (
                "When a treatment finishes, why is the patient kept in the linked list?",
                "Clinical ethics and medical governance require permanent record preservation. When treatment finishes, the patient is removed from the active waiting heap queue, but their node remains securely preserved in the Singly Linked List with updated status='Completed' and recorded duration."
            )
        ]

        for q, a in qa_items:
            q_box = ctk.CTkFrame(c_in3, fg_color=Theme.BG_CARD_SECONDARY, corner_radius=6)
            q_box.pack(fill="x", pady=6)
            q_inner = ctk.CTkFrame(q_box, fg_color="transparent")
            q_inner.pack(fill="x", padx=14, pady=10)

            ctk.CTkLabel(q_inner, text=f"• {q}", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN, wraplength=800, justify="left").pack(anchor="w")
            ctk.CTkLabel(q_inner, text=a, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11), text_color=Theme.TEXT_MUTED, wraplength=800, justify="left").pack(anchor="w", pady=(4, 0))

    def _refresh_dsa_view(self):
        self.dsa_ll_text.configure(text=self.service.master_list.to_pointer_visualization(max_nodes=6))
        self.dsa_hp_text.configure(text=self.service.waiting_queue.to_heap_array_visualization())
