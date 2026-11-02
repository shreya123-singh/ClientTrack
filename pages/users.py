
import streamlit as st
import pandas as pd
import sqlite3

from database.db import fetch_data, execute_query


def show_users():

    st.title("👥 Users & Roles Management")
    st.write("Manage system users and assign their roles.")
    st.markdown("---")

    users = fetch_data("""
        SELECT * FROM users
        ORDER BY id DESC
    """)

    roles = ["Admin", "Manager", "Staff"]

    # Add User
    st.subheader("➕ Add New User")

    with st.form("add_user_form", clear_on_submit=True):

        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")

        role = st.selectbox(
            "Select Role",
            roles
        )

        submitted = st.form_submit_button("Add User")

        if submitted:

            if not name.strip() or not email.strip():
                st.error("Please enter both name and email.")

            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")

            else:
                try:
                    execute_query(
                        """
                        INSERT INTO users (name, email, role)
                        VALUES (?, ?, ?)
                        """,
                        (
                            name.strip(),
                            email.strip().lower(),
                            role
                        )
                    )

                    st.success("User added successfully!")
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error("This email address is already registered.")

    st.markdown("---")

    # User Summary
    st.subheader("📊 User Overview")

    total_users = len(users)

    admin_count = sum(1 for u in users if u["role"] == "Admin")
    manager_count = sum(1 for u in users if u["role"] == "Manager")
    staff_count = sum(1 for u in users if u["role"] == "Staff")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Users", total_users)
    c2.metric("Admins", admin_count)
    c3.metric("Managers", manager_count)
    c4.metric("Staff", staff_count)

    st.markdown("---")

    # Display Users
    st.subheader("📋 All System Users")

    if users:

        df = pd.DataFrame([dict(u) for u in users])

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input("🔍 Search by Name or Email")

        with col2:
            role_filter = st.selectbox(
                "Filter by Role",
                ["All"] + roles
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered["email"].str.contains(
                    search, case=False, na=False
                )
            ]

        if role_filter != "All":
            filtered = filtered[
                filtered["role"] == role_filter
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Edit User
        st.subheader("✏️ Edit User")

        user_options = {
            f"{u['name']} - {u['email']} (ID: {u['id']})": u["id"]
            for u in users
        }

        selected = st.selectbox(
            "Select User to Edit",
            list(user_options.keys()),
            key="edit_user"
        )

        selected_id = user_options[selected]

        current = fetch_data(
            "SELECT * FROM users WHERE id = ?",
            (selected_id,)
        )[0]

        with st.form("edit_user_form"):

            edit_name = st.text_input(
                "Full Name",
                value=current["name"]
            )

            edit_email = st.text_input(
                "Email Address",
                value=current["email"] or ""
            )

            edit_role = st.selectbox(
                "Role",
                roles,
                index=roles.index(current["role"])
                if current["role"] in roles else 0
            )

            update = st.form_submit_button("Update User")

            if update:

                if not edit_name.strip() or not edit_email.strip():
                    st.error("Name and email are required.")

                elif "@" not in edit_email or "." not in edit_email.split("@")[-1]:
                    st.error("Please enter a valid email address.")

                else:
                    try:
                        execute_query(
                            """
                            UPDATE users
                            SET name = ?, email = ?, role = ?
                            WHERE id = ?
                            """,
                            (
                                edit_name.strip(),
                                edit_email.strip().lower(),
                                edit_role,
                                selected_id
                            )
                        )

                        st.success("User updated successfully!")
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.error("This email address is already used by another user.")

        st.markdown("---")

        # Delete User
        st.subheader("🗑️ Delete User")

        delete_option = st.selectbox(
            "Select User to Delete",
            list(user_options.keys()),
            key="delete_user"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this user."
        )

        if st.button("Delete Selected User"):

            if confirm_delete:

                delete_id = user_options[delete_option]

                execute_query(
                    "DELETE FROM users WHERE id = ?",
                    (delete_id,)
                )

                st.success("User deleted successfully!")
                st.rerun()

            else:
                st.warning("Please confirm before deleting.")

    else:
        st.info("No users available. Add your first system user.")
