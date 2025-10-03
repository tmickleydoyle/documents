## Task Management Dashboard

A comprehensive React/Next.js application for managing tasks and projects with a modern, responsive interface.

### Features

- **Task Management**: Create, edit, delete, and track tasks
- **Status Tracking**: Todo, In Progress, Review, and Completed statuses
- **Priority Levels**: Low, Medium, High, and Urgent priorities
- **User Assignment**: Assign tasks to team members
- **Due Date Tracking**: Visual indicators for overdue tasks
- **Time Estimation**: Track estimated vs actual hours
- **Tagging System**: Organize tasks with custom tags
- **Dashboard Analytics**: Visual charts and statistics
- **Search & Filtering**: Find tasks quickly with advanced filters
- **Responsive Design**: Works on desktop, tablet, and mobile

### Tech Stack

- **Framework**: Next.js 13.4
- **UI Library**: Material-UI (MUI) v5
- **State Management**: Zustand
- **Forms**: React Hook Form
- **Charts**: Recharts
- **Date Handling**: date-fns
- **TypeScript**: Full type safety
- **Testing**: Jest + React Testing Library

### Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) with your browser.

### Project Structure

```
├── components/           # Reusable UI components
│   ├── TaskCard.tsx     # Individual task display
│   ├── TaskForm.tsx     # Task creation/editing form
│   ├── DashboardOverview.tsx  # Analytics dashboard
│   ├── TaskFilters.tsx  # Search and filter controls
│   └── LoginForm.tsx    # Authentication form
├── pages/               # Next.js pages
│   ├── index.tsx        # Main dashboard
│   └── login.tsx        # Login page
├── store/               # State management
│   └── taskStore.ts     # Zustand store for tasks
├── types/               # TypeScript definitions
│   └── index.ts         # Type definitions
├── utils/               # Utility functions
│   └── taskUtils.ts     # Task-related helpers
└── __tests__/           # Test files
    └── TaskCard.test.tsx
```

### Key Components

#### TaskCard
- Displays individual task information
- Supports inline status updates
- Shows priority, assignee, due date, and tags
- Edit and delete actions

#### TaskForm
- Modal dialog for creating/editing tasks
- Form validation with React Hook Form
- Tag management with autocomplete
- User assignment dropdown

#### DashboardOverview
- Statistics cards (total, completed, in progress, overdue)
- Progress visualization
- Charts for status and priority distribution
- Recent tasks display

#### TaskFilters
- Real-time search functionality
- Filter by status, priority, and assignee
- Clear all filters option
- Collapsible advanced filters

### State Management

Uses Zustand for lightweight state management:
- Task CRUD operations
- User management
- Loading and error states
- Optimistic updates

### Testing

Run tests with:
```bash
npm test
```

Coverage report:
```bash
npm run test:coverage
```

### Demo Credentials

For testing the login functionality:
- **Email**: demo@taskdashboard.com
- **Password**: demo123

### License

MIT License
