
import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_daily_progress():

    st.title("📈 Daily Progress Tracking")
    st.write("Record daily work and monitor project progress.")
    st.markdown("---")

    projects = fetch_data("""
        SELECT id, name, progress, status
        FROM projects
        ORDER BY name
    """)

    if not projects:
        st.warning("Please create a project first in the Projects module.")
        return

    project_options = {
        f"{p['name']} (ID: {p['id']})": p["id"]
        for p in projects
    }

    # Add Daily Progress
    st.subheader("➕ Add Daily Progress")

    with st.form("add_daily_progress", clear_on_submit=True):

        selected_project = st.selectbox(
            "Select Project",
            list(project_options.keys())
        )

        progress_date = st.date_input(
            "Progress Date",
            value=date.today()
        )

        progress_percentage = st.slider(
            "Current Project Progress (%)",
            min_value=0,
            max_value=100,
            value=0
        )

        description = st.text_area(
            "Work Completed Today *",
            placeholder="Describe the work completed today..."
        )

        submitted = st.form_submit_button("Save Daily Progress")

        if submitted:

            if not description.strip():
                st.error("Please enter today's work details.")

            else:
                project_id = project_options[selected_project]

                execute_query(
                    """
                    INSERT INTO daily_progress
                    (project_id, progress_date, description, progress_percentage)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        str(progress_date),
                        description.strip(),
                        progress_percentage
                    )
                )

                execute_query(
                    """
                    UPDATE projects
                    SET progress = ?,
                        status = CASE
                            WHEN ? = 100 THEN 'Completed'
                            WHEN ? > 0 AND status IN ('Not Started', 'Completed')
                                THEN 'In Progress'
                            ELSE status
                        END
                    WHERE id = ?
                    """,
                    (
                        progress_percentage,
                        progress_percentage,
                        progress_percentage,
                        project_id
                    )
                )

                st.success("Daily progress saved successfully!")
                st.rerun()

    st.markdown("---")

    # Progress Summary
    st.subheader("📊 Project Progress Overview")

    total_projects = len(projects)
    completed_projects = sum(
        1 for p in projects if p["status"] == "Completed"
    )

    average_progress = (
        sum(int(p["progress"] or 0) for p in projects) / total_projects
        if total_projects else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Projects", total_projects)
    c2.metric("Completed Projects", completed_projects)
    c3.metric("Average Progress", f"{average_progress:.1f}%")

    st.markdown("---")

    # Individual Project Progress
    st.subheader("📌 Individual Project Progress")

    for project in projects:

        progress = int(project["progress"] or 0)

        st.write(f"**{project['name']}** — {progress}%")
        st.progress(progress / 100)

    st.markdown("---")

    # Progress History
    st.subheader("📋 Daily Progress History")

    records = fetch_data("""
        SELECT daily_progress.*, projects.name AS project_name
        FROM daily_progress
        LEFT JOIN projects ON daily_progress.project_id = projects.id
        ORDER BY daily_progress.progress_date DESC,
                 daily_progress.id DESC
    """)

    if records:

        df = pd.DataFrame([dict(r) for r in records])

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input("🔍 Search Project")

        with col2:
            project_filter = st.selectbox(
                "Filter Project",
                ["All"] + list(project_options.keys())
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["project_name"].str.contains(
                    search, case=False, na=False
                )
            ]

        if project_filter != "All":
            filter_id = project_options[project_filter]
            filtered = filtered[
                filtered["project_id"] == filter_id
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Delete Progress Record
        st.subheader("🗑️ Delete Progress Record")

        record_options = {
            f"{r['project_name']} - {r['progress_date']} (ID: {r['id']})":
            r["id"]
            for r in records
        }

        selected_record = st.selectbox(
            "Select Record to Delete",
            list(record_options.keys())
        )

        if st.button("Delete Selected Record"):

            record_id = record_options[selected_record]

            execute_query(
                "DELETE FROM daily_progress WHERE id = ?",
                (record_id,)
            )

            st.success("Progress record deleted successfully!")
            st.rerun()

    else:
        st.info("No daily progress records available yet.")
