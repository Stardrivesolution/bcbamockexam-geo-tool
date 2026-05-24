from app.db.session import SessionLocal
from app.repositories.projects import ProjectRepository
from app.schemas.project import Competitor, ProjectCreate


COMPETITORS = [
    Competitor(
        name="Pass the Big ABA Exam",
        domain="passthebigabaexam.com",
        url="https://passthebigabaexam.com/",
        category="broad",
        notes="Well-known BCBA exam prep provider; competes for exam prep, study materials, and readiness queries.",
        source_url="https://passthebigabaexam.com/",
    ),
    Competitor(
        name="StudyABA",
        domain="studyaba.com",
        url="https://www.studyaba.com/",
        category="direct",
        notes="Direct mock-exam competitor for BCBA exam prep and practice exam queries.",
        source_url="https://www.studyaba.com/",
    ),
    Competitor(
        name="ABA Wizard / Test Prep Technologies",
        domain="testpreptech.com",
        url="https://www.testpreptech.com/",
        category="direct",
        notes="Practice-question and full-study-course competitor for BCBA exam prep prompts.",
        source_url="https://www.testpreptech.com/",
    ),
    Competitor(
        name="Study ABA Exam",
        domain="studyabaexam.com",
        url="https://www.studyabaexam.com/bcba-exam-prep",
        category="direct",
        notes="Direct competitor offering practice questions, flashcards, and mock exams aligned to the 6th edition outline.",
        source_url="https://www.studyabaexam.com/bcba-exam-prep",
    ),
    Competitor(
        name="Mock ABA Exam",
        domain="mockabaexam.com",
        url="https://www.mockabaexam.com/",
        category="direct",
        notes="Direct mock exam competitor for users searching specifically for ABA/BCBA mock exams.",
        source_url="https://www.mockabaexam.com/",
    ),
    Competitor(
        name="ABA Sprout",
        domain="abasprout.com",
        url="https://www.abasprout.com/bcba",
        category="direct",
        notes="BCBA exam prep competitor with mock exams, case studies, and domain mastery tools.",
        source_url="https://www.abasprout.com/bcba",
    ),
    Competitor(
        name="Behavior Development Solutions",
        domain="bds.com",
        url="https://www.bds.com/",
        category="broad",
        notes="Known for CBA Learning Module Series; competes in BCBA exam prep and mastery-style study tools.",
        source_url="https://www.bds.com/",
    ),
    Competitor(
        name="Study Notes ABA",
        domain="studynotesaba.com",
        url="https://studynotesaba.com/",
        category="broad",
        notes="BCBA/BCaBA exam prep content, study products, and community-style learning resources.",
        source_url="https://studynotesaba.com/",
    ),
]


def main() -> None:
    db = SessionLocal()
    try:
        repo = ProjectRepository(db)
        existing = repo.find_by_domain("bcbamockexam.com")
        if existing:
            existing.name = "BCBA Mock Exam"
            existing.brand_name = "BCBA Mock Exam"
            existing.target_language = "en"
            existing.target_region = "US"
            existing.competitors = [item.model_dump() for item in COMPETITORS]
            existing.project_metadata = {
                "website_url": "https://bcbamockexam.com/",
                "primary_topic": "BCBA mock exam and exam prep",
                "notes": "Company-owned site; first GEO target project.",
            }
            db.commit()
            print(f"Updated project id={existing.id}")
            return

        project = repo.create(
            ProjectCreate(
                name="BCBA Mock Exam",
                brand_name="BCBA Mock Exam",
                domain="bcbamockexam.com",
                target_language="en",
                target_region="US",
                competitors=COMPETITORS,
                project_metadata={
                    "website_url": "https://bcbamockexam.com/",
                    "primary_topic": "BCBA mock exam and exam prep",
                    "notes": "Company-owned site; first GEO target project.",
                },
            )
        )
        print(f"Created project id={project.id} domain={project.domain}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
