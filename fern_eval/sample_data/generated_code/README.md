# Task Manager App

A task management application built with Next.js and React.

## Features

- Task creation and management
- Status tracking (pending, active, testing, done)
- Priority management (low, normal, high, critical)
- User assignments
- Due date tracking
- Tag system
- Dashboard with charts
- Search and filtering

## Technology Used

- Next.js 14.0
- React 18.2
- Material-UI 5.14
- Recharts for charts
- Moment.js for dates
- Lodash for utilities
- TypeScript

## Setup Instructions

1. Install packages:
   ```
   npm install
   ```

2. Start development:
   ```
   npm run dev
   ```

3. Open browser to http://localhost:3000

## File Structure

```
├── components/
│   ├── TaskComponent.tsx
│   ├── TaskDialog.tsx
│   ├── DashboardOverview.tsx
│   ├── TaskFilter.tsx
│   └── LoginComponent.tsx
├── pages/
│   ├── index.tsx
│   └── login.tsx
├── types/
│   └── types.ts
├── utils/
│   └── helpers.ts
└── package.json
```

## Components Overview

### TaskComponent
Shows individual task with edit/delete buttons and status updates.

### TaskDialog
Modal for creating and editing tasks with form validation.

### DashboardOverview
Statistics display with pie charts and bar charts showing task distribution.

### TaskFilter
Search and filter functionality for finding tasks.

### LoginComponent
Simple login form with demo credentials.

## Usage

The app starts with a dashboard showing task statistics. You can:

- Click the + button to add new tasks
- Filter tasks by status in the tabs
- Use search and filters to find specific tasks
- Click on task status to cycle through statuses
- Edit or delete tasks using the buttons

## Demo Login

Use these credentials to test:
- Email: demo@taskdashboard.com
- Password: demo123

## Development

The app uses mock data for demonstration. In a real implementation, you would replace this with API calls to a backend service.

Key libraries:
- MUI for UI components
- Moment.js for date handling
- Lodash for array/object utilities
- Recharts for data visualization

## Notes

This is a demo application for task management functionality.
