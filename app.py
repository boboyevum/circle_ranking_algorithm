from flask import Flask, render_template_string
import json
import os
from datetime import datetime, timezone
from bs4 import BeautifulSoup

app = Flask(__name__)

SCORED_PATH = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'posts_scored.json')

def get_plain_text(html):
    if not html:
        return ''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def get_time_ago(published_at):
    if not published_at:
        return ''
    try:
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
    except Exception:
        return ''
    now = datetime.now(timezone.utc)
    delta = now - dt
    seconds = delta.total_seconds()
    hours = int(seconds // 3600)
    days = int(seconds // 86400)
    weeks = int(seconds // (86400 * 7))
    years = int(seconds // (86400 * 365))
    if hours < 24:
        return f"{hours}h" if hours > 0 else "<1h"
    elif days < 7:
        return f"{days}d"
    elif weeks < 52:
        return f"{weeks}w"
    else:
        return f"{years}y"

def truncate_body(body, word_limit=40):
    words = body.split()
    if len(words) <= word_limit:
        return body, False
    return ' '.join(words[:word_limit]) + ' ...', True

def get_avatar_initials(name):
    if not name:
        return "?"
    parts = name.split()
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()

@app.route('/')
def feed():
    with open(SCORED_PATH, encoding='utf-8') as f:
        posts_data = json.load(f)
    posts = []
    count = 0
    for post in posts_data:
        space_name = post.get('space_name') or 'General'
        if space_name == 'Feature requests':
            continue
        if count >= 50:
            break
        user_name = post.get('user_name') or 'Unknown User'
        user_avatar = post.get('user_avatar_url')
        title = post.get('name')
        body_html = post.get('body', '')
        body = get_plain_text(body_html)
        likes = post.get('likes_count', 0)
        comments = post.get('comments_count', 0)
        time_ago = get_time_ago(post.get('published_at'))
        body_preview, is_truncated = truncate_body(body, 40)

        avatars = []
        if user_avatar:
            avatars.append({'img': user_avatar, 'initials': None})
        else:
            avatars.append({'img': None, 'initials': get_avatar_initials(user_name)})

        import random, string
        for _ in range(2):
            if random.random() > 0.5:
                avatars.append({'img': None, 'initials': ''.join(random.choices(string.ascii_uppercase, k=2))})
            else:
                avatars.append({'img': f'https://randomuser.me/api/portraits/men/{random.randint(10,99)}.jpg', 'initials': None})
        avatars = avatars[:3]
        posts.append({
            'user': user_name,
            'profile_pic': user_avatar,
            'category': space_name,
            'title': title,
            'body': body_preview,
            'comments': comments,
            'likes': likes,
            'time_ago': time_ago,
            'see_more': is_truncated,
            'avatars': avatars,
        })
        count += 1
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feed</title>
    <link href="https://fonts.googleapis.com/css?family=Inter:400,500,600,700,800&display=swap" rel="stylesheet">
    <style>
        body {
            background: #191b1f;
            margin: 0;
            font-family: 'Inter', Arial, sans-serif;
            color: #E4E6EB;
        }
        .top-bar {
            width: 100vw;
            background: #2b2e33;
            color: #fff;
            font-size: 1.45em;
            font-weight: 700;
            padding: 22px 0 22px 0;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            padding-left: 40px;
            letter-spacing: -0.5px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .feed-container {
            max-width: 700px;
            margin: 40px auto 0 auto;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-card {
            background: #2b2e33;
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.10);
            margin-bottom: 28px;
            padding: 0;
            border: 1px solid #353945;
            transition: border 0.2s;
            font-family: 'Inter', Arial, sans-serif;
            position: relative;
            padding-top: 0;
        }
        .post-card:hover {
            border: 1px solid #44474f;
        }
        .post-header {
            display: flex;
            align-items: flex-start;
            padding: 20px 24px 0 24px;
            margin-top: 0;
            font-family: 'Inter', Arial, sans-serif;
            justify-content: space-between;
        }
        .post-header-main {
            display: flex;
            align-items: center;
        }
        .post-header-actions {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 2px;
        }
        .share-label {
            color: #A3A6AB;
            font-size: 0.82em;
            font-weight: 400;
            font-family: 'Inter', Arial, sans-serif;
            letter-spacing: 0.01em;
        }
        .menu-dots {
            display: flex;
            align-items: center;
            gap: 2px;
        }
        .menu-dot {
            width: 4px;
            height: 4px;
            background: #A3A6AB;
            border-radius: 50%;
            display: inline-block;
        }
        .profile-pic, .profile-initials {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 16px;
            background: #353945;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.2em;
            color: #fff;
            font-family: 'Inter', Arial, sans-serif;
        }
        .profile-initials {
            background: #6C6F7F;
        }
        .user-meta {
            display: flex;
            flex-direction: column;
            font-family: 'Inter', Arial, sans-serif;
        }
        .user-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .user-name {
            font-weight: 400;
            font-size: .88em;
            color: #fff;
            font-family: 'Inter', Arial, sans-serif;
        }
        .badge {
            background: #5A5DF0;
            color: #fff;
            font-size: 0.72em;
            font-weight: 500;
            border-radius: 8px;
            padding: 2px 8px;
            margin-left: 2px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-meta {
            font-size: 0.78em;
            color: #A3A6AB;
            margin-top: 2px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .dot {
            width: 4px;
            height: 4px;
            background: #A3A6AB;
            border-radius: 50%;
            display: inline-block;
        }
        .post-body-section {
            padding: 12px 24px 0 24px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-title {
            font-size: 1.13em;
            font-weight: 700;
            color: #fff;
            margin-bottom: 6px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-body {
            color: #E4E6EB;
            font-size: 1em;
            margin-bottom: 10px;
            display: inline;
            font-family: 'Inter', Arial, sans-serif;
        }
        .see-more-btn {
            color: #A3A6AB;
            font-size: 0.98em;
            background: none;
            border: none;
            cursor: not-allowed;
            margin: 0;
            margin-top: 4px;
            padding: 0;
            font-weight: 500;
            display: block;
            text-align: left;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px 6px 24px;
            margin-top: 2px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .post-actions {
            display: flex;
            gap: 5px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .action-btn {
            background: none;
            border: none;
            color: #A3A6AB;
            font-size: 1.25em;
            border-radius: 50%;
            width: 26px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: not-allowed;
            transition: background 0.2s;
            padding: 0;
            font-family: 'Inter', Arial, sans-serif;
        }
        .action-btn svg {
            width: 22px;
            height: 22px;
        }
        .post-stats {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.88em;
            color: #A3A6AB;
            font-family: 'Inter', Arial, sans-serif;
        }
        .avatars {
            display: flex;
            align-items: center;
            margin-right: 8px;
            font-family: 'Inter', Arial, sans-serif;
        }
        .avatar-img {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #2b2e33;
            margin-left: -10px;
            background: #353945;
            object-fit: cover;
            z-index: 1;
        }
        .avatar-initials {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #2b2e33;
            margin-left: -10px;
            background: #21ba45;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: .75em;
            font-family: 'Inter', Arial, sans-serif;
            z-index: 1;
        }
        .avatars .avatar-img:first-child, .avatars .avatar-initials:first-child {
            margin-left: 0;
        }
    </style>
</head>
<body>
    <div class="top-bar">Circle's Advanced Feed</div>
    <div class="feed-container">
        {% for post in posts %}
        <div class="post-card">
            <div class="post-header">
                <div class="post-header-main">
                    {% if post.profile_pic %}
                        <img class="profile-pic" src="{{ post.profile_pic }}" alt="Profile pic">
                    {% else %}
                        <div class="profile-initials">{{ post.user.split(' ')[0][0] }}{{ post.user.split(' ')[-1][0] }}</div>
                    {% endif %}
                    <div class="user-meta">
                        <div class="user-row">
                            <span class="user-name">{{ post.user }}</span>
                        </div>
                        <div class="post-meta">
                            Posted in {{ post.category }}
                            <span class="dot"></span>
                            {{ post.time_ago }}
                        </div>
                    </div>
                </div>
                <div class="post-header-actions">
                    <span class="share-label">Share</span>
                    <span class="menu-dots">
                        <span class="menu-dot"></span>
                        <span class="menu-dot"></span>
                        <span class="menu-dot"></span>
                    </span>
                </div>
            </div>
            <div class="post-body-section">
                {% if post.title %}
                    <div class="post-title">{{ post.title }}</div>
                {% endif %}
                <span class="post-body">{{ post.body }}</span>
                {% if post.see_more %}<button class="see-more-btn" disabled>See more</button>{% endif %}
                <div style="border-bottom: 1px solid #353945; margin: 6px 0 0 0;"></div>
            </div>
            <div class="post-footer">
                <div class="post-actions">
                    <button class="action-btn" disabled title="Like">
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4.318 6.318a4.5 4.5 0 0 1 6.364 0L12 7.636l1.318-1.318a4.5 4.5 0 1 1 6.364 6.364L12 21.682l-7.682-7.682a4.5 4.5 0 0 1 0-6.364z"/></svg>
                    </button>
                    <button class="action-btn" disabled title="Comment">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="8" fill="none"/>
                            <polygon points="16,20 20,22 18,18" fill="currentColor" stroke="none"/>
                        </svg>
                    </button>
                </div>
                <div class="post-stats">
                    <div class="avatars">
                        {% for avatar in post.avatars %}
                            {% if avatar.img %}
                                <img class="avatar-img" src="{{ avatar.img }}" alt="avatar" />
                            {% else %}
                                <div class="avatar-initials">{{ avatar.initials }}</div>
                            {% endif %}
                        {% endfor %}
                    </div>
                    <span>{{ post.likes }} likes</span>
                    <span>&bull;</span>
                    <span>{{ post.comments }} comments</span>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''', posts=posts)

if __name__ == '__main__':
    app.run(debug=True) 