#!/usr/bin/env python3
"""
Script pour ajouter du contenu de démonstration à AESConnect
Cela évite l'effet "ville fantôme" lors du premier lancement
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

DATABASE_PATH = './social_network.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def seed_demo_users():
    """Créer des utilisateurs de démonstration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    demo_users = [
        {
            'username': 'amina_kenya',
            'email': 'amina@example.com',
            'full_name': 'Amina Wanjiru',
            'bio': '🌍 Passionnée par la tech et l\'innovation en Afrique de l\'Est',
            'country': 'Kenya',
            'city': 'Nairobi',
            'avatar_url': '👩🏾‍💻'
        },
        {
            'username': 'james_uganda',
            'email': 'james@example.com',
            'full_name': 'James Okello',
            'bio': '📸 Photographe amateur | 🎨 Amoureux de l\'art africain',
            'country': 'Uganda',
            'city': 'Kampala',
            'avatar_url': '👨🏿‍🎨'
        },
        {
            'username': 'fatuma_tanzania',
            'email': 'fatuma@example.com',
            'full_name': 'Fatuma Hassan',
            'bio': '🎓 Étudiante en médecine | Défenseuse de la santé publique',
            'country': 'Tanzania',
            'city': 'Dar es Salaam',
            'avatar_url': '👩🏿‍⚕️'
        },
        {
            'username': 'david_rwanda',
            'email': 'david@example.com',
            'full_name': 'David Mugisha',
            'bio': '🚀 Entrepreneur | Building the future of East Africa',
            'country': 'Rwanda',
            'city': 'Kigali',
            'avatar_url': '👨🏾‍💼'
        },
        {
            'username': 'sarah_ethiopia',
            'email': 'sarah@example.com',
            'full_name': 'Sarah Abebe',
            'bio': '☕ Coffee lover | 📚 Écrivaine en herbe',
            'country': 'Ethiopia',
            'city': 'Addis Ababa',
            'avatar_url': '👩🏾‍🏫'
        }
    ]
    
    password_hash = generate_password_hash('demo123')
    user_ids = []
    
    for user in demo_users:
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, bio, country, city, avatar_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user['username'], user['email'], password_hash, user['full_name'], 
                  user['bio'], user['country'], user['city'], user['avatar_url']))
            user_ids.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            print(f"Utilisateur {user['username']} existe déjà")
            # Get existing user id
            existing = cursor.execute('SELECT id FROM users WHERE username = ?', (user['username'],)).fetchone()
            if existing:
                user_ids.append(existing[0])
    
    conn.commit()
    conn.close()
    print(f"✅ {len(user_ids)} utilisateurs de démonstration créés/vérifiés")
    return user_ids

def seed_demo_posts(user_ids):
    """Créer des posts de démonstration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    demo_posts = [
        {
            'content': '🎉 Bienvenue sur AESConnect ! Notre réseau social dédié à l\'Afrique de l\'Est. Connectons-nous et bâtissons ensemble ! #AESConnect #EastAfrica',
            'user_id': user_ids[0] if len(user_ids) > 0 else 1
        },
        {
            'content': '📱 La tech africaine est en plein essor ! Qui travaille sur des projets innovants ? Partagez vos idées ! #TechAfrica #Innovation',
            'user_id': user_ids[1] if len(user_ids) > 1 else 1
        },
        {
            'content': '🌅 Les couchers de soleil à Nairobi sont magiques. Quelle est votre ville préférée en Afrique de l\'Est ? #Travel #Kenya',
            'user_id': user_ids[0] if len(user_ids) > 0 else 1
        },
        {
            'content': '📚 Je viens de terminer un excellent livre sur l\'histoire de l\'Éthiopie. Des recommandations de lecture ? #Books #History',
            'user_id': user_ids[4] if len(user_ids) > 4 else 1
        },
        {
            'content': '🎨 L\'art contemporain africain mérite plus de reconnaissance mondiale. Quels sont vos artistes préférés ? #Art #AfricanArt',
            'user_id': user_ids[1] if len(user_ids) > 1 else 1
        },
        {
            'content': '💼 Entrepreneuriat en Afrique de l\'Est : quels sont les défis et opportunités que vous observez ? #Business #Startup',
            'user_id': user_ids[3] if len(user_ids) > 3 else 1
        },
        {
            'content': '☕ Le café éthiopien est le meilleur du monde, change my mind ! #Coffee #Ethiopia',
            'user_id': user_ids[4] if len(user_ids) > 4 else 1
        },
        {
            'content': '🏥 La santé publique est un droit. Comment pouvons-nous améliorer l\'accès aux soins dans notre région ? #Health #PublicHealth',
            'user_id': user_ids[2] if len(user_ids) > 2 else 1
        }
    ]
    
    post_ids = []
    for i, post in enumerate(demo_posts):
        # Create posts with staggered timestamps
        cursor.execute('''
            INSERT INTO posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (post['user_id'], post['content'], datetime.now() - timedelta(hours=i*2)))
        post_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(post_ids)} posts de démonstration créés")
    return post_ids

def seed_demo_groups(user_ids):
    """Créer des groupes de démonstration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    demo_groups = [
        {
            'name': '🚀 Tech & Innovation East Africa',
            'description': 'Communauté pour les passionnés de technologie et d\'innovation en Afrique de l\'Est',
            'creator_id': user_ids[0] if len(user_ids) > 0 else 1
        },
        {
            'name': '🎨 Art & Culture',
            'description': 'Espace dédié à l\'art, la musique et la culture de notre région',
            'creator_id': user_ids[1] if len(user_ids) > 1 else 1
        },
        {
            'name': '💼 Entrepreneurs Network',
            'description': 'Réseau d\'entrepreneurs et de business leaders',
            'creator_id': user_ids[3] if len(user_ids) > 3 else 1
        },
        {
            'name': '📚 Book Club East Africa',
            'description': 'Club de lecture pour partager nos coups de cœur littéraires',
            'creator_id': user_ids[4] if len(user_ids) > 4 else 1
        },
        {
            'name': '🌍 Voyageurs & Explorateurs',
            'description': 'Pour les amoureux du voyage et de la découverte',
            'creator_id': user_ids[2] if len(user_ids) > 2 else 1
        }
    ]
    
    group_ids = []
    for group in demo_groups:
        cursor.execute('''
            INSERT INTO groups (name, description, creator_id)
            VALUES (?, ?, ?)
        ''', (group['name'], group['description'], group['creator_id']))
        group_id = cursor.lastrowid
        group_ids.append(group_id)
        
        # Add creator as admin member
        cursor.execute('''
            INSERT INTO group_members (group_id, user_id, is_admin)
            VALUES (?, ?, 1)
        ''', (group_id, group['creator_id']))
        
        # Add some other members randomly
        for user_id in user_ids:
            if user_id != group['creator_id'] and random.random() > 0.5:
                try:
                    cursor.execute('''
                        INSERT INTO group_members (group_id, user_id, is_admin)
                        VALUES (?, ?, 0)
                    ''', (group_id, user_id))
                except sqlite3.IntegrityError:
                    pass  # Already a member
    
    conn.commit()
    conn.close()
    print(f"✅ {len(group_ids)} groupes de démonstration créés")
    return group_ids

def seed_demo_interactions(user_ids, post_ids):
    """Créer des likes et commentaires de démonstration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Add random likes
    likes_count = 0
    for post_id in post_ids:
        # Each post gets 2-4 random likes
        num_likes = random.randint(2, 4)
        likers = random.sample(user_ids, min(num_likes, len(user_ids)))
        for user_id in likers:
            try:
                cursor.execute('''
                    INSERT INTO likes (post_id, user_id)
                    VALUES (?, ?)
                ''', (post_id, user_id))
                likes_count += 1
            except sqlite3.IntegrityError:
                pass  # Already liked
    
    # Add some comments
    demo_comments = [
        "Super intéressant ! 👍",
        "Je suis totalement d'accord !",
        "Merci pour le partage 🙏",
        "Belle initiative !",
        "On devrait en discuter plus 💬",
        "Exactement ce dont on a besoin !",
        "J'adore cette idée 💡",
        "Parlons-en bientôt !"
    ]
    
    comments_count = 0
    for post_id in post_ids:
        # Each post gets 1-3 random comments
        num_comments = random.randint(1, 3)
        commenters = random.sample(user_ids, min(num_comments, len(user_ids)))
        for user_id in commenters:
            comment = random.choice(demo_comments)
            cursor.execute('''
                INSERT INTO comments (post_id, user_id, content)
                VALUES (?, ?, ?)
            ''', (post_id, user_id, comment))
            comments_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ {likes_count} likes et {comments_count} commentaires ajoutés")

def main():
    print("\n🌍 AESConnect - Ajout de contenu de démonstration\n")
    print("=" * 50)
    
    try:
        # Create demo users
        user_ids = seed_demo_users()
        
        # Create demo posts
        post_ids = seed_demo_posts(user_ids)
        
        # Create demo groups
        group_ids = seed_demo_groups(user_ids)
        
        # Add interactions
        seed_demo_interactions(user_ids, post_ids)
        
        print("\n" + "=" * 50)
        print("✅ Contenu de démonstration ajouté avec succès !")
        print("\nConnexion de test :")
        print("  Username: amina_kenya")
        print("  Password: demo123")
        print("\n" + "=" * 50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
