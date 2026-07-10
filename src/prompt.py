import json

def build_prompt(resumes):

    schema = {
        "skills": [],
        "education": "",
        "experience_years": 0,
        "projects": [],
        "certifications": [],
        "job_role_1": "",
        "confidence_1": 0,
        "job_role_2": "",
        "confidence_2": 0,
        "job_role_3": "",
        "confidence_3": 0,
        "job_role_4": "",
        "confidence_4": 0,
        "job_role_5": "",
        "confidence_5": 0
    }

    prompt = f"""
You are a Resume Information Extraction Engine.

Your job is NOT to chat.

Your job is to convert resumes into structured machine learning labels.

Return ONLY a valid JSON array.

DO NOT write explanations.

DO NOT write markdown.

DO NOT wrap JSON inside ```.

DO NOT summarize the resume.

DO NOT invent information.

The JSON schema for EACH resume is:

{json.dumps(schema, indent=4)}

=========================================================
Extraction Rules
=========================================================

1. SKILLS

Return up to 10 important technical or professional skills.

Use standardized names.

Examples

Python

Java

SQL

Power BI

QuickBooks

SAP ERP

Oracle ERP

Financial Modeling

Valuation Analysis

Machine Learning

Never return generic words like

Leadership

Communication

Management

Hard Working

=========================================================

2. EDUCATION

Return ONLY the highest qualification.

GOOD

MBA

M.Tech

B.Tech

B.Com

MCA

BCA

B.Sc

PhD

BAD

MBA Executive Leadership, University of Texas

Bachelor of Commerce, University of Toronto

Master of Business Administration, Northeastern University

Never include

University

College

Location

Year

CGPA

=========================================================

3. EXPERIENCE

Estimate total professional experience.

Return ONLY an integer.

Examples

0

2

5

8

12

15

Return 0 ONLY if no work experience exists.

=========================================================

4. PROJECTS

Return at most five projects.

If none

[]

=========================================================

5. CERTIFICATIONS

Return at most five certifications.

Only official certifications.

=========================================================

6. JOB ROLES

Recommend exactly FIVE industry-standard job titles.

Rank from best to least suitable.

Examples

Software Engineer

Python Developer

Backend Developer

Machine Learning Engineer

Data Scientist

Data Analyst

Financial Controller

Finance Manager

Accounting Manager

Accountant

ERP Consultant

Compliance Officer

HR Manager

Project Manager

Business Analyst

Rules

One field = One job title

Never use

/

&

or

()

Never invent job titles.

Do NOT return

Executive Leadership

Team Player

Speaker

Leadership Coach

Online Teacher

Those are not job titles.

=========================================================

7. CONFIDENCE

Return integer between 0 and 100.

=========================================================

8. FINAL CHECK

Before returning verify

✓ Valid JSON

✓ JSON Array

✓ Exactly {len(resumes)} objects

✓ Exactly five job roles

✓ Education contains only degree

✓ Experience integer

✓ No explanations

=========================================================

Resumes

"""

    for i, resume in enumerate(resumes, start=1):

        prompt += f"\nResume {i}\n{resume}\n"

    return prompt