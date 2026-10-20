"""
Main Application Entry Point for Hospital Emergency Management System.
Features:
- CustomTkinter high-DPI modern graphical interface
- Fixed Left Sidebar with clinical branding and active navigation states
- Top Navigation Bar with live clock, ER status pill, quick action button, and physician profile
- Dynamic responsive page switching
- Data structure persistence and automatic updates
"""

import sys
import os

# Ensure workspace and Python site-packages are always discoverable by IDE and runners
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

site_pkg = r"C:\Users\pawar\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages"
if os.path.exists(site_pkg) and site_pkg not in sys.path:
    sys.path.append(site_pkg)

from datetime import datetime
import customtkinter as ctk

from ui.theme import Theme
from services.hospital_service import HospitalService
from ui.dashboard import DashboardPage
from ui.registration import RegistrationPage
from ui.emergency_queue import EmergencyQueuePage
from ui.patient_records import PatientRecordsPage
from ui.treatment import TreatmentPage
from ui.treatment_history import TreatmentHistoryPage
from ui.about_page import AboutPage


class HospitalEmergencyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Hospital Emergency Management System — MediCare ER")
        self.geometry("1320x840")
        self.minsize(1050, 700)

        # Set default appearance
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=Theme.BG_APP)

        # Initialize Central Hospital Service
        self.service = HospitalService()

        # Track navigation
        self.current_page_key = "dashboard"
        self.nav_buttons = {}

        # Build Main Layout
        self._build_layout()
        self._start_clock_timer()

        # Default Page
        self.navigate_to("dashboard")

    def _build_layout(self):
        # 1. Left Fixed Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # 2. Main Right Container
        self.main_container = ctk.CTkFrame(self, fg_color=Theme.BG_APP)
        self.main_container.pack(side="left", fill="both", expand=True)

        # Top Bar
        self.top_bar = ctk.CTkFrame(
            self.main_container,
            height=68,
            corner_radius=0,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)
        self._build_top_bar()

        # Page Display Viewport
        self.content_viewport = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_viewport.pack(side="top", fill="both", expand=True, padx=24, pady=20)

    def _build_sidebar(self):
        # Hospital Logo & Brand Box
        brand_box = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        brand_box.pack(fill="x", padx=20, pady=(20, 16))

        logo_row = ctk.CTkFrame(brand_box, fg_color="transparent")
        logo_row.pack(fill="x")

        # Hospital Cross Icon Chip
        icon_chip = ctk.CTkLabel(
            logo_row,
            text=" ➕ ",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color="#FFFFFF",
            fg_color=Theme.PRIMARY_BLUE,
            corner_radius=8,
            width=34,
            height=34
        )
        icon_chip.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(logo_row, fg_color="transparent")
        title_box.pack(side="left")

        brand_lbl = ctk.CTkLabel(
            title_box,
            text="MediCare ER",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=17, weight="bold"),
            text_color="#F8FAFC"
        )
        brand_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text=Theme.HOSPITAL_NAME,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_LIGHT_MUTED
        )
        sub_lbl.pack(anchor="w")

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#1E293B").pack(fill="x", padx=16, pady=(0, 14))

        # Navigation Links
        nav_items = [
            ("dashboard", "📊  Dashboard", "Overview & Triage Stats"),
            ("register", "➕  Register Patient", "Intake & Priority Triage"),
            ("queue", "⏳  Emergency Queue", "Binary Min-Heap Queue"),
            ("records", "🗂️  Patient Records", "Singly Linked List"),
            ("treatment", "🏥  Treatment Bay", "Active Care Monitoring"),
            ("history", "📋  Treatment History", "Completed Care Archives"),
            ("about", "ℹ️  System Architecture", "Algorithms & Technical Specs")
        ]

        self.nav_menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_menu_frame.pack(fill="x", padx=12)

        for key, title, desc in nav_items:
            btn = ctk.CTkButton(
                self.nav_menu_frame,
                text=f"  {title}",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
                anchor="w",
                height=42,
                corner_radius=Theme.RADIUS_BUTTON,
                fg_color="transparent",
                text_color=Theme.TEXT_LIGHT,
                hover_color=Theme.BG_SIDEBAR_HOVER,
                command=lambda k=key: self.navigate_to(k)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = btn

        # Bottom System Info Box
        bottom_box = ctk.CTkFrame(self.sidebar, fg_color="#090E17", corner_radius=10)
        bottom_box.pack(side="bottom", fill="x", padx=12, pady=16)

        b_inner = ctk.CTkFrame(bottom_box, fg_color="transparent")
        b_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            b_inner,
            text="🟢  SYSTEM ONLINE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color="#10B981"
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_inner,
            text=f"{Theme.VERSION}\nStorage: data/patients.json",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color="#64748B",
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

    def _build_top_bar(self):
        container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24)

        # Left: Current Page Breadcrumb
        left_box = ctk.CTkFrame(container, fg_color="transparent")
        left_box.pack(side="left", fill="y")

        self.page_title_lbl = ctk.CTkLabel(
            left_box,
            text="Dashboard Overview",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.page_title_lbl.pack(side="left", pady=18)

        # Right: Clock, Status Indicator, Register Shortcut, Profile
        right_box = ctk.CTkFrame(container, fg_color="transparent")
        right_box.pack(side="right", fill="y")

        # Live Real-time Clock
        self.clock_lbl = ctk.CTkLabel(
            right_box,
            text="--:--:--",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.clock_lbl.pack(side="left", padx=(0, 16), pady=20)

        # Emergency Triage Active Pill
        status_pill = ctk.CTkLabel(
            right_box,
            text=" ● Emergency Triage Active ",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color="#065F46",
            fg_color="#D1FAE5",
            corner_radius=12,
            height=28
        )
        status_pill.pack(side="left", padx=(0, 14), pady=20)

        # Quick Register Action Button
        btn_quick_reg = ctk.CTkButton(
            right_box,
            text="+ Register Patient",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER,
            command=lambda: self.navigate_to("register"),
            height=32,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_quick_reg.pack(side="left", padx=(0, 16), pady=18)

        # Physician Profile Chip (Matching Image 1 & 5)
        prof_frame = ctk.CTkFrame(right_box, fg_color=Theme.BG_CARD_SECONDARY, corner_radius=18, height=36)
        prof_frame.pack(side="left", pady=16)

        ctk.CTkLabel(
            prof_frame,
            text=" 👨‍⚕️ ",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(8, 2))

        prof_text_box = ctk.CTkFrame(prof_frame, fg_color="transparent")
        prof_text_box.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            prof_text_box,
            text="Dr. Parth (Chief ER)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

    def _start_clock_timer(self):
        """Updates live top bar clock every second."""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p  |  %A, %d %b %Y")
        self.clock_lbl.configure(text=time_str)
        self.after(1000, self._start_clock_timer)

    def navigate_to(self, page_key: str):
        self.current_page_key = page_key

        # Update sidebar active buttons
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(
                    fg_color=Theme.BG_SIDEBAR_ACTIVE,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_LIGHT
                )

        # Clear viewport
        for widget in self.content_viewport.winfo_children():
            widget.destroy()

        # Titles
        titles = {
            "dashboard": "Emergency Department Dashboard",
            "register": "Patient Registration & Clinical Triage Intake",
            "queue": "Priority-Based Emergency Queue (Binary Min-Heap)",
            "records": "Master Patient Records (Singly Linked List)",
            "treatment": "Emergency Treatment Bay Management",
            "history": "Completed Treatment History & Clinical Archives",
            "about": "System Architecture & Technical Specifications"
        }
        self.page_title_lbl.configure(text=titles.get(page_key, "Hospital Emergency Management"))

        # Instantiate requested page
        if page_key == "dashboard":
            DashboardPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "register":
            RegistrationPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "queue":
            EmergencyQueuePage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "records":
            PatientRecordsPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "treatment":
            TreatmentPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "history":
            TreatmentHistoryPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)
        elif page_key == "about":
            AboutPage(self.content_viewport, service=self.service, on_navigate=self.navigate_to).pack(fill="both", expand=True)


def main():
    app = HospitalEmergencyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
