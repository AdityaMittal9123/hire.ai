#importing the required libraries
import os
import docx
import openai
import gradio as gr
import csv
import PyPDF2
from dotenv import load_dotenv

#loading the environment file
load_dotenv()

# declaring the openai key 
openai.api_key=os.getenv('OPENAI_API_KEY')


# this function simply read resume passed to it
def read_file(file_path,JD):
        with open(file_path,'r',encoding='utf-8') as file:
            resume=file.read()
            prompt(resume,JD)


# This function contains the prompt used to train the LLM 
def prompt(resume,JD):
    prompt=f"""
        Please evaluate the suitability of the following resume  based on the job description provided below. Your evaluation should be based on
        the two evaluation criteria given below. Your answer should be very precise, giving "YES" or "NO" for each of the two criteria. If candidate
        has more years of experience than given in job description, then it should be a "YES" for fist evaluation criteria. Re-check your answer.
        If you are giving "NO" as responses, then write explanation in one sentence.
        Job Description:
        {JD}
        Resume:
        {resume}

        Evaluation:
        1. Does the candidate have an minimum experience that is mentioned in Job Description?
        2. Does the candidate have atleast two skills that is mentioned in Job Description?
        """
    generate_response(prompt)

# creating the empty list to storing the response of the model
output=[]

# generating the response to check the suitablity of the resume
def generate_response(prompt):
    response=openai.Completion.create(
    engine=os.getenv("OPENAI_MODEL"),
    prompt=prompt,
    max_tokens=400,
    temperature=0.1,
    frequency_penalty=0,
    presence_penalty=0,
    top_p=1
)
    output.append((response['choices'][0]['text']))
    print((response['choices'][0]['text']))


# shortlisting the resumes based on the specified criteria

def shortlist(response):
  shortlisted=[]
  for i,j in response.items():
    s=j.replace('\n',' ')
    if 'no' not in s.lower() :
        shortlisted.append(i)
  return shortlisted


# this is the prompt to create 5 intereview questions for the shortlisted resume

def question_prompt(resume):
  resume_fol_path='YOUR RESUME FOLDER PATHS'+'/'+resume

  if resume.endswith('.txt'):
    with open(resume_fol_path,'r',encoding='utf-8') as file:
      resume=file.read()

  elif resume.endswith('.pdf'):
    pdfFileObj = open(resume_fol_path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    print(pdfReader.numPages)
    pageObj = pdfReader.getPage(0)
    resume=pageObj.extractText()

  elif resume.endswith('.docx'):
    doc = docx.Document(resume_fol_path)
    resume = []
    for para in doc.paragraphs:
        resume.append(para.text)
  else:
    raise ValueError("File Format is not supported !")


  prompt=f"""
    You are conducting an interview for a position given in the job description below and have a possible candidate whose resume is given below.
    You have to create 5 interview question which would help you to decide whether the candidate is suitable for this job.
    You may ask technical, personal and behavioural questions that would help to arrive at the decision of selecting the candidate.
    
    Resume:
    {resume}
    You may increase the level of difficulty of  questions if required to assess the candidate.
    """
  queston=generate_question(prompt)
  return queston


# This model generate the questions for the resume

def generate_question(prompt):
    response=openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=400,
    temperature=0.1,
    frequency_penalty=0,
    presence_penalty=0,
    top_p=1
    )
    # print(response['choices'][0]['text'])
    ques=(response['choices'][0]['text'])
    return ques


# this will analyse the final score , whether the candidate is qualified or not.

def final_score(summary):

  prompt= f"""
      Given below is a conversation between a candidate and an interviewer:
      {summary}
      Now go through the following instructions and generate the output accordingly:
      You have to analyze the conversation and determine the accuracy of the candidate's answers for each individual question.
      Even if the answer is correct, properly assess the candidate's knowledge based on the provided answer.
      Based on the answers given by the candidate, give a score between 0 and 10. Where 0 denotes complete lack of knowledge of the asked topic and 10 denotes excellent knowledge of the asked topic.
      You also have to judge how the candidate reacts to tough situations based on the behavioural questions the interviewer has asked. Judge the candidate's response and give a score between 0 to 10, the score should be higher if the candidate's reaction to the situation was appropriate and justified and the score should be lower if the candidate's response was not accurate.
      Give each response of the candidate a score between 0 to 10 as instructed before and calculate the average of these scores. Show the average score as the final output along with a short and crisp summary of whether the candidate has demonstrated excellent knowledge of the asked topics or not.
      If the candidate answers like 'I don't know' or 'No idea', etc. You should give a zero score for that particular answer.
      """
  score=generate_question(prompt)
  return score


# this is the main function which reads the files of the a particular forlder path and then perform all the operations
JD=''
def main(input):
    global JD , display
    JD=input
    resume_folder_path='YOUR RESUME FOLDER PATH'
    os.chdir(resume_folder_path)
    files=os.listdir(resume_folder_path)
    count=0
    response={}

    # sending resumes one by one
    for i in files:
        break
        if i == 'cv19.txt':
          read_file(i,JD)
          response[i]=output[count]
          count+=1

    #this is the list of shortlisted resumes
    shortlisted=shortlist(response)

    display='display:none'
    return shortlisted


count=0
generated_questions=[]
def short1(input):
  global generated_questions , count
  count=0
  questions=question_prompt(input)
  generated_questions=questions.split('\n')
  print('these are the questions-------------\n',questions)
  return questions

def chatgpt_clone(input, history):
    global count , generated_questions
    generated_questions.append('Thank you for your time . click on FINAL SCORE button to know the final score !')
    count+=1
    history = history or []
    s = list(sum(history, ()))
    s.append(input)
    inp = ' '.join(s)
    if count<len(generated_questions):
      output = generated_questions[count]
    else:
      output=''
    with open('Resume_Q&A_log.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([output,input])
    history.append((input, output))
    return history, history


#this will return pass the chat history to the final_score() and then return the final score of the candidate
def final():
  
  with open('Resume_Q&A_log.csv', mode='r') as file:

    data=csv.reader(file)
    chat=[]
    for i in data:
      chat.append(i)
    lines=''
    for line in chat:
      lines=lines+line[0]+'\n'+line[1]+'\n'
    score=final_score(lines)
    return score


styling="""<html lang="en">
              <head>
                <!-- Required meta tags -->
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <!-- Bootstrap CSS -->
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                <title>hire.ai</title>
                <style>
                .nav .navbar-brand{font-size: 50px; text-decoration: none !important; font-weight: 900;}
                </style>
              </head>
              <body>
                <nav class="navbar navbar-expand navbar-light bg-light" style="background: linear-gradient(90deg, rgba(95,30,190,1) 10%, rgba(60,145,255,1) 50%);height:50px !important">
              <h1 class="navbar-brand text-white mb-3"> hire.ai</h1>
              </nav>
              <div class='mt-2  d-flex justify-content-center text-white' style="font-size:16px !important">Welcome to the Resume shortlisting System </div>
                <!-- Optional JavaScript -->
                <!-- jQuery first, then Popper.js, then Bootstrap JS -->
                <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
              </body>
              </html>
          """

# This is main gradio code which is used to gave a User interface
css = """
.gradio-container {background-color: #e9eaed}
"""

display='display:none'
block = gr.Blocks(css=css)
with block:
    gr.Markdown(styling)


    resume_path=gr.Textbox(label="Enter the Job Description",placeholder='Enter the Job Description to get the shortlisted resumes')
    resume_button=gr.Button("Shortlist Resumes")
    short=gr.Textbox(label="Resume Name ",placeholder='Enter the shortlisted resume name to generate the asnwers')

    shortlisted_button=gr.Button("Generate Questions")
    resume_button.click(main,inputs=[resume_path],outputs=[resume_path])
    shortlisted_button.click(short1,inputs=[short],outputs=[short])

    chatbot = gr.Chatbot()
    message = gr.Textbox(label="Type your answer here",placeholder="Should we begin")
    state = gr.State()
    with gr.Row():
      submit = gr.Button("SEND",visible=True,elem_classes="feedback")
      clear = gr.ClearButton([message,chatbot],elem_classes="feedback")
    finalScore = gr.Textbox(label="Final Score",placeholder="Final score of the candidate")
    score_button=gr.Button("Final Score")
    submit.click(chatgpt_clone, inputs=[message, state], outputs=[chatbot, state])
    clear.click(lambda: None, None , chatbot,)
    score_button.click(final,inputs=[],outputs=[finalScore])


block.launch(debug = True)
