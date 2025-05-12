from models import db, Role, User

def create_initial_roles():
    # Check if roles already exist
    if Role.query.count() == 0:
        roles = [
            Role(name='admin', description='Administrator with full access'),
            Role(name='staff', description='Staff with limited access'),
            Role(name='student', description='Student with restricted access')
        ]
        db.session.bulk_save_objects(roles)
        db.session.commit()
        # Create initial admin user
        admin_role = Role.query.filter_by(name='admin').first()
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin = User(
                username='admin',
                email='admin@example.com',
                role=admin_role
            )
            admin.set_password('admin123')  # default password, should be changed
            db.session.add(admin)
            db.session.commit() 