# DATABASE_PROJECT
For CSCI_6623_81 Database Systems 

SQL Injection Prevention & Detection / User Authentication & Access Control System

Database dealing with Banks (ex. BofA, Chase, Capital One)

SQL Injection Prevention & Detection
•	Build a database system that simulates SQL injection attacks and implement security measures to prevent them.
•	Front-end: A basic web application (HTML/CSS, Python Flask, or PHP).
•	Store logs of SQL queries to detect possible attacks.

•	Problem Statement: Many web applications are vulnerable to SQL Injection attacks, where an attacker manipulates queries to gain unauthorized access.
•	SQL Use Case: Store logs of queries, analyze patterns of SQL injections, and prevent attacks with parameterized queries.
•	Dataset: Simulated attack logs or open-source SQL Injection datasets.



User Authentication & Access Control System
•	Create a secure authentication system with role-based access control (RBAC).
•	Implement password hashing (BCrypt, SHA-256) in your database.
•	Front-end: A login system (Python Flask/Django or PHP).

•	Problem Statement: Organizations need to track security incidents (failed logins, malware attacks, unauthorized access attempts).
•	SQL Use Case: Store security event logs and create queries that identify unusual activity.	
•	Dataset: Kaggle’s Cybersecurity datasets (e.g., network traffic logs, authentication logs).



•	Kaggle (https://www.kaggle.com/) – Search for Cybersecurity, Network Security, Intrusion Detection datasets.
•	CVE Database (https://cve.mitre.org/) – Public vulnerabilities.
•	CICIDS 2017 Dataset – Intrusion Detection dataset with real-world attacks.


Define Your Database Requirements
•	Entities (Tables) – What data do you need to store? (e.g., users, logs, threats, malware samples).
•	Relationships (ERD Diagram) – How do tables connect? (e.g., Users → Login Attempts, Threats → IP Addresses).
•	Queries Needed – What SQL queries will help analyze the data? (e.g., “Show all failed login attempts in the last 24 hours”).



Example Problem Statement for Report

💡 “Our project addresses the issue of unauthorized login attempts in enterprise networks. We have created an SQL-based authentication system that logs failed login attempts and analyzes suspicious activity patterns. The database stores user roles, timestamps, and login details. Using Oracle SQL queries, we detect brute-force attacks and unauthorized access attempts.” 💡
