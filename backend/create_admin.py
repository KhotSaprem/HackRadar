#!/usr/bin/env python3
"""
CLI script to create the first admin user for HackRadar.
Usage: python create_admin.py
"""
import asyncio
import getpass
import sys
from database import init_database, AsyncSessionLocal
from auth import create_user


async def create_admin_user():
    """Create an admin user interactively."""
    print("HackRadar Admin User Creation")
    print("=" * 30)
    
    # Get email
    while True:
        email = input("Enter admin email: ").strip()
        if email and "@" in email:
            break
        print("Please enter a valid email address.")
    
    # Get password
    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters long.")
        elif len(password) > 128:
            print("Password is too long (max 128 characters). Please use a shorter password.")
        else:
            confirm_password = getpass.getpass("Confirm password: ")
            if password == confirm_password:
                break
            else:
                print("Passwords don't match. Please try again.")
    
    try:
        # Initialize database
        await init_database()
        
        # Create admin user
        async with AsyncSessionLocal() as db:
            user = await create_user(db, email, password, is_admin=True)
            print(f"\n✅ Admin user created successfully!")
            print(f"Email: {user.email}")
            print(f"User ID: {user.id}")
            print(f"Created at: {user.created_at}")
            
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin_user())