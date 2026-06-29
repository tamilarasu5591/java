import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'database.sqlite')

print("Connecting to database...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Check how many posts and comments we are deleting
cursor.execute("SELECT COUNT(*) FROM forum_comments")
comments_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM forum_posts")
posts_count = cursor.fetchone()[0]

print(f"Found {posts_count} posts and {comments_count} comments.")

# Delete all contents from forum tables
cursor.execute("DELETE FROM forum_comments")
cursor.execute("DELETE FROM forum_posts")
conn.commit()

print("All community forum posts and comments have been successfully removed!")
conn.close()
