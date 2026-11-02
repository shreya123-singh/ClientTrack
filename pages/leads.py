import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_leads():

    st.title("🎯 Leads & Pipeline")
    st.write("Track potential clients and manage your sales pipeline.")
    st.markdown("---")

    # Lead stages
    stages = [
        "New",
        "Contacted",
        "Follow-Up",
        "Requirement Discussion",
        "Proposal Sent",
        "Negotiation",
        "Converted"
    ]

    # Add New Lead
    st.subheader("➕ Add New Lead")

    with st.form("add_lead_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Lead Name *")
            company = st.text_input("Company Name")
            email = st.text_input("Email Address")

        with col2:
            phone = st.text_input("Phone Number")
            source = st.selectbox(
                "Lead Source",
                ["Website", "Social Media", "Referral", "Advertisement", "Other"]
            )
            status = st.selectbox("Lead Status", stages)

        value = st.number_input(
            "Expected Deal Value (₹)",
            min_value=0.0,
            step=1000.0
        )

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            if not name.strip():
                st.error("Lead name is required.")
            else:
                execute_query(
                    """
                    INSERT INTO leads
                    (name, company, email, phone, source, status, value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name.strip(), company, email, phone, source, status, value)
                )

                st.success("Lead added successfully!")
                st.rerun()

    st.markdown("---")

    # All Leads
    st.subheader("📋 All Leads")

    leads = fetch_data("SELECT * FROM leads ORDER BY id DESC")

    if leads:

        df = pd.DataFrame([dict(row) for row in leads])

        # Pipeline summary
        total = len(df)
        converted = len(df[df["status"] == "Converted"])
        conversion = (converted / total * 100) if total else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Leads", total)
        col2.metric("Converted Leads", converted)
        col3.metric("Conversion Rate", f"{conversion:.1f}%")

        st.markdown("---")

        # Search and filter
        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input("🔍 Search lead")

        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All"] + stages
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["name"].str.contains(search, case=False, na=False)
                | filtered["company"].str.contains(search, case=False, na=False)
            ]

        if filter_status != "All":
            filtered = filtered[filtered["status"] == filter_status]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Edit lead
        st.subheader("✏️ Update Lead")

        lead_options = {
            f"{lead['name']} (ID: {lead['id']})": lead["id"]
            for lead in leads
        }

        selected = st.selectbox(
            "Select lead to update",
            list(lead_options.keys()),
            key="edit_lead"
        )

        lead_id = lead_options[selected]

        lead_data = fetch_data(
            "SELECT * FROM leads WHERE id = ?",
            (lead_id,)
        )[0]

        with st.form("update_lead_form"):

            edit_name = st.text_input("Lead Name", value=lead_data["name"])
            edit_company = st.text_input(
                "Company",
                value=lead_data["company"] or ""
            )
            edit_email = st.text_input(
                "Email",
                value=lead_data["email"] or ""
            )
            edit_phone = st.text_input(
                "Phone",
                value=lead_data["phone"] or ""
            )
            edit_source = st.selectbox(
                "Source",
                ["Website", "Social Media", "Referral", "Advertisement", "Other"],
                index=(
                    ["Website", "Social Media", "Referral", "Advertisement", "Other"]
                    .index(lead_data["source"])
                    if lead_data["source"] in
                    ["Website", "Social Media", "Referral", "Advertisement", "Other"]
                    else 0
                )
            )
            edit_status = st.selectbox(
                "Status",
                stages,
                index=stages.index(lead_data["status"])
            )
            edit_value = st.number_input(
                "Expected Deal Value (₹)",
                min_value=0.0,
                value=float(lead_data["value"] or 0),
                step=1000.0
            )

            update = st.form_submit_button("Update Lead")

            if update:
                if not edit_name.strip():
                    st.error("Lead name is required.")
                else:
                    execute_query(
                        """
                        UPDATE leads
                        SET name=?, company=?, email=?, phone=?,
                            source=?, status=?, value=?
                        WHERE id=?
                        """,
                        (
                            edit_name.strip(), edit_company, edit_email,
                            edit_phone, edit_source, edit_status,
                            edit_value, lead_id
                        )
                    )
                    st.success("Lead updated successfully!")
                    st.rerun()

        st.markdown("---")

        # Delete lead
        st.subheader("🗑️ Delete Lead")

        delete_option = st.selectbox(
            "Select lead to delete",
            list(lead_options.keys()),
            key="delete_lead"
        )

        if st.button("Delete Selected Lead"):
            delete_id = lead_options[delete_option]

            execute_query(
                "DELETE FROM leads WHERE id=?",
                (delete_id,)
            )

            st.success("Lead deleted successfully!")
            st.rerun()

    else:
        st.info("No leads available. Add your first lead above.")