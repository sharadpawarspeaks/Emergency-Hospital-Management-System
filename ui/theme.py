"""
Design Theme and Color Palette for Hospital Emergency Management System.
Inspired by modern clinical administration dashboards.
"""

class Theme:
    # App Information
    APP_NAME = "MediCare Emergency Triage"
    HOSPITAL_NAME = "City Care Central Hospital"
    VERSION = "v2.4 - Enterprise Healthcare Edition"

    # Color Palette
    # Backgrounds
    BG_APP = "#F4F7FC"              # Soft grey-blue dashboard background
    BG_SIDEBAR = "#0F172A"          # Deep rich slate navy
    BG_SIDEBAR_HOVER = "#1E293B"    # Slightly lighter navy for hover
    BG_SIDEBAR_ACTIVE = "#2563EB"   # Royal blue for active tab
    BG_CARD = "#FFFFFF"             # Crisp pure white cards
    BG_CARD_SECONDARY = "#F8FAFC"   # Subtle off-white for table headers/stripes
    BG_INPUT = "#FFFFFF"            # White form inputs
    BG_HERO_CARD = "#0B192C"        # Dark sapphire hero banner for "Now Serving"

    # Borders & Dividers
    BORDER_LIGHT = "#E2E8F0"
    BORDER_MEDIUM = "#CBD5E1"
    BORDER_ACTIVE = "#3B82F6"

    # Text Colors
    TEXT_MAIN = "#0F172A"           # Dark slate for primary headings
    TEXT_MUTED = "#64748B"          # Grey for labels and descriptions
    TEXT_LIGHT = "#F8FAFC"          # Light text for dark sidebar
    TEXT_LIGHT_MUTED = "#94A3B8"    # Muted light text
    TEXT_BRAND = "#2563EB"          # Vibrant medical blue

    # Brand & Medical Accent Colors
    PRIMARY_BLUE = "#2563EB"        # Medical Royal Blue
    PRIMARY_HOVER = "#1D4ED8"
    TEAL_ACCENT = "#0D9488"         # Medical Teal
    TEAL_HOVER = "#0F766E"

    # Priority Colors (Consistent across entire app)
    # 1: Critical Emergency
    COLOR_CRITICAL = "#DC2626"      # Medical Red
    BG_CRITICAL_BADGE = "#FEE2E2"
    TEXT_CRITICAL_BADGE = "#991B1B"

    # 2: High Priority
    COLOR_HIGH = "#D97706"          # Urgent Amber/Orange
    BG_HIGH_BADGE = "#FEF3C7"
    TEXT_HIGH_BADGE = "#92400E"

    # 3: Normal Priority
    COLOR_NORMAL = "#059669"        # Stable Emerald Green
    BG_NORMAL_BADGE = "#D1FAE5"
    TEXT_NORMAL_BADGE = "#065F46"

    # Status Colors
    COLOR_WAITING = "#D97706"
    COLOR_IN_TREATMENT = "#2563EB"
    COLOR_COMPLETED = "#059669"
    COLOR_CANCELLED = "#64748B"

    # Font Families (Standard clean system fonts that render crisply on Windows)
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    # Spacings
    PAD_SMALL = 8
    PAD_MEDIUM = 16
    PAD_LARGE = 24
    RADIUS_CARD = 12
    RADIUS_BUTTON = 8
    RADIUS_BADGE = 14
