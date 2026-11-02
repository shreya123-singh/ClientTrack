
import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_projects():

    st.title("📁 Project Management")
    st.write("Create, manage and track all your client projects.")
    st.markdown("---")

    clients = fetch_data(
        "SELECT id, name FROM clients ORDER BY name"
    )

    if not clients:
        st.warning("Please add a client first in the Clients module.")
        return

    client_options = {
        f"{c['name']} (ID: {c['id']})": c["id"]
        for c in clients
    }

    statuses = ["Not Started", "In Progress", "On Hold", "Completed"]

    projects = fetch_data("""
        SELECT projects.*, clients.name AS client_name
        FROM projects
        LEFT JOIN clients ON projects.client_id = clients.id
        ORDER BY projects.id DESC
    """)

    # Add Project
    st.subheader("➕ Create New Project")

    with st.form("add_project_form", clear_on_submit=True):

        name = st.text_input("Project Name *")

        client = st.selectbox(
            "Assign Client",
            list(client_options.keys())
        )

        description = st.text_area("Project Description")

        col1, col2 = st.columns(2)

        with col1:
            status = st.selectbox("Project Status", statuses)
            start_date = st.date_input("Start Date", value=date.today())

        with col2:
            progress = st.slider("Progress (%)", 0, 100, 0)
            deadline = st.date_input("Project Deadline", value=date.today())

        budget = st.number_input(
            "Project Budget",
            min_value=0.0,
            step=1000.0
        )

        submitted = st.form_submit_button("Create Project")

        if submitted:

            if not name.strip():
                st.error("Please enter a project name.")

            elif deadline < start_date:
                st.error("Deadline cannot be before the start date.")

            else:
                execute_query(
                    """
                    INSERT INTO projects
                    (name, client_id, description, status, progress,
                     start_date, deadline, budget)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        client_options[client],
                        description,
                        status,
                        progress,
                        str(start_date),
                        str(deadline),
                        budget
                    )
                )

                st.success("Project created successfully!")
                st.rerun()

    st.markdown("---")

    # Project Summary
    st.subheader("📊 Project Overview")

    total = len(projects)
    ongoing = sum(1 for p in projects if p["status"] == "In Progress")
    completed = sum(1 for p in projects if p["status"] == "Completed")
    not_started = sum(1 for p in projects if p["status"] == "Not Started")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Projects", total)
    c2.metric("Ongoing", ongoing)
    c3.metric("Completed", completed)
    c4.metric("Not Started", not_started)

    st.markdown("---")

    # Project Records
    st.subheader("📋 All Projects")

    if projects:

        df = pd.DataFrame([dict(p) for p in projects])

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input("🔍 Search Project or Client")

        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All"] + statuses
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered["client_name"].str.contains(
                    search, case=False, na=False
                )
            ]

        if filter_status != "All":
            filtered = filtered[
                filtered["status"] == filter_status
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Edit Project
        st.subheader("✏️ Edit Project")

        project_options = {
            f"{p['name']} - {p['client_name']} (ID: {p['id']})": p["id"]
            for p in projects
        }

        selected = st.selectbox(
            "Select Project",
            list(project_options.keys()),
            key="edit_project"
        )

        selected_id = project_options[selected]

        current = fetch_data(
            "SELECT * FROM projects WHERE id = ?",
            (selected_id,)
        )[0]

        current_client = next(
            (
                key for key, value in client_options.items()
                if value == current["client_id"]
            ),
            list(client_options.keys())[0]
        )

        with st.form("edit_project_form"):

            edit_name = st.text_input(
                "Project Name",
                value=current["name"]
            )

            edit_client = st.selectbox(
                "Client",
                list(client_options.keys()),
                index=list(client_options.keys()).index(current_client)
            )

            edit_description = st.text_area(
                "Description",
                value=current["description"] or ""
            )

            edit_status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(current["status"])
                if current["status"] in statuses else 0
            )

            col1, col2 = st.columns(2)

            with col1:
                edit_progress = st.slider(
                    "Progress (%)",
                    0, 100,
                    int(current["progress"] or 0)
                )

                edit_start = st.date_input(
                    "Start Date",
                    value=date.fromisoformat(current["start_date"])
                )

            with col2:
                edit_deadline = st.date_input(
                    "Deadline",
                    value=date.fromisoformat(current["deadline"])
                )

                edit_budget = st.number_input(
                    "Budget",
                    min_value=0.0,
                    value=float(current["budget"] or 0),
                    step=1000.0
                )

            update = st.form_submit_button("Update Project")

            if update:

                if not edit_name.strip():
                    st.error("Project name is required.")

                elif edit_deadline < edit_start:
                    st.error("Deadline cannot be before start date.")

                else:
                    execute_query(
                        """
                        UPDATE projects
                        SET name = ?, client_id = ?, description = ?,
                            status = ?, progress = ?, start_date = ?,
                            deadline = ?, budget = ?
                        WHERE id = ?
                        """,
                        (
                            edit_name.strip(),
                            client_options[edit_client],
                            edit_description,
                            edit_status,
                            edit_progress,
                            str(edit_start),
                            str(edit_deadline),
                            edit_budget,
                            selected_id
                        )
                    )

                    st.success("Project updated successfully!")
                    st.rerun()

        st.markdown("---")

        # Delete Project
        st.subheader("🗑️ Delete Project")

        delete_option = st.selectbox(
            "Select Project to Delete",
            list(project_options.keys()),
            key="delete_project"
        )

        if st.button("Delete Selected Project"):

            delete_id = project_options[delete_option]

            execute_query(
                "DELETE FROM projects WHERE id = ?",
                (delete_id,)
            )

            st.success("Project deleted successfully!")
            st.rerun()

    else:
        st.info("No projects available. Create your first project.")
