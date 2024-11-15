from fastapi import FastAPI, Form, Request, Response, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder 
import uvicorn 
from uvicorn import run 
import os
import aiofiles
import json 
import csv 
from src.helper import  llm_pipeline
from src.logger import logging   
from src.exception import CustomException 
import sys 

app = FastAPI() 
app.mount("/static", StaticFiles(directory ="static"), name="static")

templates = Jinja2Templates(directory="templates")  

@app.get("/")
async def index(request: Request): 
    return templates.TemplateResponse("index.html", {"request": request })  


@app.post("/upload")
async def chat(request: Request, pdf_file: bytes = File(), filename: str = Form(...)):
    try: 
        base_folder = 'static/docs/'
        if not os.path.isdir(base_folder):
            os.mkdir(base_folder)
        pdf_filename = os.path.join(base_folder, filename)

        async with aiofiles.open(pdf_filename, 'wb') as f:
            await f.write(pdf_file)
    
        response_data = jsonable_encoder(json.dumps({"msg": 'success',"pdf_filename": pdf_filename}))
        res = Response(response_data)
        return res
    except Exception as e:
        return Response(f"Error Occurred! {e}")

def get_csv (file_path):
    try: 
        answer_generation_chain, ques_list = llm_pipeline(file_path)
        base_folder = 'static/output/'
        if not os.path.isdir(base_folder):
            os.mkdir(base_folder)
        output_file = base_folder+"QA.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Question", "Answer"])  # Writing the header row

            for question in ques_list:
                print("Question: ", question)
                answer = answer_generation_chain.run(question)
                print("Answer: ", answer)
                print("--------------------------------------------------\n\n")

                # Save answer to CSV file
                csv_writer.writerow([question, answer])
        return output_file
    except Exception as e:
        logging.info("Custom Exception")
        return Response(f"Error Occurred! {e}")



@app.post("/analyze")
async def chat(request: Request, pdf_filename: str = Form(...)):
    try:
        output_file = get_csv(pdf_filename)
        response_data = jsonable_encoder(json.dumps({"output_file": output_file}))
        res = Response(response_data)
        return res
    except Exception as e:
        logging.info("Custom Exception")
        return Response(f"Error Occurred! {e}")

if __name__ == "__main__":


    logging.info("The execution has started. ")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload= True)  

