
import streamlit as st
from pathlib import Path

from database.db import DB_PATH, fetch_data


def show_settings():

    st.title("⚙️ Settings")
    st.write("Application information and database management.")
    st.markdown("---")

    # Application Information
    st.subheader("ℹ️ Application Information")

    c1, c2 = st.columns(2)

    c1.metric("Application", "ClientTrack")
    c2.metric("Version", "1.0")

    st.markdown("""
    **Project Name:** ClientTrack

    **Tagline:** Manage Clients. Track Projects. Stay Organized.

    **Technology Stack:**
    - Python
    - Streamlit
    - SQLite
    - Pandas
    - Plotly
    """)

    st.markdown("---")

    # Database Information
    st.subheader("🗄️ Database Information")

    database_path = Path(DB_PATH)

    if database_path.exists():

        st.success("Database connected successfully.")

        st.write(f"Database file: `{database_path.name}`")

        st.download_button(
            label="⬇️ Download Database Backup",
            data=database_path.read_bytes(),
            file_name="clienttrack_backup.db",
            mime="application/octet-stream"
        )

        st.caption(
            "Keep your backup file safe. It contains your saved client "
            "and business records."
        )

    else:
        st.error("Database file not found.")

    st.markdown("---")

    # Record Counts
    st.subheader("📊 Stored Records")

    tables = {
        "Clients": "clients",
        "Leads": "leads",
        "Projects": "projects",
        "Meetings": "meetings",
        "Follow-Ups": "followups",
        "Daily Progress": "daily_progress",
        "Notes": "notes",
        "Communication Logs": "communication_log",
        "Users": "users"
    }

    columns = st.columns(3)

    for index, (label, table) in enumerate(tables.items()):

        records = fetch_data(f"SELECT COUNT(*) AS total FROM {table}")

        columns[index % 3].metric(
            label,
            records[0]["total"]
        )

    st.markdown("---")

    # About
    st.subheader("💡 About ClientTrack")

    st.write("""
    ClientTrack is a Client Management and Project Tracking System
    designed to organize client information, manage leads, schedule
    follow-ups, track projects and monitor business activities.

    It provides a centralized platform for maintaining business records
    and viewing performance through reports and analytics.
    """)

    st.caption("ClientTrack Management System | Version 1.0")
