# app/seeders/database_seeder.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import hash_password


def run_seeds(db: Session):
    print("🌱 Запуск сидов...")
    
    # Проверяем, есть ли уже админ
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            name="Admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.flush()
        print(f"✅ Создан админ с ID={admin.id}")
    
    # Создаём разрешения
    permissions = ["get-story-user", "get-story-role", "get-story-permission", "restore-from-history"]
    for perm_name in permissions:
        perm = db.query(Permission).filter(Permission.name == perm_name).first()
        if not perm:
            perm = Permission(name=perm_name)
            db.add(perm)
            print(f"✅ Создано разрешение: {perm_name}")
    
    db.commit()
    print("🌱 Сиды выполнены!")