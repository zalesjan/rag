import psycopg2
from psycopg2.extras import execute_values

DB_HOST = "cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "db9vb6ou8b23bu"
DB_USER = "ud1j9o71p17h9b"
DB_PASSWORD = "p8f4e6b9555540213adb174b18e69e1c11e0f5f7302cfdf8e3551a80677abaece"

def get_db_connection():
    #["postgres"], ["vukoz"]
    #role = "tenderix"
    try:
        # Database credentials
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Connection to the database was successful!")
        return conn
    except Exception as e:
        print("An error occurred while connecting to the database:", str(e))
        return None
    
def do_query(query):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return None  # If connection fails, return None

    try:
        # Execute query and fetch results
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    finally:
        cur.close()
        conn.close()


from psycopg2.extras import execute_values
import json

def insert_chunks_to_db(cur, chunk):
    """
    Inserts chunked data with embeddings and metadata into PostgreSQL.
    Args:
        chunked_data (list): List of dictionaries with 'text', 'embedding', and 'metadata'.
    """
    

    # SQL query for inserting chunks
    query = """
        INSERT INTO chunks (text, Název_článku, chapter, paragraph, page_number)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(
        query,
        (
        chunk["text"],
        chunk["document_metadata"]["Název článku"],
        #chunk["embedding"].tolist(),  
        json.dumps({  # Construct the JSON for the chapter field
            "id": chunk["page_metadata"].get("chapter_id"),
            "name": chunk["page_metadata"].get("chapter_name")
        }),
        json.dumps({  # Construct the JSON for the paragraph field
            "id": chunk["page_metadata"].get("paragraph_id"),
            "name": chunk["page_metadata"].get("paragraph_name")
        }),
        int(chunk["page_metadata"].get("page_number", 1)),   
        ) 
    )
    print("Insert Query:", query)
    print("Insert Values:", (
        chunk["text"],
        chunk["document_metadata"]["Název článku"],
        #chunk["embedding"].tolist(),  
        json.dumps({  # Construct the JSON for the chapter field
            "id": chunk["page_metadata"].get("chapter_id"),
            "name": chunk["page_metadata"].get("chapter_name")
        }),
        json.dumps({  # Construct the JSON for the paragraph field
            "id": chunk["page_metadata"].get("paragraph_id"),
            "name": chunk["page_metadata"].get("paragraph_name")
        }),
        int(chunk["page_metadata"].get("page_number", 1)),   
    ))

def fetch_distinct_values(column_name):
    conn = get_db_connection()
    cur = conn.cursor()
    query = f"SELECT DISTINCT {column_name} FROM chunks;"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]
    
def fetch_metadata_keys():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'chunks';")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]    

def fetch_filtered_chunks_from_db(filter_column=None, filter_values=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Dynamically construct the placeholders for the IN clause
    placeholders = ','.join(['%s'] * len(filter_values))
    query = f"SELECT embedding, text FROM chunks WHERE {filter_column} IN ({placeholders})"
    
    # Debugging: Print the actual query
    print(cur.mogrify(query, filter_values).decode("utf-8"))

    cur.execute(query, filter_values) 
    print(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_chunks_from_db():
    """
    Fetches chunks and metadata from the database for a specific query.
    Args:
        query (str): Search query text.
    Returns:
        list: Retrieved records.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, text, embedding, chapter, paragraph, page_number, Název_článku, autor_1 FROM chunks")
    rows = cur.fetchall()
    return rows
