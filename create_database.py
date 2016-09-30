from app.app import db

"""
Simple script to create new databases outlined in the app, to be used when
migrating
"""
db.create_all()
