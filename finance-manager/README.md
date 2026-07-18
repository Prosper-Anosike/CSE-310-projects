# Overview

As a software engineer, I wanted to practice connecting a Python application to a cloud-hosted NoSQL database rather than storing data only in local memory or files. This project is my submission for the CSE 310 **Cloud Databases** module.

This software is a **Personal Finance Manager**: a menu-driven command-line application that lets a user manage multiple people's income and expense transactions, all stored in a Firebase Firestore database. It demonstrates full CRUD (Create, Read, Update, Delete) functionality across two related Firestore collections, `users` and `transactions`, connected through a `user_id` field.

**Software Demo Video:**
(link to be added)

# Data Model

- **users** collection — one document per person: `name`, `email`, `created_at`.
- **transactions** collection — one document per income/expense entry: `user_id` (links back to a user document), `type` (`"income"` or `"expense"`), `amount`, `category`, `description`, `created_at`.

# Setup

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com) and enable **Firestore Database** (Native mode).
2. In the project, go to **Project Settings > Service Accounts > Generate new private key** and download the JSON file.
3. Save that file as `serviceAccountKey.json` inside this `finance-manager/` folder (it is gitignored and must never be committed).
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python main.py
   ```

# Development Environment

## Tools Used
- Visual Studio Code
- Python 3
- Firebase Firestore
- firebase-admin SDK
- Git
- GitHub

## Programming Language
- Python

# Useful Websites

- Python Documentation: https://docs.python.org/3/
- Firebase Documentation: https://firebase.google.com/docs
- Firestore Documentation: https://firebase.google.com/docs/firestore
- firebase-admin Python SDK Reference: https://firebase.google.com/docs/reference/admin/python
- Visual Studio Code Documentation: https://code.visualstudio.com/docs

# GitHub Repository

https://github.com/Prosper-Anosike/CSE-310-projects
