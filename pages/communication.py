
import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_communication_log():

    st.title("💬 Communication Log")
    st.write("Maintain a complete history of client communication.")
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

    records = fetch_data("""
        SELECT communication_log.*, clients.name AS client_name
        FROM communication_log
        LEFT JOIN clients
        ON communication_log.client_id = clients.id
        ORDER BY communication_log.communication_date DESC,
                 communication_log.id DESC
    """)

    # Add Communication
    st.subheader("➕ Add Communication Record")

    with st.form("add_communication_form", clear_on_submit=True):

        client = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        communication_type = st.selectbox(
            "Communication Type",
            ["Call", "Email", "WhatsApp", "Meeting", "Other"]
        )

        subject = st.text_input("Subject *")

        communication_date = st.date_input(
            "Communication Date",
            value=date.today()
        )

        details = st.text_area(
            "Communication Details *",
            placeholder="Enter discussion details, client feedback or important points..."
        )

        submitted = st.form_submit_button("Save Communication")

        if submitted:

            if not subject.strip() or not details.strip():
                st.error("Please enter both subject and details.")

            else:
                execute_query(
                    """
                    INSERT INTO communication_log
                    (client_id, communication_type, subject,
                     details, communication_date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        client_options[client],
                        communication_type,
                        subject.strip(),
                        details.strip(),
                        str(communication_date)
                    )
                )

                st.success("Communication record saved successfully!")
                st.rerun()

    st.markdown("---")

    # Summary
    st.subheader("📊 Communication Overview")

    total = len(records)

    call_count = sum(
        1 for r in records if r["communication_type"] == "Call"
    )

    email_count = sum(
        1 for r in records if r["communication_type"] == "Email"
    )

    meeting_count = sum(
        1 for r in records if r["communication_type"] == "Meeting"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", total)
    c2.metric("Calls", call_count)
    c3.metric("Emails", email_count)
    c4.metric("Meetings", meeting_count)

    st.markdown("---")

    # Display Records
    st.subheader("📋 Communication History")

    if records:

        df = pd.DataFrame([dict(r) for r in records])

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input(
                "🔍 Search by Client or Subject"
            )

        with col2:
            type_filter = st.selectbox(
                "Filter by Communication Type",
                [
                    "All",
                    "Call",
                    "Email",
                    "WhatsApp",
                    "Meeting",
                    "Other"
                ]
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["client_name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered["subject"].str.contains(
                    search, case=False, na=False
                )
            ]

        if type_filter != "All":
            filtered = filtered[
                filtered["communication_type"] == type_filter
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Edit Record
        st.subheader("✏️ Edit Communication Record")

        record_options = {
            f"{r['subject']} - {r['client_name']} (ID: {r['id']})":
            r["id"]
            for r in records
        }

        selected = st.selectbox(
            "Select Record to Edit",
            list(record_options.keys()),
            key="edit_communication"
        )

        selected_id = record_options[selected]

        current = fetch_data(
            "SELECT * FROM communication_log WHERE id = ?",
            (selected_id,)
        )[0]

        types = ["Call", "Email", "WhatsApp", "Meeting", "Other"]

        current_client = next(
            (
                key for key, value in client_options.items()
                if value == current["client_id"]
            ),
            list(client_options.keys())[0]
        )

        with st.form("edit_communication_form"):

            edit_client = st.selectbox(
                "Client",
                list(client_options.keys()),
                index=list(client_options.keys()).index(current_client)
            )

            edit_type = st.selectbox(
                "Communication Type",
                types,
                index=types.index(current["communication_type"])
                if current["communication_type"] in types else 0
            )

            edit_subject = st.text_input(
                "Subject",
                value=current["subject"]
            )

            edit_date = st.date_input(
                "Communication Date",
                value=date.fromisoformat(
                    current["communication_date"]
                )
            )

            edit_details = st.text_area(
                "Details",
                value=current["details"] or ""
            )

            update = st.form_submit_button("Update Record")

            if update:

                if not edit_subject.strip() or not edit_details.strip():
                    st.error("Subject and details are required.")

                else:
                    execute_query(
                        """
                        UPDATE communication_log
                        SET client_id = ?, communication_type = ?,
                            subject = ?, details = ?,
                            communication_date = ?
                        WHERE id = ?
                        """,
                        (
                            client_options[edit_client],
                            edit_type,
                            edit_subject.strip(),
                            edit_details.strip(),
                            str(edit_date),
                            selected_id
                        )
                    )

                    st.success("Communication record updated!")
                    st.rerun()

        st.markdown("---")

        # Delete Record
        st.subheader("🗑️ Delete Communication Record")

        delete_option = st.selectbox(
            "Select Record to Delete",
            list(record_options.keys()),
            key="delete_communication"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this record."
        )

        if st.button("Delete Selected Record"):

            if confirm_delete:

                delete_id = record_options[delete_option]

                execute_query(
                    "DELETE FROM communication_log WHERE id = ?",
                    (delete_id,)
                )

                st.success("Communication record deleted!")
                st.rerun()

            else:
                st.warning("Please confirm before deleting.")

    else:
        st.info("No communication records available yet.")
