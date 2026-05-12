import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="GitHub Profile Analyzer", page_icon="🐙", layout="wide")
st.title("🐙 GitHub Profile Analyzer")

username = st.text_input("Enter GitHub Username:", placeholder="e.g. torvalds")

def get_github_data(username):
    base = "https://api.github.com"
    user = requests.get(f"{base}/users/{username}").json()
    repos = requests.get(f"{base}/users/{username}/repos?per_page=100").json()
    return user, repos

def score_profile(user, repos):
    score = 0
    if user.get("bio"): score += 10
    if user.get("blog"): score += 10
    if user.get("location"): score += 5
    if user.get("avatar_url"): score += 5
    score += min(user.get("public_repos", 0) * 2, 30)
    score += min(user.get("followers", 0), 20)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    score += min(total_stars, 20)
    return min(score, 100)

if username:
    with st.spinner("Fetching data..."):
        user, repos = get_github_data(username)

    if "message" in user:
        st.error("User not found! Check the username.")
    else:
        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            st.image(user["avatar_url"], width=150)

        with col2:
            st.subheader(user.get("name") or username)
            st.write(user.get("bio", "No bio available"))
            st.write(f"📍 {user.get('location', 'Location not set')}")
            st.write(f"🔗 {user.get('blog', 'No website')}")

        with col3:
            score = score_profile(user, repos)
            st.metric("Profile Score", f"{score}/100")
            st.metric("Public Repos", user.get("public_repos", 0))
            st.metric("Followers", user.get("followers", 0))
            st.metric("Following", user.get("following", 0))

        st.divider()

        st.subheader("🧑‍💻 Top Languages")
        lang_count = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1

        if lang_count:
            lang_df = pd.DataFrame(list(lang_count.items()), columns=["Language", "Repos"])
            lang_df = lang_df.sort_values("Repos", ascending=False)
            fig = px.pie(lang_df, names="Language", values="Repos", title="Language Distribution")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("⭐ Top Repositories")
        if repos:
            repo_data = [{
                "Name": r["name"],
                "Stars": r["stargazers_count"],
                "Forks": r["forks_count"],
                "Language": r.get("language", "N/A"),
                "Description": r.get("description", "")[:60] or "No description"
            } for r in repos]

            repo_df = pd.DataFrame(repo_data).sort_values("Stars", ascending=False).head(10)
            st.dataframe(repo_df, use_container_width=True)

            fig2 = px.bar(repo_df, x="Name", y="Stars", title="Top Repos by Stars", color="Stars")
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        created = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        age = (datetime.now() - created).days // 365
        st.info(f"📅 Account created in {created.year} — {age} year(s) old")