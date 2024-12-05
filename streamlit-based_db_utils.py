import psycopg2
from psycopg2.extras import execute_values
import streamlit as st

def get_db_connection():
    #["postgres"], ["vukoz"]
    role = "postgres"
    try:
        conn = psycopg2.connect(
            host=st.secrets[role]["DB_HOST"],
            port=st.secrets[role]["DB_PORT"],
            dbname=st.secrets[role]["DB_NAME"],
            user=st.secrets[role]["DB_USER"],
            password=st.secrets[role]["DB_PASSWORD"]
        )
        print("Connection to the database was successful!")
        return conn
    except Exception as e:
        print("An error occurred while connecting to the database:", str(e))
        return None
    
def do_query(query):
    conn = get_db_connection()
    if conn is None:
        st.error("Database connection failed.")
        return None  # If connection fails, return None

    try:
        # Execute query and fetch results
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None
    finally:
        cur.close()
        conn.close()


from psycopg2.extras import execute_values
import json

def insert_chunks_to_db(chunk):
    """
    Inserts chunked data with embeddings and metadata into PostgreSQL.
    Args:
        chunked_data (list): List of dictionaries with 'text', 'embedding', and 'metadata'.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # SQL query for inserting chunks
    query = """
        INSERT INTO chunks (text, embedding, chapter, paragraph, page_number)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(
        query,
        (
        chunk["text"],
        chunk["embedding"].tolist(),  
        json.dumps({  # Construct the JSON for the chapter field
            "id": chunk["metadata"].get("chapter_id"),
            "name": chunk["metadata"].get("chapter_name")
        }),
        json.dumps({  # Construct the JSON for the paragraph field
            "id": chunk["metadata"].get("paragraph_id"),
            "name": chunk["metadata"].get("paragraph_name")
        }),
        int(chunk["metadata"].get("page_number", 1)),   
        ) 
    )


    # Execute batch insert with execute_values
    conn.commit()
    cur.close()
    conn.close()


def fetch_chunks_from_db(query):
    """
    Fetches chunks and metadata from the database for a specific query.
    Args:
        query (str): Search query text.
    Returns:
        list: Retrieved records.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text, embedding, chapter_id, chapter_name, paragraph_id, page_number FROM chunks")
    rows = cur.fetchall()
    return rows
