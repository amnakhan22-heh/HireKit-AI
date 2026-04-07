cat > ~/job-kit-generator/.claude/skills/add-component.md << 'EOF'
---
name: add-component
description: Use this skill when the user wants to add a new React component to the frontend
---

When adding a new React component to this project:
1. Create the component file in frontend/src/components/
2. Use functional components and hooks only, no class components
3. All backend API calls must go through frontend/src/api/ not directly in the component
4. Use Tailwind utility classes only for styling, no custom CSS
5. Handle loading state, error state and empty state in every component
6. Keep the component under 100 lines, split into smaller components if needed
EOF