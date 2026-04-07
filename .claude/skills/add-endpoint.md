---
name: add-endpoint
description: Use this skill when the user wants to add a new API endpoint to the Django REST Framework backend
---

When adding a new API endpoint to this Django REST Framework project:
1. Create the view in backend/generator/views.py following existing view patterns
2. Create or update the serializer in backend/generator/serializers.py with full validation
3. Register the URL in backend/generator/urls.py following REST conventions
4. If the endpoint calls OpenAI, add the logic in backend/generator/services.py only
5. Write pytest tests in backend/generator/tests/ before marking it done
6. Update API.md with the new endpoint details
7. Run pytest and confirm all tests pass before finishing
