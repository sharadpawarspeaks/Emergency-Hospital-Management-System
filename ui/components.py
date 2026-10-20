"""
Reusable UI Components for Hospital Emergency Management System.
Built with CustomTkinter following clinical dashboard design patterns.
"""

import customtkinter as ctk
from typing import Optional, Callable, Dict, Any
from ui.theme import Theme
from models.patient import Patient, PriorityLevel, PatientStatus


class CardFrame(ctk.CTkFrame):
    """Clean white card with subtle border and rounded corners."""
    def __init__(
        self,
        master,
        corner_radius: int = Theme.RADIUS_CARD,
        fg_color: Optional[str] = None,
        border_width: int = 1,
        border_color: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=corner_radius,
            fg_color=fg_color if fg_color is not None else Theme.BG_CARD,
            border_width=border_width,
            border_color=border_color if border_color is not None else Theme.BORDER_LIGHT,
            **kwargs
        )


class StatCard(ctk.CTkFrame):
    """
    Summary Metric Card displaying key hospital metrics:
    - Metric Icon / Tag
    - Large formatted number
    - Descriptive label
    - Color accent bar
    """
    def __init__(
        self,
        master,
        title: str,
        value: str,
        accent_color: str,
        icon_text: str = "●",
        subtitle: str = "Real-time count",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            **kwargs
        )
        self.accent_color = accent_color

        # Left accent stripe
        self.stripe = ctk.CTkFrame(
            self,
            width=5,
            corner_radius=2,
            fg_color=accent_color
        )
        self.stripe.pack(side="left", fill="y", padx=(0, 12))

        # Content container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 16))

        # Top row: title & icon
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        self.title_lbl = ctk.CTkLabel(
            top_row,
            text=title.upper(),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.title_lbl.pack(side="left")

        self.icon_badge = ctk.CTkLabel(
            top_row,
            text=f" {icon_text} ",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=accent_color,
            fg_color=Theme.BG_CARD_SECONDARY,
            corner_radius=6
        )
        self.icon_badge.pack(side="right")

        # Number value
        self.val_lbl = ctk.CTkLabel(
            content,
            text=str(value),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=28, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.val_lbl.pack(anchor="w", pady=(4, 2))

        # Subtitle / trend
        self.sub_lbl = ctk.CTkLabel(
            content,
            text=subtitle,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        self.sub_lbl.pack(anchor="w")

    def update_value(self, value: Any, subtitle: Optional[str] = None) -> None:
        self.val_lbl.configure(text=str(value))
        if subtitle:
            self.sub_lbl.configure(text=subtitle)


class PriorityBadge(ctk.CTkFrame):
    """Pill badge with standardized triage priority color coding."""
    def __init__(self, master, priority: int, **kwargs):
        if priority == PriorityLevel.CRITICAL:
            fg = Theme.BG_CRITICAL_BADGE
            text_col = Theme.TEXT_CRITICAL_BADGE
            dot_col = Theme.COLOR_CRITICAL
            label = "Critical Emergency"
        elif priority == PriorityLevel.HIGH:
            fg = Theme.BG_HIGH_BADGE
            text_col = Theme.TEXT_HIGH_BADGE
            dot_col = Theme.COLOR_HIGH
            label = "High Priority"
        else:
            fg = Theme.BG_NORMAL_BADGE
            text_col = Theme.TEXT_NORMAL_BADGE
            dot_col = Theme.COLOR_NORMAL
            label = "Normal Priority"

        super().__init__(
            master,
            corner_radius=Theme.RADIUS_BADGE,
            fg_color=fg,
            border_width=0,
            **kwargs
        )

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=10, pady=3)

        dot = ctk.CTkLabel(
            inner,
            text="●",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9),
            text_color=dot_col
        )
        dot.pack(side="left", padx=(0, 4))

        lbl = ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=text_col
        )
        lbl.pack(side="left")


class StatusBadge(ctk.CTkFrame):
    """Pill badge showing patient workflow status."""
    def __init__(self, master, status: str, **kwargs):
        if status == PatientStatus.WAITING:
            fg = "#FEF3C7"
            text_col = "#92400E"
            label = "Waiting in Queue"
        elif status == PatientStatus.IN_TREATMENT:
            fg = "#DBEAFE"
            text_col = "#1E40AF"
            label = "● In Treatment"
        elif status == PatientStatus.COMPLETED:
            fg = "#D1FAE5"
            text_col = "#065F46"
            label = "✓ Completed"
        else:
            fg = "#F1F5F9"
            text_col = "#475569"
            label = status

        super().__init__(
            master,
            corner_radius=Theme.RADIUS_BADGE,
            fg_color=fg,
            **kwargs
        )
        lbl = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=text_col
        )
        lbl.pack(padx=10, pady=3)


class EmptyState(ctk.CTkFrame):
    """Clean empty placeholder when no data exists."""
    def __init__(self, master, title: str, message: str, icon_symbol: str = "📭", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        icon_lbl = ctk.CTkLabel(
            self,
            text=icon_symbol,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=38),
            text_color=Theme.TEXT_MUTED
        )
        icon_lbl.pack(pady=(20, 6))

        title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title_lbl.pack(pady=(0, 4))

        msg_lbl = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        msg_lbl.pack(pady=(0, 20))


class AlertBanner(ctk.CTkFrame):
    """Inline notification alert message."""
    def __init__(self, master, message: str, alert_type: str = "info", **kwargs):
        if alert_type == "success":
            bg = "#ECFDF5"
            border = "#A7F3D0"
            text_col = "#065F46"
            icon = "✓ "
        elif alert_type == "error":
            bg = "#FEF2F2"
            border = "#FECACA"
            text_col = "#991B1B"
            icon = "✕ "
        elif alert_type == "warning":
            bg = "#FFFBEB"
            border = "#FDE68A"
            text_col = "#92400E"
            icon = "⚠ "
        else:
            bg = "#EFF6FF"
            border = "#BFDBFE"
            text_col = "#1E40AF"
            icon = "ℹ "

        super().__init__(
            master,
            corner_radius=8,
            fg_color=bg,
            border_width=1,
            border_color=border,
            **kwargs
        )

        lbl = ctk.CTkLabel(
            self,
            text=f"{icon}{message}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=text_col
        )
        lbl.pack(side="left", padx=12, pady=8)


class PatientDetailsModal(ctk.CTkToplevel):
    """Modal popup displaying full clinical record for a patient."""
    def __init__(self, master, patient: Patient):
        super().__init__(master)
        self.title(f"Patient Record - {patient.patient_id}")
        self.geometry("540x620")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_APP)

        # Center modal on parent
        self.transient(master)
        self.grab_set()

        # Header
        header = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, height=70, corner_radius=0)
        header.pack(fill="x")

        title_lbl = ctk.CTkLabel(
            header,
            text=f"{patient.name} ({patient.patient_id})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title_lbl.pack(side="left", padx=20, pady=16)

        # Status Badge in header
        badge = StatusBadge(header, status=patient.status)
        badge.pack(side="right", padx=20)

        # Body container
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        def make_field(label: str, val: str, is_badge: bool = False):
            row = CardFrame(body)
            row.pack(fill="x", pady=4)
            lbl = ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                text_color=Theme.TEXT_MUTED,
                width=140,
                anchor="w"
            )
            lbl.pack(side="left", padx=14, pady=10)

            if is_badge:
                p_badge = PriorityBadge(row, priority=patient.priority)
                p_badge.pack(side="left", padx=10, pady=8)
            else:
                val_lbl = ctk.CTkLabel(
                    row,
                    text=val or "N/A",
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
                    text_color=Theme.TEXT_MAIN,
                    wraplength=300,
                    justify="left",
                    anchor="w"
                )
                val_lbl.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        make_field("Priority Level:", "", is_badge=True)
        make_field("Age & Gender:", f"{patient.age} years  |  {patient.gender}")
        make_field("Contact Phone:", patient.contact or "Not Provided")
        make_field("Symptoms / Reason:", patient.symptoms)
        make_field("Arrival Time:", patient.arrival_time)
        make_field("Waiting Duration:", f"{patient.waiting_duration_minutes} minutes")
        make_field("Arrival Sequence #:", str(patient.arrival_sequence))
        make_field("Attending Doctor:", patient.attending_doctor or "Unassigned")
        make_field("Assigned Room / Bay:", patient.triage_room or "Unassigned")
        make_field("Treatment Started:", patient.treatment_start_time or "Not Started")
        make_field("Treatment Completed:", patient.treatment_completion_time or "Not Completed")
        if patient.treatment_notes:
            make_field("Clinical Notes:", patient.treatment_notes)

        # Close button
        btn_close = ctk.CTkButton(
            self,
            text="Close Window",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.destroy,
            height=38,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_close.pack(pady=14, padx=20, fill="x")
