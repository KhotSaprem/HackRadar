"""
Vercel serverless function entry point for FastAPI application.
"""
from main import app

# Vercel expects a variable named 'app' or 'handler'
# This file serves as the entry point for Vercel deployments
