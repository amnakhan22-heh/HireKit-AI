cat > ~/job-kit-generator/.claude/skills/debug-backend.md << 'EOF'
---
name: debug-backend
description: Use this skill when the user encounters a Django backend error or bug and needs to debug it
---

When debugging a Django backend error in this project:
1. Read the full error traceback carefully, start from the bottom
2. Check backend/.env to confirm all environment variables are set correctly
3. Run python manage.py check to catch configuration issues
4. Check backend/generator/services.py if the error is related to OpenAI calls
5. Run pytest on the relevant test file to reproduce the issue in isolation
6. Check the database with python manage.py dbshell if it is a database error
7. Always activate the virtual environment first: source backend/venv/bin/activate
EOF