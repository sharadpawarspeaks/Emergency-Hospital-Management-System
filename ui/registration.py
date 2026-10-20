"""
Patient Registration Page for Hospital Emergency Management System.
Includes clinical triage priority selector, comprehensive input validation, and direct queue dispatch.
"""

from datetime import datetime
import customtkinter as ctk
from typing import Callable, Optional
from ui.theme import Theme
from ui.components import CardFrame, AlertBanner
from models.patient import PriorityLevel
from services.hospital_service import HospitalService


class RegistrationPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.priority_var = ctk.IntVar(value=PriorityLevel.NORMAL)
        self.gender_var = ctk.StringVar(value="Male")

        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            header,
            text="Emergency Patient Registration & Triage Intake",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Register incoming emergency patient, assign clinical triage priority, and insert into priority queue & linked list",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # Feedback notification banner container (only packed when an alert is active)
        self.banner_container = ctk.CTkFrame(self, fg_color="transparent")

        # Main Form Card
        self.form_card = CardFrame(self)
        self.form_card.pack(fill="x", pady=(0, 20))

        form_inner = ctk.CTkFrame(self.form_card, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=24, pady=24)



        # Row 1: Name & Age & Gender
        row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 14))
        row1.grid_columnconfigure(0, weight=5)
        row1.grid_columnconfigure(1, weight=2)
        row1.grid_columnconfigure(2, weight=3)

        # Name
        box_name = ctk.CTkFrame(row1, fg_color="transparent")
        box_name.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(box_name, text="Patient Full Name *", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.entry_name = ctk.CTkEntry(box_name, placeholder_text="e.g. Eleanor Rigby", height=38, corner_radius=Theme.RADIUS_BUTTON)
        self.entry_name.pack(fill="x")

        # Age
        box_age = ctk.CTkFrame(row1, fg_color="transparent")
        box_age.grid(row=0, column=1, padx=5, sticky="nsew")
        ctk.CTkLabel(box_age, text="Age (Years) *", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.entry_age = ctk.CTkEntry(box_age, placeholder_text="e.g. 45", height=38, corner_radius=Theme.RADIUS_BUTTON)
        self.entry_age.pack(fill="x")

        # Gender
        box_gender = ctk.CTkFrame(row1, fg_color="transparent")
        box_gender.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(box_gender, text="Gender *", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.gender_menu = ctk.CTkOptionMenu(
            box_gender,
            variable=self.gender_var,
            values=["Male", "Female", "Other"],
            height=38,
            corner_radius=Theme.RADIUS_BUTTON,
            fg_color=Theme.BG_CARD_SECONDARY,
            text_color=Theme.TEXT_MAIN,
            button_color=Theme.BORDER_MEDIUM,
            button_hover_color=Theme.PRIMARY_BLUE
        )
        self.gender_menu.pack(fill="x")

        # Row 2: Contact & Arrival Timestamp
        row2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 14))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        # Contact Phone
        box_contact = ctk.CTkFrame(row2, fg_color="transparent")
        box_contact.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(box_contact, text="Contact Phone (Optional)", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.entry_contact = ctk.CTkEntry(box_contact, placeholder_text="e.g. 987-654-3210", height=38, corner_radius=Theme.RADIUS_BUTTON)
        self.entry_contact.pack(fill="x")

        # Arrival Time (Auto)
        box_arrival = ctk.CTkFrame(row2, fg_color="transparent")
        box_arrival.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(box_arrival, text="Arrival Timestamp (Auto-Recorded)", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.entry_arrival = ctk.CTkEntry(box_arrival, height=38, corner_radius=Theme.RADIUS_BUTTON, fg_color=Theme.BG_CARD_SECONDARY)
        self.entry_arrival.insert(0, datetime.now().strftime("%Y-%m-%d %I:%M %p"))
        self.entry_arrival.configure(state="disabled")
        self.entry_arrival.pack(fill="x")

        # Row 3: Symptoms / Medical Notes
        row3 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            row3,
            text="Primary Symptoms & Reason for Emergency Visit *",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", pady=(0, 4))

        self.entry_symptoms = ctk.CTkTextbox(
            row3,
            height=70,
            corner_radius=Theme.RADIUS_BUTTON,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12)
        )
        self.entry_symptoms.pack(fill="x")

        # Row 4: Clinical Triage Priority Selector (3 Radio Cards)
        ctk.CTkLabel(
            form_inner,
            text="Emergency Triage Priority Level * (Determines Binary Heap Queue Placement)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", pady=(6, 8))

        self.prio_cards_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        self.prio_cards_frame.pack(fill="x", pady=(0, 20))
        self.prio_cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="prio_cols")

        self.prio_buttons = {}
        self._build_priority_cards()

        # Action Buttons
        btn_bar = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(10, 0))

        self.btn_submit = ctk.CTkButton(
            btn_bar,
            text="✓ Register Patient & Add to Queue",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._handle_submit,
            height=44,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.btn_submit.pack(side="left", padx=(0, 10))

        btn_clear = ctk.CTkButton(
            btn_bar,
            text="Reset Form",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13),
            fg_color=Theme.BG_CARD_SECONDARY,
            text_color=Theme.TEXT_MAIN,
            hover_color=Theme.BORDER_MEDIUM,
            command=self._handle_clear,
            height=44,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_clear.pack(side="left")

    def _build_priority_cards(self):
        """Constructs three clickable visual triage severity cards."""
        priorities = [
            (
                PriorityLevel.CRITICAL,
                "🚨 Critical Emergency",
                "Priority 1 (Highest Urgency)",
                "Immediate life threat (e.g. cardiac arrest, severe trauma, respiratory failure)",
                Theme.COLOR_CRITICAL,
                Theme.BG_CRITICAL_BADGE
            ),
            (
                PriorityLevel.HIGH,
                "⚠️ High Priority",
                "Priority 2 (Urgent Care)",
                "Severe injury, severe pain, fractures, deep lacerations needing urgent treatment",
                Theme.COLOR_HIGH,
                Theme.BG_HIGH_BADGE
            ),
            (
                PriorityLevel.NORMAL,
                "🟢 Normal Priority",
                "Priority 3 (Standard Triage)",
                "Non-urgent stable symptoms (e.g. mild fever, sprain, minor cut, routine check)",
                Theme.COLOR_NORMAL,
                Theme.BG_NORMAL_BADGE
            )
        ]

        for idx, (p_val, title, subtitle, desc, border_color, bg_tint) in enumerate(priorities):
            card = ctk.CTkFrame(
                self.prio_cards_frame,
                corner_radius=Theme.RADIUS_CARD,
                fg_color=Theme.BG_CARD,
                border_width=2,
                border_color=Theme.BORDER_LIGHT
            )
            card.grid(row=0, column=idx, padx=6 if idx == 1 else (0 if idx == 0 else (6, 0)), sticky="nsew")

            # Clickable behavior
            def select_p(val=p_val):
                self.priority_var.set(val)
                self._update_priority_selection_ui()

            # Radio / Indicator
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 4))

            rbtn = ctk.CTkRadioButton(
                top,
                text=title,
                value=p_val,
                variable=self.priority_var,
                command=self._update_priority_selection_ui,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
                text_color=Theme.TEXT_MAIN,
                fg_color=border_color
            )
            rbtn.pack(anchor="w")

            sub_lbl = ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                text_color=border_color
            )
            sub_lbl.pack(anchor="w", padx=12, pady=(0, 4))

            desc_lbl = ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MUTED,
                wraplength=210,
                justify="left"
            )
            desc_lbl.pack(anchor="w", padx=12, pady=(0, 14))

            self.prio_buttons[p_val] = {
                "card": card,
                "border": border_color,
                "bg_tint": bg_tint
            }

        self._update_priority_selection_ui()

    def _update_priority_selection_ui(self):
        curr = self.priority_var.get()
        for p_val, data in self.prio_buttons.items():
            if p_val == curr:
                data["card"].configure(
                    border_color=data["border"],
                    border_width=2,
                    fg_color=data["bg_tint"]
                )
            else:
                data["card"].configure(
                    border_color=Theme.BORDER_LIGHT,
                    border_width=1,
                    fg_color=Theme.BG_CARD
                )

    def _show_banner(self, message: str, alert_type: str, registered_patient=None):
        for w in self.banner_container.winfo_children():
            w.destroy()

        self.banner_container.pack(fill="x", pady=(0, 10), before=self.form_card)

        banner_box = AlertBanner(self.banner_container, message=message, alert_type=alert_type)
        banner_box.pack(fill="x")

        if registered_patient:
            btn_box = ctk.CTkFrame(banner_box, fg_color="transparent")
            btn_box.pack(side="right", padx=10)

            btn_q = ctk.CTkButton(
                btn_box,
                text="View in Queue →",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                height=26,
                fg_color=Theme.PRIMARY_BLUE,
                hover_color=Theme.PRIMARY_HOVER,
                command=lambda: self.on_navigate("queue")
            )
            btn_q.pack(side="left", padx=4)

    def _handle_submit(self):
        name = self.entry_name.get()
        age_str = self.entry_age.get()
        gender = self.gender_var.get()
        contact = self.entry_contact.get()
        symptoms = self.entry_symptoms.get("1.0", "end-1c")
        priority = self.priority_var.get()

        ok, msg, patient = self.service.register_patient(
            name=name,
            age_str=age_str,
            gender=gender,
            contact=contact,
            symptoms=symptoms,
            priority=priority
        )

        if not ok:
            self._show_banner(msg, "error")
        else:
            self._show_banner(
                f"Success! {patient.name} registered as {patient.patient_id} ({patient.priority_label}). Added to Queue Position #{self._get_queue_pos(patient.patient_id)}.",
                "success",
                registered_patient=patient
            )
            # Clear input fields for next entry
            self._handle_clear(keep_banner=True)

    def _get_queue_pos(self, patient_id: str) -> int:
        ordered = self.service.get_waiting_queue_ordered()
        for idx, p in enumerate(ordered):
            if p.patient_id == patient_id:
                return idx + 1
        return 1

    def _handle_clear(self, keep_banner: bool = False):
        if not keep_banner:
            for w in self.banner_container.winfo_children():
                w.destroy()
            self.banner_container.pack_forget()
        self.entry_name.delete(0, "end")
        self.entry_age.delete(0, "end")
        self.entry_contact.delete(0, "end")
        self.entry_symptoms.delete("1.0", "end")
        self.priority_var.set(PriorityLevel.NORMAL)
        self._update_priority_selection_ui()
