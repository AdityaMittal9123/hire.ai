# hire.ai
### A Resume shortlisting and QA tool using LLM Model

hire.ai is a LLM tool which can help a recruiting company to shortlist the resume based on a particular JD using GEN AI capability.
* We will pass the resumes one by one to the LLM which will check if the candidate is suitable for the job or not.
* We have to provide a prompt defining all the criteria to find the suitable candidate so that LLM can give more accurate response.

hire.ai can also generate some questions related to the skills mentioned in the resume which will help the recruiter to get initial screening done.
* This tool asks 4-5 questions to the user and store the responses in the log file.
* After that, it will generate a summary about the user performance according to the answer he gave for each question.
* He will also give you the rating of the candidate.

### Steps to run the code 

1. Clone the repo in your system
2. Create a new dedicated virtualenv
3. run the requirements.txt file in that venv which will install all the libraries required in this tool.
4. create a .env file in the same location of your main code file ( name should be ".env" only)
5. define all your credentials (openai_key , openai_model_name etc) in the .env file
6. pass your resume folder path in main() and question_prompt()

Tadaah..!
your tool is ready to run....
