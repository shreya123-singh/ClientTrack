
import streamlit as st


def show_java_mysql_hub():

    st.title("☕ Java & MySQL Hub")
    st.write("Technical resources and project development information.")
    st.markdown("---")

    st.subheader("📚 Java Programming")

    with st.expander("Java Overview", expanded=True):
        st.write("""
        Java is an object-oriented programming language used to develop
        desktop, web and enterprise applications.

        **Important Concepts:**
        - Classes and Objects
        - Inheritance
        - Polymorphism
        - Encapsulation
        - Abstraction
        - Exception Handling
        - JDBC Connectivity
        """)

    with st.expander("Java in ClientTrack"):
        st.write("""
        Java concepts can be used to understand application development,
        object-oriented programming and database connectivity.

        ClientTrack's current application is developed using Python and
        Streamlit. Java is included here as a learning and reference section.
        """)

    st.markdown("---")

    st.subheader("🗄️ MySQL Database")

    with st.expander("MySQL Overview", expanded=True):
        st.write("""
        MySQL is a relational database management system used to store
        and manage structured information.

        **Important Concepts:**
        - Database and Tables
        - Primary Key and Foreign Key
        - SQL Queries
        - INSERT, UPDATE and DELETE
        - SELECT and WHERE
        - JOIN Operations
        - Database Relationships
        """)

    with st.expander("Database in ClientTrack"):
        st.write("""
        ClientTrack currently uses SQLite to store information such as
        clients, leads, projects, meetings, follow-ups and notes.

        SQLite provides lightweight database storage without requiring
        a separate database server.
        """)

    st.markdown("---")

    st.subheader("🔗 Useful Learning Resources")

    st.markdown(
        "- [Java Documentation](https://docs.oracle.com/en/java/)\n"
        "- [MySQL Documentation](https://dev.mysql.com/doc/)\n"
        "- [Python Documentation](https://docs.python.org/3/)\n"
        "- [Streamlit Documentation](https://docs.streamlit.io/)"
    )

    st.info(
        "This hub is an informational learning section. "
        "The actual ClientTrack application runs on Python, Streamlit and SQLite."
    )
