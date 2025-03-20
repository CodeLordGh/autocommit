# GitHub Auto-Commit App

An application that automatically creates and maintains a GitHub repository with daily commits.

## Features

- GitHub OAuth authentication
- Automatic repository creation
- Configurable daily commits (randomly between 1-10 commits per day)
- Random commit scheduling during business hours
- Modern React frontend with TypeScript and Vite
- Event-driven architecture for reliable scheduling

## Technology Stack

### Backend
- Flask
- APScheduler for task scheduling
- GitHub API for repository management and commits

### Frontend
- React with TypeScript
- Vite for fast development
- React Router for navigation
- Tailwind CSS for styling
- Axios for API communication

## Architecture Overview

The application follows an event-driven architecture:

1. **Authentication Flow**:
   - User authenticates via GitHub OAuth
   - Backend stores access token in session
   - Frontend redirects to dashboard

2. **Repository Creation**:
   - User initiates repository creation from dashboard
   - Backend creates repository using GitHub API
   - Backend schedules daily commit jobs

3. **Commit Scheduling**:
   - At midnight each day, a random number (1-10) of commits is scheduled
   - Commits are distributed randomly throughout business hours (9 AM - 5 PM)
   - Each commit updates the README.md file with a timestamp

4. **User Interface**:
   - Dashboard shows repository status and scheduled commits
   - Real-time updates when commits are scheduled or completed

## Getting Started

Follow the setup instructions in the project documentation:

1. Set up the Flask backend
2. Configure GitHub OAuth
3. Start the React frontend
4. Connect your GitHub account

## Security Considerations

- OAuth tokens are stored in server-side sessions only
- Environment variables are used for sensitive information
- CORS is configured for enhanced security
- HTTPS is recommended for production deployment

## Development

See the setup instructions for detailed development setup steps.