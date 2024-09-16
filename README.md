[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.


We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.

- [x] My code's working just fine! 🥳
- [x] I have recorded a video showing it working and embedded it in the README ▶️
- [x] I have tested all the normal working cases 😎
- [x] I have even solved some edge cases (brownie points) 💪
- [x] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.

## Developer's Section

# Google Sheets and SQL Real-Time Synchronization
[Video](https://drive.google.com/drive/folders/1lmAEWa8p8Pih5NLcMsTF5x5qn0W05UXP?usp=sharing)


## Overview

This project provides a real-time synchronization solution between Google Sheets and SQL databases. It ensures that updates made in either Google Sheets or SQL are reflected instantly in the other platform. The solution is designed to be scalable and handle a large number of tables and rows.

### Scripts Overview

1. **sheets_to_mysql.py**
   - **Purpose**: Handles the initial transfer of Google Sheets data to an SQL database.
   - **Functions**:
     - Creates SQL tables from Google Sheets.
     - Populates tables with initial data.
     - Creates triggers for handling real-time synchronization (e.g., `AFTER INSERT`, `AFTER DELETE`, `AFTER UPDATE`).
     - Creates a log table to monitor changes for real-time updates.
     
2. **Code.gs (Google Apps Script)**
   - **Purpose**: Manages real-time synchronization when edits are made in Google Sheets.
   - **Functions**:
     - Uses the `onEdit()` trigger, an in-built Google Apps Script function, to detect changes in Google Sheets.
     - Connects to the SQL database via JDBC, which requires a hosted database (a free deployment server is used in this case).
     - Handles two main cases:
       1. Changes in column names.
       2. Changes in row values.
     - Includes a `testOnEdit()` function to simulate the behavior of `onEdit()` without needing to deploy it as a live trigger.
   
3. **mysql_to_sheets.py**
   - **Purpose**: Acts as a server to continuously monitor changes in SQL and synchronize them with Google Sheets.
   - **Functions**:
     - Monitors the log table in SQL for changes.
     - Ensures real-time synchronization from SQL to Google Sheets when changes are detected.
     - Deletes the log entries once synchronization is complete.
4. **trial.ipynb**(Not used in the final product)
    - **Purpsoe**: This file is utilized to explore and understand the concepts to be implemented. It serves as a testing and debugging tool for outputs before final implementation.

### Key Features and Edge Cases

- **Change in Column Names**: Handles changes in column names seamlessly, ensuring that both the Google Sheets and SQL schema remain in sync.
  
- **Bidirectional Synchronization**: Prevents feedback loops where changes from Google Sheets to SQL could trigger redundant updates from SQL back to Google Sheets.
  
- **Scalability**: Designed to handle large datasets with numerous tables and rows while maintaining near real-time synchronization.

### Deployment Notes

- **Google Sheets App Script Setup**: 
  - Use the `Code.gs` script to manage Google Sheets changes.
  - Refer to `scripts.txt` for instructions on how to open Google Apps Script from Google Sheets.
  
- **SQL Database**: 
  - A hosted SQL server is required for the JDBC connection from the Google Apps Script.

## Conclusion

This solution provides a reliable and scalable method to synchronize Google Sheets and SQL databases in real time. By handling edge cases such as column name changes and preventing unnecessary triggers, it ensures efficient synchronization across platforms.

## Thought process behind the solution

I began by focusing on transferring data from Google Sheets to SQL, which led to the creation of sheets_to_mysql.py. This script performs a one-time synchronization of data from Sheets to SQL. To achieve real-time synchronization, I explored various methods, including using a log table and Google Apps Script. Although the log table seemed like a viable option initially, it wasn’t scalable. This led me to use Apps Script to connect to the SQL database via JDBC, which brought me closer to real-time synchronization.

Next, I tackled the problem of synchronizing SQL data back to Google Sheets. Since the SQL database is already set up for the spreadsheet, the next step was to create triggers to update the Google Sheets. However, I encountered two main issues:

Python functions cannot be executed via triggers.
Triggers run on any change, including those made directly in Google Sheets, leading to unnecessary executions.
To address these issues, I decided to use a combination of a log table and a global variable table. The global variable is used to control the execution of triggers. When an update occurs from Google Sheets, the global variable is set to 0, indicating that synchronization is in progress. Once the update is complete, the variable is set back to 1. This approach helps manage the synchronization process more effectively.
