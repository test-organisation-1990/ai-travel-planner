from history.db import get_connection
import json

def save_chat(session_id: str, user_query: str, ai_response: str):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO chat_history
                (session_id, user_query, ai_response)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    session_id,
                    user_query,
                    json.dumps(ai_response)
                    
                )
            )

            # IMPORTANT: fetch while cursor is still open
            chat_id = cursor.fetchone()[0]

        conn.commit()

    return chat_id

def save_feedback(chat_id:int, session_id: str, feedback: str):

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE chat_history
                SET
                    feedback = %s
                WHERE
                    id = %s
                    AND session_id = %s
                """,
                (
                    feedback,
                    chat_id,
                    session_id
                )
            )

            updated_rows = cursor.rowcount

        conn.commit()

    return updated_rows