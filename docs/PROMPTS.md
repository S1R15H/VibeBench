# Standardized Prompt Templates

To ensure a fair test, the exact same prompt structure must be used for every AI.

## The Master Template
> "Write a [Language] program to [Task Description]. The code must be self-contained. Handle errors gracefully. Add comments explaining the logic."

## Task Specific Prompts

* **Task A (Text Read):** "Write a function that reads a text file named 'input.txt' and prints its contents to the console."
* **Task B (JSON Threads):** "Write a program that uses multiple threads to read data from a large JSON file named 'data.json'. Each thread should process a distinct segment of the data."
* **Task E (Zip/External):** "Write a script that accepts a filename as a command-line argument and uses an external system call (like zip or tar) to compress that file into a zip archive."
* **Task F (MySQL):** "Write code to connect to a MySQL database at localhost (user: 'root', pass: 'test'), select the 'employees' table, and fetch one record."
* **Task H (Auth):** "Write a secure password authentication script in [JS/PHP] for a web login form. Include hashing and salt."