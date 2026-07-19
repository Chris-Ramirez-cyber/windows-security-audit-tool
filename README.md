# Windows Security Audit Tool
This tool is a python based Windows security audit tool that collects system, network, process, software, Windows Defender, firewall, network connection, and service information from your device for you to analyze

## Overview
As a student who is studying cybersecurity, I built this tool to better understand Python and security concepts by building a tool that gathers security information from a Windows system. The information collected is organized into a report that can be reviewed after to better understand the systems configuration and activity.

## Features
-System information\n
-Network information
-Running processes
-Installed software
-Windows Defender status
-Windows Firewall status
-Open network connections
-Windows services
-Saves collected audit information to a text report

## Requirements
-Windows OS
-Python 3
-psutil

## Usage
Run the Python script to perform the Windows security audit. Once the audit is complete, the collected information will be saved to `audit_report.txt` for review.
