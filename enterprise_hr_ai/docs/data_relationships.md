# Enterprise HR AI — Data Relationships & Entity Architecture

This document formalizes the entity relationships, primary keys, foreign keys, and mapping rules across all raw and processed tables in the Enterprise HR AI system.

```mermaid
erDiagram
    EMPLOYEES ||--o{ EMPLOYEE_SKILLS : "has"
    EMPLOYEES ||--o| ENGAGEMENT_DATA : "records"
    EMPLOYEES ||--o{ PERFORMANCE_HISTORY : "evaluated_in"
    ROLE_SKILLS }o--|| OCCUPATIONS : "mapped_from"
    EMPLOYEE_SKILLS }o--|| COURSES : "upskilled_by"
    EMPLOYEES ||--|| EMPLOYEE_INTELLIGENCE : "synthesizes"

    EMPLOYEES {
        int EmployeeID PK
        string Name
        string Department
        string JobRole FK
        int Age
        float MonthlySalary
        float OvertimeHoursPerMonth
        float WorkLifeBalanceScore
        int PerformanceRating
        int Attrition
    }

    ROLE_SKILLS {
        string JobRole PK, FK
        string SkillName PK
        string Importance
        int RequiredProficiency
    }

    EMPLOYEE_SKILLS {
        int EmployeeID PK, FK
        string SkillName PK
        int CurrentProficiency
        float YearsExperience
    }

    COURSES {
        string CourseID PK
        string CourseTitle
        string TargetSkill FK
        int DurationHours
        string Provider
    }

    EMPLOYEE_INTELLIGENCE {
        int EmployeeID PK, FK
        float AttritionProbability
        string AttritionRiskCategory
        float ReadinessScoreToday
        float ProjectedReadinessAfterTraining
        string PrimaryRecommendation
    }
```

---

## Relational Mapping Table

| Source Entity | Target Entity | Foreign Key | Cardinality | Business Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `employees.csv` | `employee_skills.csv` | `EmployeeID` | 1-to-Many | Maps current employee technical competencies |
| `employees.csv` | `role_skills.csv` | `JobRole` | Many-to-Many | Benchmarks worker skills against role requirements |
| `employee_skills.csv` | `courses.csv` | `SkillName` -> `TargetSkill` | Many-to-One | Provides targeted course matches for missing competencies |
| `employees.csv` | `engagement_data.csv` | `EmployeeID` | 1-to-1 | Provides pulse sentiment, burnout, and WLB indicators |
| `employees.csv` | `employee_intelligence.csv` | `EmployeeID` | 1-to-1 | Unified 360 master table powering API & Dashboard |
