import streamlit as st
import re
import urllib.parse
from google import genai
def reset_form():
    st.session_state.playlist_result = None
    st.session_state.playlist_meta = None
    st.session_state.songs = []
    st.session_state.user_mind_input = ""
def spotify_search_link(song_name):
     query=urllib.parse.quote(song_name)
     return f"https://open.spotify.com/search/{query}"
def build_shareable_text(playlist_text,mood,genre):
        return f"🎧 MoodTunes AI - {mood} | {genre} \n\n{playlist_text}"
def extract_songs(text):
    match=re.search(r"🎵 Songs:\s*(.*?)(?:💌|$)", text, re.DOTALL)
    if not match:
         return []
    songs=[]
    for line in match.group(1).strip().split("\n"):
        line=re.sub(r"^\d+\.\s*", "", line.strip())
        if line:
             songs.append(line)
    return songs
st.set_page_config(page_title="MoodTunes AI", page_icon="🎧")
if "playlist_result" not in st.session_state:
    st.session_state.playlist_result = None
    st.session_state.playlist_count = 0
    st.session_state.playlist_meta = None
    st.session_state.mood_history = []
st.title("🎧 MoodTunes AI")
st.header("Music for every emotion")
st.write("🎵 Select your mood, tell us what's on your mind, and let MoodTunes create your vibe.")

with st.sidebar:
    st.header("🎧 About MoodTunes AI")

    st.markdown("""
    **MoodTunes AI** is your personal music companion that transforms emotions into curated playlists.

    ### ✨ Features
    - 🎵 Personalized song recommendations
    - 💌 Supportive messages
    - ✨ Motivational quotes
    - 🌱 Self-care suggestions

    ### 🛠 Tech Stack
    - Python
    - Streamlit
    - Gemini AI

    ### 🎯 Goal
    To help users discover music that resonates with their emotions and promotes well-being.
    """)

    st.divider()
    

    st.caption("Made with 🎶 and ☕ by Shagun")
    st.caption("Built for ELEVATE 2026")
    st.metric("Playlists Generated",st.session_state.playlist_count)
    if st.session_state.get("mood_history"):
             st.divider()
             st.subheader("🫠 Your Mood Today")
             for mood in st.session_state.mood_history:
                    st.write(mood)
    st.divider()
    st.markdown("""###  Future Scope
• Verified Spotify catalog matching

• Mood Journal

• Weekly Insights

• Calendar Tracking

• Persistent history across sessions""")
    st.divider()
    st.caption("💡 MoodTunes AI offers supportive suggestions and music inspiration. It is not a substitute for professional mental health support.")
status=st.radio("Select your mood:",["🙂 Happy",
"🙁 Sad",
"🤯 Stressed",
"😔 Lonely",
"😎 Excited",
"💔 Heartbroken",
"🎧 Study Mode"])
user_mind=st.text_input("What's on your mind ??",placeholder="Had a great day",max_chars=200,key="user_mind_input",)
option = st.selectbox(
    "What kind of music do you want?",
    ('Bollywood', 'Pop', 'Indie', 'Lo-fi', 'K-pop', 'Classical', 'Surprise Me')
)
col1, col2 = st.columns(2)
with col1:
    button_clicked = st.button("🎵 Generate My Vibe")
with col2:
    st.button("🔄 Reset", on_click=reset_form)
if button_clicked:
    if not user_mind:
        st.warning("💭 Tell me what's on your mind first!")
    elif "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ No API key configured. Add GOOGLE_API_KEY to your Streamlit secrets.")
    else:
        prompt = f"""
You are MoodTunes AI, an empathetic music curator.
Mood: {status}
Thoughts: {user_mind}
Genre: {option}
Generate only real songs available on Spotify.
Prefer popular and recognizable tracks.
Recommendations should feel emotionally aligned with the user's current feelings.
Keep the tone warm, supportive, and non-judgmental.
Generate in this exact format:
🎧 Playlist Name:
...
🎵 Songs:
1.
2.
3.
4.
5.
💌 Supportive Message:
...
🎭 Music Personality:
...
✨ Motivational Quote:
...
🌱 Self-Care Activity:
...
"""
        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            with st.spinner("✨ Building your perfect playlist..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                )
            if response.text:
                st.session_state.playlist_result = response.text
                st.session_state.playlist_count +=1
                st.session_state.playlist_meta = (status, option)
                st.session_state.songs=extract_songs(response.text)
                if status not in st.session_state.mood_history:
                      st.session_state.mood_history.append(status)
                      st.session_state.mood_history = st.session_state.mood_history[-5:]
            else:
                st.warning("Got an empty response from the AI — try again?")
                st.session_state.playlist_result = None
        except Exception as e:
            st.error(f"😕 Something went wrong generating your playlist: {e}")
            st.session_state.playlist_result = None
 
# Display whatever the last successful result was (persists across reruns)
if st.session_state.playlist_result:
    mood_shown, genre_shown = st.session_state.playlist_meta
    badges = {
    "🙂 Happy": "🌞 Sunshine Soul",
    "🙁 Sad": "🌧️ Healing Heart",
    "🤯 Stressed": "🧘 Calm Seeker",
    "😔 Lonely": "🌙 Midnight Dreamer",
    "😎 Excited": "⚡ Main Character Energy",
    "💔 Heartbroken": "💔 Healing Journey",
    "🎧 Study Mode": "📚 Focus Architect"}
    st.success(f"🎭 Music Personality Badge: {badges.get(mood_shown,'🎶 Unique Listener')}")
    st.info(f"Current Mood: {mood_shown} | Genre: {genre_shown}")
    st.subheader("✨ Your Personalized Vibe")
    with st.expander("🎧 Reveal My Mood Mix", expanded=True):
        formatted_text = st.session_state.playlist_result.replace("\n", "\n\n")
        st.markdown(formatted_text)
    if st.session_state.get("songs"):
        st.subheader("🎵 Listen on Spotify")
        for song in st.session_state.songs:
            st.markdown(f"- [{song}]({spotify_search_link(song)})")
    share_text=build_shareable_text(st.session_state.playlist_result,mood_shown,genre_shown)
    st.download_button("📥 Download My Vibe",data=share_text,file_name="my_moodtune_vibe.txt",mime="text/plain",)
elif not button_clicked:
    st.info("🎵 Your personalized soundtrack is waiting. Select a mood and let's begin!")
    