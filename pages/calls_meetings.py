import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_calls_meetings():

    st.title("📞 Calls & Meetings")
    st.write("Schedule and manage client calls and meetings.")
    st.markdown("---")

    # Get clients
    clients = fetch_data("SELECT id, name FROM clients ORDER BY name")

    if not clients:
        st.warning("Please add a client first in the Clients module.")

    else:

        client_options = {
            f"{client['name']} (ID: {client['id']})": client['id']
            for client in clients
        }

        # Schedule Call or Meeting
        st.subheader("➕ Schedule New Call / Meeting")

        with st.form("meeting_form", clear_on_submit=True):

            title = st.text_input("Call / Meeting Title *")

            client_name = st.selectbox(
                "Select Client",
                list(client_options.keys())
            )

            col1, col2 = st.columns(2)

            with col1:
                meeting_type = st.selectbox(
                    "Type",
                    ["Call", "Online Meeting", "Physical Meeting"]
                )

                meeting_date = st.date_input("Date")

            with col2:
                meeting_time = st.time_input("Time")
                status = st.selectbox(
                    "Status",
                    ["Scheduled", "Completed", "Cancelled"]
                )

            notes = st.text_area("Meeting Notes")

            submitted = st.form_submit_button("Save Schedule")

            if submitted:

                if not title.strip():
                    st.error("Please enter a meeting title.")

                else:

                    execute_query(
                        """
                        INSERT INTO meetings
                        (client_id, title, meeting_type, meeting_date,
                         meeting_time, notes, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            client_options[client_name],
                            title.strip(),
                            meeting_type,
                            str(meeting_date),
                            str(meeting_time),
                            notes,
                            status
                        )
                    )

                    st.success("Call / Meeting scheduled successfully!")
                    st.rerun()

    st.markdown("---")

    # Display Meetings
    st.subheader("📋 All Calls & Meetings")

    meetings = fetch_data("""
        SELECT meetings.*, clients.name AS client_name
        FROM meetings
        LEFT JOIN clients ON meetings.client_id = clients.id
        ORDER BY meeting_date DESC, meeting_time DESC
    """)

    if meetings:

        df = pd.DataFrame([dict(row) for row in meetings])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Update Meeting
        st.subheader("✏️ Update Meeting Status")

        meeting_options = {
            f"{m['title']} - {m['client_name']} (ID: {m['id']})": m['id']
            for m in meetings
        }

        selected = st.selectbox(
            "Select Meeting",
            list(meeting_options.keys())
        )

        meeting_id = meeting_options[selected]

        current = fetch_data(
            "SELECT * FROM meetings WHERE id = ?",
            (meeting_id,)
        )[0]

        status_options = ["Scheduled", "Completed", "Cancelled"]

        current_status = current["status"]

        with st.form("update_meeting_form"):

            new_status = st.selectbox(
                "New Status",
                status_options,
                index=status_options.index(current_status)
            )

            update = st.form_submit_button("Update Status")

            if update:

                execute_query(
                    "UPDATE meetings SET status = ? WHERE id = ?",
                    (new_status, meeting_id)
                )

                st.success("Meeting status updated!")
                st.rerun()

        st.markdown("---")

        # Delete Meeting
        st.subheader("🗑️ Delete Meeting")

        if st.button("Delete Selected Meeting"):
            execute_query(
                "DELETE FROM meetings WHERE id = ?",
                (meeting_id,)
            )

            st.success("Meeting deleted successfully!")
            st.rerun()

    else:
        st.info("No calls or meetings scheduled yet.")