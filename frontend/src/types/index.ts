
  export interface User {
    authenticated: boolean;
    username?: string;
    hasRepository?: boolean;
    repositoryName?: string;
  }
  
  export interface Repository {
    name: string;
    html_url: string;
    description: string;
  }
  
  export interface NextCommitInfo {
    has_scheduled_commits: boolean;
    formatted_time: string | null;
    formatted_countdown: string | null;
    seconds_until_next: number | null;
  }

  export interface AutomationStatus {
    active: boolean;
    hasRepository: boolean;
    repo_name: string | null;
    scheduled_commits: number;
    total_commits: number;
    next_commit: NextCommitInfo;
  }
  
  export interface CreateRepositoryRequest {
    repoName: string;
    description: string;
  }

    
  // Commit history
  export interface CommitRecord {
    id: number;
    timestamp: string;
    repo_name: string;
    commit_message: string;
    commit_url: string;
  }
