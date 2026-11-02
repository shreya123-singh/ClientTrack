
import streamlit as st
import pandas as pd
import plotly.express as px

from database.db import fetch_data


def show_reports():

    st.title("📊 Reports & Analytics")
    st.write("Analyze business performance and track important statistics.")
    st.markdown("---")

    # Fetch Data
    clients = fetch_data("SELECT * FROM clients")
    leads = fetch_data("SELECT * FROM leads")
    projects = fetch_data("SELECT * FROM projects")
    followups = fetch_data("SELECT * FROM followups")
    meetings = fetch_data("SELECT * FROM meetings")
    progress_records = fetch_data("""
        SELECT daily_progress.*, projects.name AS project_name
        FROM daily_progress
        LEFT JOIN projects
        ON daily_progress.project_id = projects.id
    """)

    # Main Statistics
    st.subheader("📌 Business Summary")

    total_clients = len(clients)
    total_leads = len(leads)
    total_projects = len(projects)

    completed_projects = sum(
        1 for p in projects if p["status"] == "Completed"
    )

    pending_followups = sum(
        1 for f in followups if f["status"] == "Pending"
    )

    scheduled_meetings = sum(
        1 for m in meetings if m["status"] == "Scheduled"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Clients", total_clients)
    c2.metric("Total Leads", total_leads)
    c3.metric("Total Projects", total_projects)

    c4, c5, c6 = st.columns(3)

    c4.metric("Completed Projects", completed_projects)
    c5.metric("Pending Follow-Ups", pending_followups)
    c6.metric("Scheduled Meetings", scheduled_meetings)

    st.markdown("---")

    # Leads Analysis
    st.subheader("📈 Leads Analysis")

    if leads:

        lead_df = pd.DataFrame([dict(l) for l in leads])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Leads by Status**")

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
                hole=0.45
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Leads by Source**")

            source_data = (
                lead_df["source"]
                .fillna("Unknown")
                .replace("", "Unknown")
                .value_counts()
                .reset_index()
            )

            source_data.columns = ["Source", "Count"]

            fig = px.bar(
                source_data,
                x="Source",
                y="Count",
                color="Source"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No lead data available for analysis.")

    st.markdown("---")

    # Projects Analysis
    st.subheader("📁 Projects Analysis")

    if projects:

        project_df = pd.DataFrame([dict(p) for p in projects])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Projects by Status**")

            status_data = (
                project_df["status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Count"]

            fig = px.bar(
                status_data,
                x="Status",
                y="Count",
                color="Status"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Project Progress (%)**")

            fig = px.bar(
                project_df,
                x="name",
                y="progress",
                color="status",
                range_y=[0, 100],
                labels={
                    "name": "Project",
                    "progress": "Progress (%)",
                    "status": "Status"
                }
            )

            st.plotly_chart(fig, use_container_width=True)

        # Project Budget
        total_budget = sum(
            float(p["budget"] or 0) for p in projects
        )

        st.metric(
            "Total Project Budget",
            f"₹ {total_budget:,.2f}"
        )

    else:
        st.info("No project data available for analysis.")

    st.markdown("---")

    # Follow-Up Analysis
    st.subheader("📌 Follow-Up Statistics")

    if followups:

        followup_df = pd.DataFrame([dict(f) for f in followups])

        followup_data = (
            followup_df["status"]
            .value_counts()
            .reset_index()
        )

        followup_data.columns = ["Status", "Count"]

        fig = px.pie(
            followup_data,
            names="Status",
            values="Count",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No follow-up records available.")

    st.markdown("---")

    # Daily Progress Analysis
    st.subheader("📅 Daily Progress Report")

    if progress_records:

        progress_df = pd.DataFrame(
            [dict(p) for p in progress_records]
        )

        progress_df["progress_date"] = pd.to_datetime(
            progress_df["progress_date"]
        )

        progress_df = progress_df.sort_values("progress_date")

        fig = px.line(
            progress_df,
            x="progress_date",
            y="progress_percentage",
            color="project_name",
            markers=True,
            labels={
                "progress_date": "Date",
                "progress_percentage": "Progress (%)",
                "project_name": "Project"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No daily progress records available.")

    st.markdown("---")

    # Export Reports
    st.subheader("📥 Download Reports")

    report_type = st.selectbox(
        "Select Report",
        [
            "Clients",
            "Leads",
            "Projects",
            "Follow-Ups",
            "Communication Summary"
        ]
    )

    report_queries = {
        "Clients": "SELECT * FROM clients",
        "Leads": "SELECT * FROM leads",
        "Projects": "SELECT * FROM projects",
        "Follow-Ups": """
            SELECT followups.*, clients.name AS client_name
            FROM followups
            LEFT JOIN clients ON followups.client_id = clients.id
        """,
        "Communication Summary": """
            SELECT communication_log.*, clients.name AS client_name
            FROM communication_log
            LEFT JOIN clients
            ON communication_log.client_id = clients.id
        """
    }

    report_data = fetch_data(report_queries[report_type])

    if report_data:

        export_df = pd.DataFrame([dict(r) for r in report_data])

        csv_data = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_data,
            file_name=report_type.lower().replace(" ", "_") + "_report.csv",
            mime="text/csv"
        )

    else:
        st.info("No records available for this report.")
