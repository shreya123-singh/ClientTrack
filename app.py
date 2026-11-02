
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from database.db import create_tables, fetch_data

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="ClientTrack",
    page_icon="📊",
    layout="wide"
)

# ---------------- DATABASE ----------------

create_tables()

# ---------------- LOAD CSS ----------------

css_path = Path("styles/style.css")

if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ---------------- NAVIGATION ----------------

menu_options = [
    "Dashboard",
    "Clients",
    "Leads & Pipeline",
    "Calls & Meetings",
    "Follow-Ups",
    "Projects",
    "Daily Progress",
    "Notes",
    "Communication Log",
    "Reports & Analytics",
    "Users & Roles",
    "Java & MySQL Hub",
    "Settings"
]

if "main_menu" not in st.session_state:
    st.session_state["main_menu"] = "Dashboard"


def go_to_page(page):
    st.session_state["main_menu"] = page


# ---------------- SIDEBAR ----------------

st.sidebar.title("🌿 ClientTrack")
st.sidebar.caption("Manage Clients. Track Projects.")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MAIN MENU",
    menu_options,
    key="main_menu"
)

st.sidebar.markdown("---")
st.sidebar.caption("ClientTrack Management System")


# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.title("ClientTrack Command Center")
    st.write("Welcome back! Here's your business overview.")
    st.markdown("---")

    # Fetch database records
    clients = fetch_data("SELECT * FROM clients")
    leads = fetch_data("SELECT * FROM leads")
    projects = fetch_data("SELECT * FROM projects")

    followups = fetch_data(
        "SELECT * FROM followups WHERE status = 'Pending'"
    )

    meetings = fetch_data(
        "SELECT * FROM meetings WHERE status = 'Scheduled'"
    )

    # Dashboard metrics
    total_clients = len(clients)
    total_leads = len(leads)
    total_projects = len(projects)
    pending_followups = len(followups)
    scheduled_meetings = len(meetings)

    completed_projects = sum(
        1 for p in projects if p["status"] == "Completed"
    )

    # First row
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Clients", total_clients)
    col2.metric("Total Leads", total_leads)
    col3.metric("Total Projects", total_projects)

    # Second row
    col4, col5, col6 = st.columns(3)

    col4.metric("Pending Follow-Ups", pending_followups)
    col5.metric("Scheduled Meetings", scheduled_meetings)
    col6.metric("Completed Projects", completed_projects)

    st.markdown("---")

    # ---------------- QUICK ACTIONS ----------------

    st.subheader("⚡ Quick Actions")

    action1, action2, action3, action4 = st.columns(4)

    with action1:
        st.button(
            "➕ Add Client",
            use_container_width=True,
            on_click=go_to_page,
            args=("Clients",)
        )

    with action2:
        st.button(
            "➕ Add Lead",
            use_container_width=True,
            on_click=go_to_page,
            args=("Leads & Pipeline",)
        )

    with action3:
        st.button(
            "📞 Schedule Call",
            use_container_width=True,
            on_click=go_to_page,
            args=("Calls & Meetings",)
        )

    with action4:
        st.button(
            "📌 Add Follow-Up",
            use_container_width=True,
            on_click=go_to_page,
            args=("Follow-Ups",)
        )

    action5, action6, action7, action8 = st.columns(4)

    with action5:
        st.button(
            "🤝 Schedule Meet",
            use_container_width=True,
            on_click=go_to_page,
            args=("Calls & Meetings",)
        )

    with action6:
        st.button(
            "📁 Create Project",
            use_container_width=True,
            on_click=go_to_page,
            args=("Projects",)
        )

    with action7:
        st.button(
            "📈 Add Progress",
            use_container_width=True,
            on_click=go_to_page,
            args=("Daily Progress",)
        )

    with action8:
        st.button(
            "📝 Add Note",
            use_container_width=True,
            on_click=go_to_page,
            args=("Notes",)
        )

    st.markdown("---")

    # ---------------- BUSINESS OVERVIEW ----------------

    st.subheader("📊 Business Overview")

    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("**Leads by Status**")

        if leads:
            lead_df = pd.DataFrame(
                [dict(row) for row in leads]
            )

            status_data = (
                lead_df["status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Count"]

            fig = px.pie(
                status_data,
                names="Status",
                values="Count",
                hole=0.5
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("No leads available yet. Add your first lead.")

    with chart2:
        st.markdown("**Projects by Status**")

        if projects:
            project_df = pd.DataFrame(
                [dict(row) for row in projects]
            )

            project_data = (
                project_df["status"]
                .value_counts()
                .reset_index()
            )

            project_data.columns = ["Status", "Count"]

            fig = px.bar(
                project_data,
                x="Status",
                y="Count",
                color="Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("No projects available yet. Create your first project.")

    st.markdown("---")

    # ---------------- FOLLOW-UP WATCHLIST ----------------

    st.subheader("📅 Follow-Up Watchlist")

    if followups:
        followup_df = pd.DataFrame(
            [dict(row) for row in followups]
        )

        st.dataframe(
            followup_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No pending follow-ups right now.")


# ---------------- OTHER MODULES ----------------

elif menu == "Clients":

    from pages.clients import show_clients
    show_clients()


elif menu == "Leads & Pipeline":

    from pages.leads import show_leads
    show_leads()


elif menu == "Calls & Meetings":

    from pages.calls_meetings import show_calls_meetings
    show_calls_meetings()


elif menu == "Follow-Ups":

    from pages.followups import show_followups
    show_followups()


elif menu == "Projects":

    from pages.projects import show_projects
    show_projects()


elif menu == "Daily Progress":

    from pages.daily_progress import show_daily_progress
    show_daily_progress()


elif menu == "Notes":

    from pages.notes import show_notes
    show_notes()


elif menu == "Communication Log":

    from pages.communication import show_communication_log
    show_communication_log()


elif menu == "Reports & Analytics":

    from pages.reports import show_reports
    show_reports()


elif menu == "Users & Roles":

    from pages.users import show_users
    show_users()


elif menu == "Java & MySQL Hub":

    from pages.java_mysql import show_java_mysql_hub
    show_java_mysql_hub()


elif menu == "Settings":

    from pages.settings import show_settings
    show_settings()
