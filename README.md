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

2. CRUD Operations

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
- [X] I have recorded a video showing it working and embedded it in the README ▶️
- [x] I have tested all the normal working cases 😎
- [ ] I have even solved some edge cases (brownie points) 💪
- [X] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓

Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries.

All the best ✨.

## Developer's Section

_Add your video here, and your approach to the problem (optional). Leave some comments for us here if you want, we will be reading this :)_

### Working of the project :  

https://github.com/user-attachments/assets/a9bbf586-b932-480f-b399-cc533ebfc7d0  

### My approach : 
i)I created a project in google cloud platform and emabled OAuth , Google Sheets API and Google Drive API. 
ii)After that , I downloaded the client_secrets.json to uniquely verify myself. 
iii)The algorithm that I followed before getting the program ready is as follows : 

a)Maintain two variables each for the spreadsheet and database . 
b)If current_db_data == previous_db_data but current_sheet_data is not equal to previous_sheet_data: 
    then a deletion or addition has occured in the sheet , and the change (either deletion or addition) has to be replicated in the DB as well. (I had been doing it synchronously , but I feel 
    asynchronous updation is the best approach. I used synchronous method because that was more easy to debug). 
    c)If (current_db_data!=previous_db_data but current_sheet_data is equal to previous_sheet_data): 
          Change has occured in DB and it has to be replicated in the sheet. 
    d) Make the change and return from the function. 
    e) Run the main.py script again to listen for changes. 
This is a rough approach I followed. The video contains the demonstration of my project. 
#### PS: I forgot to mention what was the most challenging part I faced since there was a time constraint of 2 minutes and I had to shorted my explanation. The most challenging part of the assignment was the updation part. I felt that the deletion and addition of records is fairly straight forward but I had to come up with the logic of updation by myself because GPT/Claude aren't that smart yet to solve the bugs I faced :) . The code for the updation logic is in the main.py(line 112 to 123) and the entire updateFunctionality.py file. 

iv) That is the crux of the algorithm I used. I created a .env file to store the environment variables such as client secrets , spreadsheet ID(This, I obtained from the URL of the spreadsheet) ,the credentials of the instance of MySQL database in my local machine. 
v)I used the os library to import the required environment variables. 
vi)The list of libraries I used are : 
  logging(to log data into my console) , mysql.connector (to make a connection between the MySQL database and my python program) , gspread(to establish a connection between my python program and the google spreadsheet , os(to read the environment variables) and dotenv(to load the environment variables from the .env file to the python program). 
vii)I was not able to solve all the edge cases as figuring out why the error occured and the solution for the updation part of the solution took almost 8 hours to me. But eitherways , I am happy I learnt a lot. 
Thank you for this opportunity ! 
