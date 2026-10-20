"""
Treatment History Page for Hospital Emergency Management System.
Displays all completed clinical treatment records with duration metrics, search, and CSV export.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, List
from ui.theme import Theme
from ui.components import CardFrame, PriorityBadge, EmptyState, PatientDetailsModal
from models.patient import Patient, PriorityLevel
from services.hospital_service import HospitalService


class TreatmentHistoryPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.filter_priority: Optional[int] = None
        self.search_query = ""

        self.build_ui()
        self.refresh_history()

    def build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(
            title_box,
            text="Completed Treatment History & Clinical Archives",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            title_box,
            text="Permanent treatment history preserved in Master Linked List with completion timestamps and clinical durations",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # Export CSV Button
        btn_export = ctk.CTkButton(
            header,
            text="📥 Export to CSV",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.TEAL_ACCENT,
            hover_color=Theme.TEAL_HOVER,
            command=self._handle_export_csv,
            height=34,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_export.pack(side="right")

        # 2. Controls & Search Bar
        ctrl_card = CardFrame(self)
        ctrl_card.pack(fill="x", pady=(0, 14))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        self.search_entry = ctk.CTkEntry(
            ctrl_inner,
            placeholder_text="🔍 Search history by Patient ID, Name, or Attending Doctor...",
            width=320,
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        filter_box = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        filter_box.pack(side="right")

        self.btn_f_all = ctk.CTkButton(filter_box, text="All", width=55, height=32, corner_radius=6, command=lambda: self._set_priority_filter(None))
        self.btn_f_all.pack(side="left", padx=2)

        self.btn_f_crit = ctk.CTkButton(filter_box, text="🚨 Critical", width=85, height=32, corner_radius=6, command=lambda: self._set_priority_filter(PriorityLevel.CRITICAL))
        self.btn_f_crit.pack(side="left", padx=2)

        self.btn_f_high = ctk.CTkButton(filter_box, text="⚠️ High", width=75, height=32, corner_radius=6, command=lambda: self._set_priority_filter(PriorityLevel.HIGH))
        self.btn_f_high.pack(side="left", padx=2)

        self.btn_f_norm = ctk.CTkButton(filter_box, text="🟢 Normal", width=80, height=32, corner_radius=6, command=lambda: self._set_priority_filter(PriorityLevel.NORMAL))
        self.btn_f_norm.pack(side="left", padx=2)

        self._update_filter_buttons()

        # 3. Table Card
        self.table_card = CardFrame(self)
        self.table_card.pack(fill="both", expand=True, pady=(0, 20))

        th = ctk.CTkFrame(self.table_card, fg_color=Theme.BG_CARD_SECONDARY, height=38, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(16, 6))

        ctk.CTkLabel(th, text="PATIENT ID", width=95, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PATIENT NAME", width=150, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PRIORITY", width=135, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="ATTENDING DOCTOR", width=160, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="TREATMENT START / END", width=180, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="DURATION", width=80, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="ACTIONS", width=80, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=12)

        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _set_priority_filter(self, priority: Optional[int]):
        self.filter_priority = priority
        self._update_filter_buttons()
        self.refresh_history()

    def _update_filter_buttons(self):
        btns = [
            (None, self.btn_f_all),
            (PriorityLevel.CRITICAL, self.btn_f_crit),
            (PriorityLevel.HIGH, self.btn_f_high),
            (PriorityLevel.NORMAL, self.btn_f_norm)
        ]
        for val, btn in btns:
            if val == self.filter_priority:
                btn.configure(fg_color=Theme.PRIMARY_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN)

    def _on_search_change(self):
        self.search_query = self.search_entry.get().strip().lower()
        self.refresh_history()

    def refresh_history(self):
        for w in self.rows_container.winfo_children():
            w.destroy()

        history = self.service.get_treatment_history()

        filtered: List[Patient] = []
        for p in history:
            if self.filter_priority is not None and p.priority != self.filter_priority:
                continue
            if self.search_query:
                match = (
                    self.search_query in p.patient_id.lower() or
                    self.search_query in p.name.lower() or
                    self.search_query in (p.attending_doctor or "").lower() or
                    self.search_query in (p.treatment_notes or "").lower()
                )
                if not match:
                    continue
            filtered.append(p)

        if not filtered:
            EmptyState(
                self.rows_container,
                title="No Treatment History Found",
                message="No patients have completed emergency treatment matching current filters.",
                icon_symbol="📋"
            ).pack(fill="both", expand=True, pady=30)
            return

        for idx, p in enumerate(filtered):
            row = ctk.CTkFrame(
                self.rows_container,
                fg_color=Theme.BG_CARD if idx % 2 == 0 else Theme.BG_CARD_SECONDARY,
                height=48,
                corner_radius=6
            )
            row.pack(fill="x", pady=2)

            # ID
            ctk.CTkLabel(
                row,
                text=p.patient_id,
                width=95,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=12, weight="bold"),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Name
            ctk.CTkLabel(
                row,
                text=p.name,
                width=150,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Priority Badge
            b_box = ctk.CTkFrame(row, fg_color="transparent", width=135)
            b_box.pack(side="left", padx=4)
            badge = PriorityBadge(b_box, priority=p.priority)
            badge.pack(anchor="w")

            # Doctor
            ctk.CTkLabel(
                row,
                text=p.attending_doctor or "Dr. S. Nair",
                width=160,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Time Range
            start = p.treatment_start_time.split(" ")[-2:] if p.treatment_start_time else ["--"]
            end = p.treatment_completion_time.split(" ")[-2:] if p.treatment_completion_time else ["--"]
            time_str = f"{' '.join(start)} → {' '.join(end)}"

            ctk.CTkLabel(
                row,
                text=time_str,
                width=180,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).pack(side="left", padx=4)

            # Duration
            dur_mins = p.treatment_duration_minutes or 20
            ctk.CTkLabel(
                row,
                text=f"{dur_mins} mins",
                width=80,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                text_color="#059669",
                anchor="w"
            ).pack(side="left", padx=4)

            # Action
            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.pack(side="right", padx=10)

            ctk.CTkButton(
                act_box,
                text="Details",
                width=65,
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color=Theme.BG_CARD_SECONDARY,
                text_color=Theme.TEXT_MAIN,
                hover_color=Theme.BORDER_MEDIUM,
                command=lambda pt=p: PatientDetailsModal(self, pt)
            ).pack(side="left")

    def _handle_export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")],
            initialfile="hospital_emergency_treatment_history.csv",
            title="Export Emergency Treatment History"
        )
        if filename:
            ok, msg = self.service.export_treatment_history_csv(filename)
            if ok:
                messagebox.showinfo("Export Successful", f"Saved {msg}")
            else:
                messagebox.showerror("Export Failed", msg)
