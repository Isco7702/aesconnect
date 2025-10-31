#!/usr/bin/env python3
"""
Script pour ajouter du contenu de démonstration à AESConnect
Cela évite l'effet "ville fantôme" lors du premier lancement
"""

from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import os
import sys
from flask import Flask
from .database import DATABASE_PATH
from .models import db, User, Post, Comment, Like, Group, GroupMember

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

# Configuration temporaire de l'application Flask pour le contexte
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def seed_demo_users():
    """Créer des utilisateurs de démonstration"""
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
    
    user_ids = []
    
    for user_data in demo_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        
        if existing_user:
            print(f"Utilisateur {user_data['username']} existe déjà")
            user_ids.append(existing_user.id)
            continue
        
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            bio=user_data['bio'],
            country=user_data['country'],
            city=user_data['city'],
            avatar_url=user_data['avatar_url']
        )
        new_user.set_password('demo123')
        db.session.add(new_user)
        db.session.flush()
        user_ids.append(new_user.id)
    
    db.session.commit()
    print(f"✅ {len(user_ids)} utilisateurs de démonstration créés/vérifiés")
    return user_ids

def seed_demo_posts(user_ids):
    """Créer des posts de démonstration"""
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
    for i, post_data in enumerate(demo_posts):
        new_post = Post(
            user_id=post_data['user_id'],
            content=post_data['content'],
            created_at=datetime.utcnow() - timedelta(hours=i*2)
        )
        db.session.add(new_post)
        db.session.flush()
        post_ids.append(new_post.id)
    
    db.session.commit()
    print(f"✅ {len(post_ids)} posts de démonstration créés")
    return post_ids

def seed_demo_groups(user_ids):
    """Créer des groupes de démonstration"""
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
    for group_data in demo_groups:
        # Check if group already exists (simple check by name)
        existing_group = Group.query.filter_by(name=group_data['name']).first()
        if existing_group:
            print(f"Groupe {group_data['name']} existe déjà")
            group_ids.append(existing_group.id)
            continue

        new_group = Group(
            name=group_data['name'],
            description=group_data['description'],
            creator_id=group_data['creator_id'],
            members_count=1
        )
        db.session.add(new_group)
        db.session.flush()
        group_id = new_group.id
        group_ids.append(group_id)
        
        # Add creator as admin member
        new_member = GroupMember(
            group_id=group_id,
            user_id=group_data['creator_id'],
            is_admin=True
        )
        db.session.add(new_member)
        
        # Add some other members randomly
        for user_id in user_ids:
            if user_id != group_data['creator_id'] and random.random() > 0.5:
                # Check if already a member (to avoid IntegrityError)
                existing_member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
                if not existing_member:
                    new_member = GroupMember(
                        group_id=group_id,
                        user_id=user_id,
                        is_admin=False
                    )
                    db.session.add(new_member)
                    new_group.members_count += 1
    
    db.session.commit()
    print(f"✅ {len(group_ids)} groupes de démonstration créés")
    return group_ids

def seed_demo_interactions(user_ids, post_ids):
    """Créer des likes et commentaires de démonstration"""
    
    # Add random likes
    likes_count = 0
    for post_id in post_ids:
        # Each post gets 2-4 random likes
        num_likes = random.randint(2, 4)
        likers = random.sample(user_ids, min(num_likes, len(user_ids)))
        for user_id in likers:
            # Check if already liked (to avoid IntegrityError)
            existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
            if not existing_like:
                new_like = Like(post_id=post_id, user_id=user_id)
                db.session.add(new_like)
                likes_count += 1
    
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
            comment_content = random.choice(demo_comments)
            new_comment = Comment(
                post_id=post_id,
                user_id=user_id,
                content=comment_content
            )
            db.session.add(new_comment)
            comments_count += 1
            
    db.session.commit()
    print(f"✅ {likes_count} likes et {comments_count} commentaires ajoutés")

def main():
    print("\n🌍 AESConnect - Ajout de contenu de démonstration\n")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Assurer que les tables existent
            db.create_all()
            
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
            db.session.rollback()
            print(f"\n❌ Erreur : {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
