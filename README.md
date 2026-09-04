# Job Search Intelligence System

A full-stack application for discovering, organizing, and analyzing entry-level software engineering opportunities.

## About

As I venture through this new grad job search era of my life, I've realized just how many roles I'm missing out on because I'm simply not searching in the right key words. Similar roles appear under many different titles, the same job may appear on multiple job boards, and it can be difficult to distinguish genuinely entry-level positions from jobs that require several years of experience, even for LinkedIn and Handshake's job board filters and search engines.  

This project aims to make that process easier by building a system that collects and normalizes job postings, identifies positions suitable for new graduates, tracks applications, and provides insights into the entry-level software engineering job market.

The initial focus is on software engineering opportunities in the Chicago area (though I intend on being able to make this project configurable to any city ASAP)

## Planned Features

* Store and organize software engineering job postings
* Normalize inconsistent job titles
* Identify positions likely to be suitable for new graduates
* Explain why a position was classified as entry-level
* Filter jobs by company, title, location, and suitability
* Detect duplicate job postings
* Track applications and interview progress
* Analyze new job openings over time
* Identify commonly requested technologies and skills
* Rank opportunities based on candidate preferences and skills

## Planned Tech Stack

**Frontend**

* React
* TypeScript

**Backend**

* Python
* FastAPI

**Database**

* PostgreSQL

**Infrastructure**

* Docker
* AWS

## Development Roadmap

### Phase 1 — Core API

Build the backend foundation for storing and managing job postings.

* FastAPI application
* PostgreSQL database
* Job data model
* CRUD API
* Database migrations
* Automated tests

### Phase 2 — Job Intelligence

Add logic for understanding job postings.

* Job title normalization
* Entry-level suitability scoring
* Explainable classification
* Filtering and search
* Duplicate detection

### Phase 3 — Frontend

Build an interface for exploring jobs and tracking applications.

* Job dashboard
* Search and filtering
* Job details
* Application tracking
* Market statistics

### Phase 4 — Job Ingestion

Create a modular ingestion system for importing job postings from permitted sources.

* JSON/CSV imports
* Public APIs and job feeds
* Source adapters
* Duplicate detection across sources

### Phase 5 — Job Market Analytics

Use historical job data to understand hiring trends.

Examples include:

* New entry-level SWE jobs per week
* Hiring trends over time
* Companies hiring the most entry-level engineers
* Most requested technologies
* Application and interview conversion rates

### Phase 6 — Deployment

Deploy and operate the application using AWS.

Potential components include:

* AWS RDS
* AWS compute services
* S3
* CloudWatch
* CI/CD

## Current Status

**Early development**

The project is currently being designed and the initial backend architecture is being built.

## Motivation

This project started from a simple question:

> How many genuinely new entry-level software engineering jobs are opening each week?

Answering that accurately requires more than searching a job board. Job titles are inconsistent, postings are duplicated, experience requirements vary, and openings appear across many different sources.

The goal of this project is to turn that messy job-search data into useful information for new software engineers.
