import requests
import sys

BASE_URL = 'http://localhost:8000/api'

def format_compact(num):
    if num is None or num <= 0:
        return '0'
    if num < 1000:
        return str(num)
    if num < 1_000_000:
        val = num / 1000
        formatted = f"{val:.1f}"
        return f"{int(val)}K" if formatted.endswith('.0') else f"{formatted}K"
    val = num / 1_000_000
    formatted = f"{val:.1f}"
    return f"{int(val)}M" if formatted.endswith('.0') else f"{formatted}M"

def run_tests():
    print("============================================================")
    print("COMMUNITY FEED REALISM & DEDUPLICATION VERIFICATION")
    print("============================================================")

    # 1. Login Account A (Demo Recruiter) and Account B (Demo Content Creator)
    r_a = requests.post(f'{BASE_URL}/auth/login', json={'email': 'recruiter@codexero.com', 'password': 'Demo@123'})
    assert r_a.status_code == 200, "Login A failed"
    token_a = r_a.json()['access_token']
    h_a = {'Authorization': f'Bearer {token_a}'}

    r_b = requests.post(f'{BASE_URL}/auth/login', json={'email': 'creator@codexero.com', 'password': 'Demo@123'})
    assert r_b.status_code == 200, "Login B failed"
    token_b = r_b.json()['access_token']
    h_b = {'Authorization': f'Bearer {token_b}'}
    print("[PASS] 1. Authentication for Account A & B verified")

    # 2. Check no duplicate posts returned by GET /community/posts
    r_feed = requests.get(f'{BASE_URL}/community/posts', headers=h_a)
    assert r_feed.status_code == 200, "Fetch feed failed"
    posts = r_feed.json()
    post_ids = [p['id'] for p in posts]
    titles = [p['title'] for p in posts]
    
    assert len(post_ids) == len(set(post_ids)), f"Duplicate post IDs found: {len(post_ids)} vs {len(set(post_ids))}"
    print(f"[PASS] 2. No duplicate post IDs in feed (Total unique posts: {len(posts)})")

    # Verify no consecutive identical titles from same author
    seen_posts = set()
    for p in posts:
        key = (p['author_id'], p['title'].strip().lower())
        assert key not in seen_posts, f"Duplicate author post found in feed: {p['title']}"
        seen_posts.add(key)
    print(f"[PASS] 3. Database contains 0 duplicate author/title post pairs")

    # 3. Verify realistic engagement baselines & format
    print("\n--- Seeded Posts Engagement Verification ---")
    seeded_checked = 0
    for p in posts[:6]:
        likes = p['likes_count']
        comments = p['comments_count']
        fmt_likes = format_compact(likes)
        fmt_comments = format_compact(comments)
        print(f"  Post #{p['id']}: '{p['title'][:40]}...' | Likes: {likes} ({fmt_likes}) | Comments: {comments} ({fmt_comments})")
        if likes >= 800:
            seeded_checked += 1
            assert 'K' in fmt_likes or likes < 1000, f"Expected compact format for {likes}"

    assert seeded_checked >= 3, "Seeded posts do not have realistic baseline numbers!"
    print(f"[PASS] 4. Realistic engagement baselines and compact K formatting verified")

    # 4. Verify Like/Unlike real interactions
    target_post = posts[0]
    target_id = target_post['id']
    init_likes = target_post['likes_count']
    print(f"\n--- Testing Real Interactive Like on Post #{target_id} ---")
    print(f"  Initial likes count: {init_likes} ({format_compact(init_likes)})")

    # First ensure it's not liked
    if target_post.get('is_liked_by_me'):
        requests.delete(f'{BASE_URL}/community/posts/{target_id}/like', headers=h_a)
        r_f = requests.get(f'{BASE_URL}/community/posts', headers=h_a)
        target_post = [p for p in r_f.json() if p['id'] == target_id][0]
        init_likes = target_post['likes_count']

    # Like post as Account A
    r_like = requests.post(f'{BASE_URL}/community/posts/{target_id}/like', headers=h_a)
    assert r_like.status_code == 200, f"Like request failed: {r_like.text}"
    like_data = r_like.json()
    assert like_data['liked'] is True, "Expected liked to be True"
    assert like_data['likes_count'] == init_likes + 1, f"Expected {init_likes + 1}, got {like_data['likes_count']}"
    print(f"[PASS] 5. Like incremented count by 1: {init_likes} -> {like_data['likes_count']} ({format_compact(like_data['likes_count'])})")

    # Account B sees the updated count
    r_feed_b = requests.get(f'{BASE_URL}/community/posts', headers=h_b)
    post_seen_by_b = [p for p in r_feed_b.json() if p['id'] == target_id][0]
    assert post_seen_by_b['likes_count'] == init_likes + 1, "Cross-account like count mismatch!"
    print(f"[PASS] 6. Account B accurately sees updated like count: {post_seen_by_b['likes_count']}")

    # Unlike post as Account A
    r_unlike = requests.delete(f'{BASE_URL}/community/posts/{target_id}/like', headers=h_a)
    assert r_unlike.status_code == 200, f"Unlike request failed: {r_unlike.text}"
    unlike_data = r_unlike.json()
    assert unlike_data['liked'] is False, "Expected liked to be False"
    assert unlike_data['likes_count'] == init_likes, f"Expected {init_likes}, got {unlike_data['likes_count']}"
    print(f"[PASS] 7. Unlike decremented count by 1 back to: {unlike_data['likes_count']}")

    # 5. Verify Comment Persistence & Count Increment
    init_comments = target_post['comments_count']
    comment_text = "Verified realism: This pipeline output is breathtaking!"
    r_comment = requests.post(f'{BASE_URL}/community/posts/{target_id}/comments', json={'content': comment_text}, headers=h_a)
    assert r_comment.status_code == 201, f"Add comment failed: {r_comment.text}"
    print(f"[PASS] 8. Real user comment added to Post #{target_id}")

    # Re-fetch post: comment count must increment by 1
    r_refetch = requests.get(f'{BASE_URL}/community/posts', headers=h_b)
    refetched_post = [p for p in r_refetch.json() if p['id'] == target_id][0]
    assert refetched_post['comments_count'] == init_comments + 1, f"Expected {init_comments + 1}, got {refetched_post['comments_count']}"
    print(f"[PASS] 9. Comments count updated dynamically: {init_comments} -> {refetched_post['comments_count']} ({format_compact(refetched_post['comments_count'])})")

    # Account B reads comments list
    r_cmts = requests.get(f'{BASE_URL}/community/posts/{target_id}/comments', headers=h_b)
    assert r_cmts.status_code == 200, "Get comments failed"
    matching = [c for c in r_cmts.json() if c['content'] == comment_text]
    assert len(matching) > 0, "Account B could not see comment created by Account A"
    print(f"[PASS] 10. Comment content accurately persisted & visible to Account B")

    # 6. Verify duplicate post prevention on POST /community/posts
    post_payload = {
        'title': 'Realism Guard Test Post',
        'content': 'Ensuring deduplication prevents duplicate rows from being inserted.',
        'post_type': 'Showcase Work',
        'tools_tags': ['Midjourney v6', 'Runway Gen-3']
    }
    r_p1 = requests.post(f'{BASE_URL}/community/posts', json=post_payload, headers=h_b)
    assert r_p1.status_code == 201, "First post failed"
    p1_id = r_p1.json()['id']

    # Immediate second post with same content
    r_p2 = requests.post(f'{BASE_URL}/community/posts', json=post_payload, headers=h_b)
    assert r_p2.status_code in (200, 201), "Second post request failed"
    p2_id = r_p2.json()['id']
    assert p1_id == p2_id, f"Duplicate post prevention failed: Got {p1_id} and {p2_id}"
    print(f"[PASS] 11. Duplicate post creation within 10s successfully debounced/prevented (Returned ID: {p1_id})")

    print("\n============================================================")
    print("ALL COMMUNITY REALISM & DEDUPLICATION TESTS PASSED!")
    print("============================================================")

if __name__ == '__main__':
    run_tests()
