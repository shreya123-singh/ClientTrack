import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_clients():

    st.title("👥 Client Management")
    st.write("Manage your clients and their information.")
    st.markdown("---")

    # Add Client Form
    st.subheader("➕ Add New Client")

    with st.form("add_client_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Client Name *")
            company = st.text_input("Company Name")
            email = st.text_input("Email Address")

        with col2:
            phone = st.text_input("Phone Number")
            status = st.selectbox(
                "Client Status",
                ["Active", "Inactive", "Completed"]
            )

        submitted = st.form_submit_button("Save Client")

        if submitted:
            if not name.strip():
                st.error("Client name is required.")

            else:
                execute_query(
                    """
                    INSERT INTO clients
                    (name, company, email, phone, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        company,
                        email,
                        phone,
                        status
                    )
                )

                st.success("Client added successfully!")
                st.rerun()

    st.markdown("---")

    # Display Clients
    st.subheader("📋 All Clients")

    clients = fetch_data("SELECT * FROM clients ORDER BY id DESC")

    if clients:

        client_df = pd.DataFrame([dict(row) for row in clients])

        # Search
        search = st.text_input(
            "🔍 Search by client name or company"
        )

        if search:
            mask = (
                client_df["name"].str.contains(
                    search, case=False, na=False
                )
                |
                client_df["company"].str.contains(
                    search, case=False, na=False
                )
            )

            client_df = client_df[mask]

        st.dataframe(
            client_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Showing {len(client_df)} client(s)")

        st.markdown("---")

        # Edit Client
        st.subheader("✏️ Edit Client")

        all_clients = fetch_data(
            "SELECT id, name FROM clients ORDER BY id DESC"
        )

        client_options = {
            f"{client['name']} (ID: {client['id']})": client["id"]
            for client in all_clients
        }

        selected_client = st.selectbox(
            "Select client to edit",
            list(client_options.keys()),
            key="edit_client_select"
        )

        selected_id = client_options[selected_client]

        selected_data = fetch_data(
            "SELECT * FROM clients WHERE id = ?",
            (selected_id,)
        )[0]

        with st.form("edit_client_form"):

            edit_name = st.text_input(
                "Client Name",
                value=selected_data["name"]
            )

            edit_company = st.text_input(
                "Company Name",
                value=selected_data["company"] or ""
            )

            edit_email = st.text_input(
                "Email",
                value=selected_data["email"] or ""
            )

            edit_phone = st.text_input(
                "Phone",
                value=selected_data["phone"] or ""
            )

            statuses = ["Active", "Inactive", "Completed"]

            current_status = selected_data["status"]

            edit_status = st.selectbox(
                "Status",
                statuses,
                index=(
                    statuses.index(current_status)
                    if current_status in statuses else 0
                )
            )

            update_button = st.form_submit_button("Update Client")

            if update_button:

                if not edit_name.strip():
                    st.error("Client name is required.")

                else:
                    execute_query(
                        """
                        UPDATE clients
                        SET name = ?, company = ?, email = ?,
                            phone = ?, status = ?
                        WHERE id = ?
                        """,
                        (
                            edit_name.strip(),
                            edit_company,
                            edit_email,
                            edit_phone,
                            edit_status,
                            selected_id
                        )
                    )

                    st.success("Client updated successfully!")
                    st.rerun()

        st.markdown("---")

        # Delete Client
        st.subheader("🗑️ Delete Client")

        delete_client = st.selectbox(
            "Select client to delete",
            list(client_options.keys()),
            key="delete_client_select"
        )

        if st.button("Delete Selected Client", type="secondary"):

            delete_id = client_options[delete_client]

            execute_query(
                "DELETE FROM clients WHERE id = ?",
                (delete_id,)
            )

            st.success("Client deleted successfully!")
            st.rerun()

    else:
        st.info("No clients found. Add your first client above.")