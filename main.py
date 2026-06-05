import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

st.title("📚 Blog AI Agent")

question = st.text_input("Ask Anything About Blogs")

if question:

    conn = sqlite3.connect("database/blogs.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, content
        FROM blogs
    """)

    rows = cursor.fetchall()

    q = question.lower()

    matched_blogs = []

    # Find relevant blogs
    for topic, content in rows:

        topic_words = topic.lower().strip()

        if topic_words in q:
            matched_blogs.append(
                f"TOPIC: {topic}\n{content}"
            )

    # If no topic matched
    if not matched_blogs:

        for topic, content in rows:

            if any(word in content.lower() for word in q.split()):
                matched_blogs.append(
                    f"TOPIC: {topic}\n{content}"
                )

    # No matching blog found
    if not matched_blogs:

        st.error("No relevant blog found in database.")

    else:

        blog_text = "\n\n".join(matched_blogs)

        prompt = f"""
You are a Blog Database Assistant.

Use ONLY the database content below.

DATABASE:

{blog_text}

QUESTION:
{question}

Rules:
1. Answer only from database content.
2. If answer is not available, say:
   Information not available in database.
3. Give direct answers.
4. If user asks for summary, summarize.
5. If user asks for author, give author only.
6. If user asks for published year, give year only.
7. If user asks for title, give title only.
"""

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

        st.subheader("Answer")
        st.write(answer)

    conn.close()