export type ItemStatus = "Active" | "Expiring Soon" | "Expired";

export interface LearningHours {
  year: number;
  quarter: string;
  hours: number;
  target_hours: number;
}

export interface Certification {
  name: string;
  provider: string;
  type: "Internal" | "External";
  completed_date: string;
  expiry_date: string | null;
  status: ItemStatus;
  days_to_expiry: number | null;
}

export interface Competency {
  name: string;
  category: string;
  level: "E1" | "E2";
  acquired_date: string;
  expiry_date: string | null;
  status: ItemStatus;
  days_to_expiry: number | null;
}

export interface TDProgram {
  name: string;
  category: string;
  start_date: string;
  mode: string;
  duration_days: number;
  status: string;
}

export interface Associate {
  id: string;
  name: string;
  email: string;
  designation: string;
  band: string;
  department: string;
  project: string;
  project_manager: string;
  td_manager: string;
  location: string;
  date_of_joining: string;
  total_experience_years: number;
  performance_rating: string;
  learning_hours: LearningHours[];
  certifications: Certification[];
  competencies: Competency[];
  upcoming_td_programs: TDProgram[];
  ytd_learning_hours: number;
  ytd_target_hours: number;
  e1_competencies: number;
  e2_competencies: number;
}

export interface ReminderItem {
  associate_id: string;
  associate_name: string;
  project: string;
  project_manager: string;
  td_manager: string;
  item_type: "Competency" | "Certification";
  name: string;
  level: string;
  expiry_date: string;
  days_to_expiry: number;
  status: ItemStatus;
}

export interface ProgressionCandidate {
  associate_id: string;
  associate_name: string;
  designation: string;
  band: string;
  readiness_score: number;
  max_score: number;
  ready: boolean;
  ytd_learning_hours: number;
  ytd_target_hours: number;
  e2_competencies: number;
  performance_rating: string;
  gaps: string[];
}

export interface OrgSummary {
  headcount: {
    total: number;
    by_department: Record<string, number>;
    by_project: Record<string, number>;
    by_band: Record<string, number>;
  };
  avg_ytd_learning_hours: number;
  total_e1_competencies: number;
  total_e2_competencies: number;
  items_expiring_or_expired: number;
  as_of: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export type Role = "TD Manager" | "Project Manager";
