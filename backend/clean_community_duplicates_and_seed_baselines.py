import sqlite3
import sys

def main():
    conn = sqlite3.connect('maccall.db')
    cursor = conn.cursor()

    # 1. Add base_likes and base_comments columns if not present
    cursor.execute("PRAGMA table_info(community_posts)")
    cols = [col[1] for col in cursor.fetchall()]

    if 'base_likes' not in cols:
        print("[MIGRATION] Adding base_likes column...")
        cursor.execute("ALTER TABLE community_posts ADD COLUMN base_likes INTEGER DEFAULT 0")

    if 'base_comments' not in cols:
        print("[MIGRATION] Adding base_comments column...")
        cursor.execute("ALTER TABLE community_posts ADD COLUMN base_comments INTEGER DEFAULT 0")

    conn.commit()

    # 2. Find and clean duplicate posts
    cursor.execute("SELECT id, author_id, title, content FROM community_posts ORDER BY id ASC")
    all_posts = cursor.fetchall()

    seen_keys = {}
    to_delete = []

    for post_id, author_id, title, content in all_posts:
        norm_title = (title or "").strip().lower()
        norm_content = (content or "").strip().lower()
        key = (author_id, norm_title, norm_content)

        if key in seen_keys:
            to_delete.append(post_id)
            print(f"[DUPLICATE] Found duplicate post ID {post_id} (original is ID {seen_keys[key]}): '{title}'")
        else:
            seen_keys[key] = post_id

    if to_delete:
        print(f"[CLEANUP] Removing {len(to_delete)} duplicate post(s): {to_delete}")
        for del_id in to_delete:
            cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (del_id,))
            cursor.execute("DELETE FROM post_comments WHERE post_id = ?", (del_id,))
            cursor.execute("DELETE FROM saved_posts WHERE post_id = ?", (del_id,))
            cursor.execute("DELETE FROM community_posts WHERE id = ?", (del_id,))
        conn.commit()
        print("[CLEANUP] Duplicate posts safely removed.")
    else:
        print("[INFO] No duplicate posts found.")

    # 3. Populate realistic baseline engagement counts
    baselines = {
        1: (3420, 184),
        2: (1890, 126),
        3: (8750, 612),
        4: (1240, 88),
        5: (980, 54),
        6: (11400, 1420),
        7: (4650, 320),
        8: (2100, 145),
        9: (5400, 410),
        10: (3120, 215),
        11: (7800, 580),
        12: (6200, 490),
        13: (9450, 830),
        14: (2450, 190),
        15: (1680, 115),
    }

    for pid, (blikes, bcmts) in baselines.items():
        cursor.execute("UPDATE community_posts SET base_likes = ?, base_comments = ? WHERE id = ?", (blikes, bcmts, pid))

    conn.commit()
    print("[BASELINES] Realistic engagement baselines updated for seeded posts.")

    # Verify final rows
    cursor.execute("SELECT id, title, base_likes, base_comments FROM community_posts ORDER BY id ASC")
    remaining = cursor.fetchall()
    print(f"\n[SUMMARY] Total community posts remaining: {len(remaining)}")
    for r in remaining:
        print(f"  ID {r[0]}: '{r[1]}' -> {r[2]} base likes, {r[3]} base comments")

    conn.close()

if __name__ == '__main__':
    main()
