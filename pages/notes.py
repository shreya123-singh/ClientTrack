
import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_notes():

    st.title("📝 Notes Management")
    st.write("Store and manage important business information.")
    st.markdown("---")

    notes = fetch_data("""
        SELECT * FROM notes
        ORDER BY created_at DESC
    """)

    # Add Note
    st.subheader("➕ Create New Note")

    with st.form("add_note_form", clear_on_submit=True):

        title = st.text_input("Note Title *")
        content = st.text_area(
            "Note Details *",
            placeholder="Write your important notes here..."
        )

        submitted = st.form_submit_button("Save Note")

        if submitted:

            if not title.strip() or not content.strip():
                st.error("Please enter both title and note details.")

            else:
                execute_query(
                    """
                    INSERT INTO notes (title, content)
                    VALUES (?, ?)
                    """,
                    (title.strip(), content.strip())
                )

                st.success("Note saved successfully!")
                st.rerun()

    st.markdown("---")

    # Notes Summary
    st.subheader("📊 Notes Overview")

    c1, c2 = st.columns(2)

    c1.metric("Total Notes", len(notes))

    if notes:
        latest_note = notes[0]["created_at"]
    else:
        latest_note = "No notes yet"

    c2.metric("Latest Note", latest_note)

    st.markdown("---")

    # Display Notes
    st.subheader("📋 All Notes")

    if notes:

        search = st.text_input("🔍 Search Notes by Title or Content")

        filtered_notes = [
            n for n in notes
            if search.lower() in (
                (n["title"] or "") + " " + (n["content"] or "")
            ).lower()
        ]

        if filtered_notes:

            for note in filtered_notes:

                with st.expander(
                    f"📌 {note['title']} | {note['created_at']}"
                ):

                    st.write(note["content"])

                    st.caption(f"Note ID: {note['id']}")

        else:
            st.info("No matching notes found.")

        st.markdown("---")

        # Edit Note
        st.subheader("✏️ Edit Note")

        note_options = {
            f"{n['title']} (ID: {n['id']})": n["id"]
            for n in notes
        }

        selected_note = st.selectbox(
            "Select Note to Edit",
            list(note_options.keys()),
            key="edit_note"
        )

        selected_id = note_options[selected_note]

        current = fetch_data(
            "SELECT * FROM notes WHERE id = ?",
            (selected_id,)
        )[0]

        with st.form("edit_note_form"):

            edit_title = st.text_input(
                "Note Title",
                value=current["title"]
            )

            edit_content = st.text_area(
                "Note Details",
                value=current["content"] or ""
            )

            update = st.form_submit_button("Update Note")

            if update:

                if not edit_title.strip() or not edit_content.strip():
                    st.error("Title and content are required.")

                else:
                    execute_query(
                        """
                        UPDATE notes
                        SET title = ?, content = ?
                        WHERE id = ?
                        """,
                        (
                            edit_title.strip(),
                            edit_content.strip(),
                            selected_id
                        )
                    )

                    st.success("Note updated successfully!")
                    st.rerun()

        st.markdown("---")

        # Delete Note
        st.subheader("🗑️ Delete Note")

        delete_note = st.selectbox(
            "Select Note to Delete",
            list(note_options.keys()),
            key="delete_note"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this note."
        )

        if st.button("Delete Selected Note"):

            if confirm_delete:

                delete_id = note_options[delete_note]

                execute_query(
                    "DELETE FROM notes WHERE id = ?",
                    (delete_id,)
                )

                st.success("Note deleted successfully!")
                st.rerun()

            else:
                st.warning("Please confirm before deleting.")

    else:
        st.info("No notes available. Create your first note.")
