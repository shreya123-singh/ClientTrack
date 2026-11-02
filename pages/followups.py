import streamlit as st
import pandas as pd
from datetime import date, datetime

from database.db import fetch_data, execute_query


def show_followups():

    st.title("📌 Follow-Up Management")
    st.write("Track client follow-ups and never miss an important task.")
    st.markdown("---")

    # Fetch clients
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

    # Fetch follow-ups
    followups = fetch_data("""
        SELECT followups.*, clients.name AS client_name
        FROM followups
        LEFT JOIN clients ON followups.client_id = clients.id
        ORDER BY followups.followup_date DESC, followups.followup_time DESC
    """)

    # Add Follow-Up
    st.subheader("➕ Schedule New Follow-Up")

    with st.form("add_followup_form", clear_on_submit=True):

        subject = st.text_input("Follow-Up Subject *")

        client = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        col1, col2 = st.columns(2)

        with col1:
            method = st.selectbox(
                "Communication Method",
                ["Phone", "WhatsApp", "Email", "In-Person", "Other"]
            )

            followup_date = st.date_input(
                "Follow-Up Date",
                value=date.today()
            )

        with col2:
            followup_time = st.time_input("Follow-Up Time")

            status = st.selectbox(
                "Status",
                ["Pending", "Done", "Cancelled"]
            )

        notes = st.text_area("Follow-Up Notes")

        submitted = st.form_submit_button("Save Follow-Up")

        if submitted:

            if not subject.strip():
                st.error("Please enter a follow-up subject.")

            else:
                execute_query(
                    """
                    INSERT INTO followups
                    (client_id, subject, method, followup_date,
                     followup_time, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client_options[client],
                        subject.strip(),
                        method,
                        str(followup_date),
                        str(followup_time),
                        status,
                        notes
                    )
                )

                st.success("Follow-up scheduled successfully!")
                st.rerun()

    st.markdown("---")

    # Follow-Up Summary
    st.subheader("📊 Follow-Up Overview")

    pending = sum(1 for f in followups if f["status"] == "Pending")
    done = sum(1 for f in followups if f["status"] == "Done")
    cancelled = sum(1 for f in followups if f["status"] == "Cancelled")

    today = date.today()

    overdue = sum(
        1 for f in followups
        if f["status"] == "Pending"
        and (
            f["followup_date"] < str(today)
            or (
                f["followup_date"] == str(today)
                and f["followup_time"] < datetime.now().strftime("%H:%M:%S")
            )
        )
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Follow-Ups", len(followups))
    c2.metric("Pending", pending)
    c3.metric("Completed", done)
    c4.metric("Overdue", overdue)

    st.markdown("---")

    # Display Follow-Ups
    st.subheader("📋 Follow-Up Records")

    if followups:

        df = pd.DataFrame([dict(f) for f in followups])

        # Add overdue information
        df["Reminder"] = df.apply(
            lambda row:
            "Overdue"
            if row["status"] == "Pending"
            and (
                row["followup_date"] < str(today)
                or (
                    row["followup_date"] == str(today)
                    and row["followup_time"] < datetime.now().strftime("%H:%M:%S")
                )
            )
            else "Upcoming"
            if row["status"] == "Pending"
            else row["status"],
            axis=1
        )

        # Search and filters
        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input("🔍 Search by subject or client")

        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Pending", "Done", "Cancelled"]
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["subject"].str.contains(
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

        # Edit Follow-Up
        st.subheader("✏️ Edit Follow-Up")

        followup_options = {
            f"{f['subject']} - {f['client_name']} (ID: {f['id']})": f["id"]
            for f in followups
        }

        selected = st.selectbox(
            "Select Follow-Up to Edit",
            list(followup_options.keys()),
            key="edit_followup"
        )

        selected_id = followup_options[selected]

        current = fetch_data(
            "SELECT * FROM followups WHERE id = ?",
            (selected_id,)
        )[0]

        methods = ["Phone", "WhatsApp", "Email", "In-Person", "Other"]
        statuses = ["Pending", "Done", "Cancelled"]

        with st.form("edit_followup_form"):

            edit_subject = st.text_input(
                "Subject",
                value=current["subject"]
            )

            current_client = next(
                (
                    key for key, value in client_options.items()
                    if value == current["client_id"]
                ),
                list(client_options.keys())[0]
            )

            edit_client = st.selectbox(
                "Client",
                list(client_options.keys()),
                index=list(client_options.keys()).index(current_client)
            )

            edit_method = st.selectbox(
                "Communication Method",
                methods,
                index=methods.index(current["method"])
                if current["method"] in methods else 0
            )

            edit_date = st.date_input(
                "Follow-Up Date",
                value=date.fromisoformat(current["followup_date"])
            )

            edit_time = st.time_input(
                "Follow-Up Time",
                value=datetime.strptime(
                    current["followup_time"], "%H:%M:%S"
                ).time()
                if len(current["followup_time"]) == 8
                else datetime.strptime(
                    current["followup_time"], "%H:%M"
                ).time()
            )

            edit_status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(current["status"])
                if current["status"] in statuses else 0
            )

            edit_notes = st.text_area(
                "Notes",
                value=current["notes"] or ""
            )

            update = st.form_submit_button("Update Follow-Up")

            if update:

                if not edit_subject.strip():
                    st.error("Subject is required.")

                else:
                    execute_query(
                        """
                        UPDATE followups
                        SET client_id = ?, subject = ?, method = ?,
                            followup_date = ?, followup_time = ?,
                            status = ?, notes = ?
                        WHERE id = ?
                        """,
                        (
                            client_options[edit_client],
                            edit_subject.strip(),
                            edit_method,
                            str(edit_date),
                            str(edit_time),
                            edit_status,
                            edit_notes,
                            selected_id
                        )
                    )

                    st.success("Follow-up updated successfully!")
                    st.rerun()

        st.markdown("---")

        # Delete Follow-Up
        st.subheader("🗑️ Delete Follow-Up")

        delete_option = st.selectbox(
            "Select Follow-Up to Delete",
            list(followup_options.keys()),
            key="delete_followup"
        )

        if st.button("Delete Selected Follow-Up"):

            delete_id = followup_options[delete_option]

            execute_query(
                "DELETE FROM followups WHERE id = ?",
                (delete_id,)
            )

            st.success("Follow-up deleted successfully!")
            st.rerun()

    else:
        st.info("No follow-ups available. Schedule your first follow-up.")