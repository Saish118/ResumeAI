"""Unit tests for Resume Content Validation Service."""

import pytest
from app.services.resume_validator import resume_validator


def test_valid_resume_full_sections():
    text = """
    AYUSH SASANE
    Pune, India | +91-9881802434 | ayush@gmail.com
    linkedin.com/in/ayush-sasane | github.com/AyushSasane
    
    SUMMARY
    Full-stack engineer with hands-on experience building web applications using React.js and Node.js.
    
    EDUCATION
    Vishwakarma Institute of Technology | B.Tech in CSE (2023 - 2026)
    
    SKILLS
    Languages: Python, JavaScript, Java, SQL
    Frontend: React, HTML, CSS
    
    EXPERIENCE
    Software Engineering Intern - TechCorp (March 2026 - Present)
    Built RESTful APIs and admin dashboards.
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is True
    assert res["score"] >= 0.50
    assert "+ Found Experience Section" in res["evidence"]
    assert "+ Found Education Section" in res["evidence"]


def test_resume_minimal_sections():
    text = """
    Jane Doe
    jane.doe@example.com
    
    EDUCATION
    BS Computer Science, Stanford University (2020 - 2024)
    
    SKILLS
    Python, C++, Java, Git, HTML, CSS
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is True
    assert res["score"] >= 0.30
    assert "+ Found Education Section" in res["evidence"]


def test_empty_or_whitespace_text():
    res1 = resume_validator.validate("")
    assert res1["is_resume"] is False
    assert res1["score"] == 0.0

    res2 = resume_validator.validate("   \n\t  ")
    assert res2["is_resume"] is False
    assert res2["score"] == 0.0


def test_random_article_or_report():
    text = """
    The Global Climate Impact Report 2025
    
    Introduction
    Global temperatures have increased steadily over the past century. Carbon emissions
    continue to rise across industrial nations.
    
    Methodology
    We collected satellite data across 50 regions over ten years.
    
    Results
    Data indicates a 1.2 degree Celsius increase in average global sea surface temperature.
    
    Conclusion
    Urgent policy intervention is required.
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is False


def test_invoice_document():
    text = """
    TAX INVOICE # 94021
    Bill To: Global Logistics Inc.
    Ship To: Warehouse 4B
    Invoice Date: Oct 12, 2025
    Payment Terms: Net 30
    
    Item Description | Qty | Unit Price | Total
    Server Rack 42U  |  2  | $1,500.00  | $3,000.00
    
    Amount Due: $3,000.00
    Total Amount: $3,000.00
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is False
    assert "- Detected Invoice / Bill Document" in res["evidence"]


def test_academic_assignment_or_lab_report():
    text = """
    LABORATORY REPORT # 4
    Experiment No 5: Digital Logic Circuit Simulation
    Course Code: CS301 - Computer Architecture
    Submitted to: Prof. Alan Turing
    Submitted by: John Smith (Roll No: 104)
    
    Problem Statement:
    Design a 4-bit synchronous binary counter using JK flip-flops.
    
    Circuit Design and Observations:
    We connected the clock input to all flip-flops simultaneously.
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is False
    assert "- Detected Academic Lab Report / Assignment" in res["evidence"]


def test_academic_research_paper():
    text = """
    Attention Is All You Need for Transformer Networks
    
    Abstract:
    The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.
    
    1. Introduction
    Recurrent models typically factor computation along the symbol positions of the input and output sequences.
    
    2. Related Work
    The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU.
    
    References:
    [1] Vaswani et al. IEEE Transactions on Neural Networks 2017. doi:10.1109/TNN.2017.001
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is False
    assert "- Detected Academic Research Paper" in res["evidence"]


def test_short_valid_resume():
    text = """
    Alex Mercer
    alex@mercer.dev | 555-0192 | github.com/alexm
    
    SUMMARY
    Junior Python Developer seeking entry-level backend role.
    
    PROJECTS
    Web Scraper CLI (Python, BeautifulSoup)
    Built automated scraper storing data in SQLite.
    
    SKILLS
    Python, SQL, Git, Linux
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is True


def test_resume_unusual_section_names():
    text = """
    SARAH JENKINS
    sarah@jenkins.io
    
    CAREER HISTORY
    Senior Data Engineer at Acme Analytics (2021 - Present)
    Maintained PySpark data pipelines on AWS EMR.
    
    ACADEMIC BACKGROUND
    MS Data Science, UC Berkeley (2019 - 2021)
    
    CORE COMPETENCIES
    PySpark, SQL, Airflow, Docker, Python
    """
    res = resume_validator.validate(text)
    assert res["is_resume"] is True
    assert "+ Found Experience Section" in res["evidence"]
    assert "+ Found Education Section" in res["evidence"]
    assert "+ Found Skills Section" in res["evidence"]
