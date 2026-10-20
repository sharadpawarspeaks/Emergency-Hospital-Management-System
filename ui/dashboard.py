"""
Dashboard Page for Hospital Emergency Management System.
Features:
- 4 Key Metric Stat Cards
- Live 'Now Serving / Active Emergency Bay' Callout Card
- Priority Distribution Donut Chart (Matplotlib)
- Next Waiting Patients Queue Table
- Live Activity Feed
"""

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable, Optional
from ui.theme import Theme
from ui.components import CardFrame, StatCard, PriorityBadge, StatusBadge, EmptyState
from models.patient import Patient, PriorityLevel, PatientStatus
from services.hospital_service import HospitalService


class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.chart_canvas = None
        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        # 1. Page Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(
            title_box,
            text="Emergency Department Overview",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            title_box,
            text="Live patient triage status, prioritized waiting queue, and treatment bays",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")



        # 2. Metric Stat Cards Row (4 cards)
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 20))
        stats_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_group")

        self.card_total = StatCard(
            stats_row,
            title="Total Registered",
            value="0",
            accent_color=Theme.PRIMARY_BLUE,
            icon_text="👥",
            subtitle="Master Linked List records"
        )
        self.card_total.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.card_waiting = StatCard(
            stats_row,
            title="Waiting in Queue",
            value="0",
            accent_color=Theme.COLOR_HIGH,
            icon_text="⏳",
            subtitle="Binary Heap Queue"
        )
        self.card_waiting.grid(row=0, column=1, padx=5, sticky="nsew")

        self.card_critical = StatCard(
            stats_row,
            title="Critical Emergency",
            value="0",
            accent_color=Theme.COLOR_CRITICAL,
            icon_text="🚨",
            subtitle="Immediate Triage P1"
        )
        self.card_critical.grid(row=0, column=2, padx=5, sticky="nsew")

        self.card_completed = StatCard(
            stats_row,
            title="Completed Treatments",
            value="0",
            accent_color=Theme.COLOR_NORMAL,
            icon_text="✅",
            subtitle="Archived in History"
        )
        self.card_completed.grid(row=0, column=3, padx=(10, 0), sticky="nsew")

        # 3. NOW SERVING HERO CARD (Inspired by Drittech Queue & MediSys UI)
        self.hero_card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_HERO_CARD,
            border_width=1,
            border_color="#1E293B"
        )
        self.hero_card.pack(fill="x", pady=(0, 20))
        self._build_hero_card()

        # 4. Middle Section: Two Columns (Emergency Queue preview + Priority Chart)
        mid_grid = ctk.CTkFrame(self, fg_color="transparent")
        mid_grid.pack(fill="x", pady=(0, 20))
        mid_grid.grid_columnconfigure(0, weight=6, uniform="mid_cols")
        mid_grid.grid_columnconfigure(1, weight=4, uniform="mid_cols")

        # Left: Live Emergency Queue Card
        self.queue_card = CardFrame(mid_grid)
        self.queue_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self._build_queue_preview()

        # Right: Priority Distribution Donut Chart Card
        self.chart_card = CardFrame(mid_grid)
        self.chart_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self._build_chart_card()

        # 5. Bottom Section: Recent Activity Log Feed
        self.activity_card = CardFrame(self)
        self.activity_card.pack(fill="x", pady=(0, 20))
        self._build_activity_card()

    def _build_hero_card(self):
        """Constructs the prominent 'Now Serving / Active Treatment Bay' banner."""
        container = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        container.pack(fill="x", padx=24, pady=20)

        left_side = ctk.CTkFrame(container, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True)

        # Label: NOW SERVING AT BAY
        lbl_eyebrow = ctk.CTkLabel(
            left_side,
            text="🏥  NOW SERVING IN ACTIVE EMERGENCY BAY",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_eyebrow.pack(anchor="w")

        self.hero_patient_id = ctk.CTkLabel(
            left_side,
            text="BAY AVAILABLE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=36, weight="bold"),
            text_color="#FFFFFF"
        )
        self.hero_patient_id.pack(anchor="w", pady=(2, 2))

        self.hero_patient_desc = ctk.CTkLabel(
            left_side,
            text="No active patient currently in treatment. Triage bay is ready for next emergency admission.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13),
            text_color="#94A3B8"
        )
        self.hero_patient_desc.pack(anchor="w")

        # Right Action Buttons
        right_side = ctk.CTkFrame(container, fg_color="transparent")
        right_side.pack(side="right", padx=(20, 0))

        self.btn_hero_action = ctk.CTkButton(
            right_side,
            text="⚡ Start Next Patient",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._handle_hero_action,
            height=42,
            width=170,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.btn_hero_action.pack(pady=4)

        self.btn_hero_queue = ctk.CTkButton(
            right_side,
            text="View Full Queue →",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#E2E8F0",
            command=lambda: self.on_navigate("queue"),
            height=34,
            width=170,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.btn_hero_queue.pack(pady=4)

    def _build_queue_preview(self):
        header = ctk.CTkFrame(self.queue_card, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 10))

        lbl = ctk.CTkLabel(
            header,
            text="Emergency Queue (Next in Line)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        lbl.pack(side="left")

        link_btn = ctk.CTkButton(
            header,
            text="Manage Queue",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.BG_CARD_SECONDARY,
            command=lambda: self.on_navigate("queue"),
            width=100,
            height=26
        )
        link_btn.pack(side="right")

        # Table header
        th = ctk.CTkFrame(self.queue_card, fg_color=Theme.BG_CARD_SECONDARY, height=32, corner_radius=6)
        th.pack(fill="x", padx=18, pady=(0, 6))

        ctk.CTkLabel(th, text="POS", width=40, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(side="left", padx=5)
        ctk.CTkLabel(th, text="PATIENT ID", width=90, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(th, text="NAME", width=140, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(th, text="PRIORITY", width=130, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(th, text="WAIT TIME", width=80, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=10)

        # Rows container
        self.queue_rows_container = ctk.CTkFrame(self.queue_card, fg_color="transparent")
        self.queue_rows_container.pack(fill="x", padx=18, pady=(0, 16))

    def _build_chart_card(self):
        header = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 4))

        lbl = ctk.CTkLabel(
            header,
            text="Priority Distribution",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        lbl.pack(side="left")

        self.chart_container = ctk.CTkFrame(self.chart_card, fg_color="transparent", height=230)
        self.chart_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_activity_card(self):
        header = ctk.CTkFrame(self.activity_card, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 8))

        lbl = ctk.CTkLabel(
            header,
            text="Real-time Clinical Activity Log",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        lbl.pack(side="left")

        self.activity_rows_container = ctk.CTkFrame(self.activity_card, fg_color="transparent")
        self.activity_rows_container.pack(fill="x", padx=18, pady=(0, 16))

    def refresh_data(self):
        stats = self.service.get_dashboard_stats()

        # Update Stat Cards
        self.card_total.update_value(stats["total_patients"])
        self.card_waiting.update_value(stats["waiting_count"])
        self.card_critical.update_value(stats["critical_count"])
        self.card_completed.update_value(stats["completed_count"])

        # Update Hero Card (Active Treatment)
        active: Optional[Patient] = stats["active_patient"]
        if active:
            self.hero_patient_id.configure(
                text=f"{active.patient_id} : {active.name}",
                text_color="#F8FAFC"
            )
            self.hero_patient_desc.configure(
                text=f"Undergoing Treatment in {active.triage_room}  |  Attending: {active.attending_doctor}  |  Started: {active.treatment_start_time}",
                text_color="#E2E8F0"
            )
            self.btn_hero_action.configure(
                text="✓ Complete Treatment",
                fg_color="#059669",
                hover_color="#047857"
            )
        else:
            next_pt = self.service.get_next_patient_in_queue()
            if next_pt:
                self.hero_patient_id.configure(
                    text="BAY 1 READY - NEXT: " + next_pt.patient_id,
                    text_color="#38BDF8"
                )
                self.hero_patient_desc.configure(
                    text=f"Next eligible patient: {next_pt.name} ({next_pt.priority_label})  |  Waiting: {next_pt.waiting_duration_minutes}m",
                    text_color="#94A3B8"
                )
                self.btn_hero_action.configure(
                    text=f"⚡ Treat {next_pt.patient_id}",
                    fg_color="#0284C7",
                    hover_color="#0369A1",
                    state="normal"
                )
            else:
                self.hero_patient_id.configure(
                    text="BAY 1 AVAILABLE",
                    text_color="#94A3B8"
                )
                self.hero_patient_desc.configure(
                    text="No patients waiting in queue. Triage bay is ready for next admission.",
                    text_color="#64748B"
                )
                self.btn_hero_action.configure(
                    text="Queue Empty",
                    fg_color="#334155",
                    state="disabled"
                )

        # Update Mini Queue preview
        for widget in self.queue_rows_container.winfo_children():
            widget.destroy()

        waiting_list = self.service.get_waiting_queue_ordered()[:5]
        if not waiting_list:
            empty = EmptyState(
                self.queue_rows_container,
                title="Emergency Queue is Clear",
                message="No patients are currently awaiting treatment.",
                icon_symbol="✨"
            )
            empty.pack(fill="x")
        else:
            for idx, p in enumerate(waiting_list):
                row = ctk.CTkFrame(self.queue_rows_container, fg_color="transparent", height=38)
                row.pack(fill="x", pady=2)

                pos_lbl = ctk.CTkLabel(
                    row,
                    text=f"#{idx + 1}",
                    width=40,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
                    text_color=Theme.PRIMARY_BLUE if idx == 0 else Theme.TEXT_MUTED
                )
                pos_lbl.pack(side="left", padx=5)

                id_lbl = ctk.CTkLabel(
                    row,
                    text=p.patient_id,
                    width=90,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=12, weight="bold"),
                    text_color=Theme.TEXT_MAIN,
                    anchor="w"
                )
                id_lbl.pack(side="left", padx=5)

                name_lbl = ctk.CTkLabel(
                    row,
                    text=p.name,
                    width=140,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
                    text_color=Theme.TEXT_MAIN,
                    anchor="w"
                )
                name_lbl.pack(side="left", padx=5)

                badge = PriorityBadge(row, priority=p.priority)
                badge.pack(side="left", padx=5)

                wait_lbl = ctk.CTkLabel(
                    row,
                    text=f"{p.waiting_duration_minutes} mins",
                    width=80,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                    text_color=Theme.TEXT_MUTED,
                    anchor="e"
                )
                wait_lbl.pack(side="right", padx=10)

        # Update Priority Donut Chart
        self._render_donut_chart(stats["priority_distribution"])

        # Update Recent Activity Rows
        for widget in self.activity_rows_container.winfo_children():
            widget.destroy()

        activities = self.service.activity_log[-4:]
        activities.reverse()
        if not activities:
            ctk.CTkLabel(
                self.activity_rows_container,
                text="No recent events logged yet.",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=10)
        else:
            for act in activities:
                row = ctk.CTkFrame(self.activity_rows_container, fg_color="transparent")
                row.pack(fill="x", pady=3)

                dot_color = (
                    Theme.COLOR_CRITICAL if act["level"] == "critical"
                    else (Theme.COLOR_HIGH if act["level"] == "warning"
                          else (Theme.COLOR_NORMAL if act["level"] == "success"
                                else Theme.PRIMARY_BLUE))
                )

                dot = ctk.CTkLabel(row, text="●", text_color=dot_color, font=ctk.CTkFont(size=12))
                dot.pack(side="left", padx=(0, 8))

                time_lbl = ctk.CTkLabel(
                    row,
                    text=act["timestamp"],
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=11),
                    text_color=Theme.TEXT_MUTED,
                    width=75,
                    anchor="w"
                )
                time_lbl.pack(side="left")

                msg_lbl = ctk.CTkLabel(
                    row,
                    text=act["message"],
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
                    text_color=Theme.TEXT_MAIN,
                    anchor="w"
                )
                msg_lbl.pack(side="left", fill="x", expand=True)

    def _render_donut_chart(self, distribution: dict):
        """Draws Matplotlib Donut Chart for Priority Distribution."""
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None

        labels = ["Critical", "High", "Normal"]
        values = [
            distribution.get("Critical Emergency", 0),
            distribution.get("High Priority", 0),
            distribution.get("Normal", 0)
        ]
        total_waiting = sum(values)

        colors = [Theme.COLOR_CRITICAL, Theme.COLOR_HIGH, Theme.COLOR_NORMAL]

        fig = Figure(figsize=(3.4, 2.2), dpi=100, facecolor=Theme.BG_CARD)
        ax = fig.add_subplot(111)

        if total_waiting == 0:
            # Empty donut ring
            ax.pie([1], colors=["#E2E8F0"], startangle=90, wedgeprops=dict(width=0.35, edgecolor="none"))
            ax.text(0, 0, "No Queue", ha="center", va="center", fontsize=11, color=Theme.TEXT_MUTED, weight="bold", fontfamily=Theme.FONT_FAMILY)
        else:
            # Filter non-zero slices
            filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
            f_labels, f_values, f_colors = zip(*filtered)

            wedges, _ = ax.pie(
                f_values,
                colors=f_colors,
                startangle=90,
                wedgeprops=dict(width=0.38, edgecolor=Theme.BG_CARD, linewidth=2)
            )
            # Center text displaying total
            ax.text(0, 0.1, str(total_waiting), ha="center", va="center", fontsize=18, weight="bold", color=Theme.TEXT_MAIN, fontfamily=Theme.FONT_FAMILY)
            ax.text(0, -0.2, "Waiting", ha="center", va="center", fontsize=9, color=Theme.TEXT_MUTED, fontfamily=Theme.FONT_FAMILY)

            # Clean legend below
            legend_labels = [f"{l} ({v})" for l, v in zip(f_labels, f_values)]
            ax.legend(
                wedges,
                legend_labels,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.25),
                ncol=3,
                frameon=False,
                fontsize=8
            )

        ax.axis("equal")
        fig.tight_layout(pad=0.2)

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _handle_hero_action(self):
        """Starts treatment or navigates to treatment completion dialog."""
        if self.service.active_patient is not None:
            # Navigate to treatment page
            self.on_navigate("treatment")
        else:
            ok, msg, _ = self.service.start_treatment()
            self.refresh_data()


