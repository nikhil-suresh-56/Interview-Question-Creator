from langchain.document_loaders import PyPDFLoader 
from langchain.docstore.document import Document 
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI 
from langchain_openai import ChatOpenAI 
from langchain.prompts import PromptTemplate 
from langchain.chains import load_summarize_chain 
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.vectorstores import FAISS 
from langchain.chains import RetrievalQA  
from src.prompt import *
import os 
from dotenv import load_dotenv 

# OpenAI Authentication 
load_dotenv()
OpenAI_api_key = os.environ.get('OPENAI_API_KEY') 
os.environ['OPENAI_API_KEY'] = OpenAI_api_key  

def file_processing(filepath):
    # Load data from PDF
    loader = PyPDFLoader(filepath)
    data = loader.load()

    question_gen = ""
    for page in data:
        question_gen += page.page_content
    
    splitter_ques_gen = TokenTextSplitter(
    model_name = 'gpt-3.5-turbo', 
    chunk_size = 10000,
    chunk_overlap = 200 
)

    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)
    document_ques_gen = [Document(page_content = t) for t in chunks_ques_gen] 
    splitter_ans_gen = TokenTextSplitter(

        model_name= "gpt-3.5-turbo",
        chunk_size = 1000,
        chunk_overlap = 100

)

    document_answer_gen = splitter_ans_gen.split_text(document_ques_gen) 

    return document_ques_gen, document_answer_gen 


def llm_pipeline(file_path):

    document_ques_gen, document_answer_gen = file_processing(file_path)

    llm_ques_gen_pipeline = ChatOpenAI(
        temperature = 0.3, 
        model= "gpt-3.5-turbo"
    )

    PROMPT_QUESTIONS = PromptTemplate(template = prompt_template, input_variable =['text']) 
    REFINE_PROMPT_QUESTIONS = PromptTemplate(
    input_variable =['existing_answer', 'text' ] ,
    template = refine_template)

    ques_gen_chain = load_summarize_chain (
    llm = llm_ques_gen_pipeline, 
    chain_type = "refine", verbose = False, 
    question_prompt = PROMPT_QUESTIONS, refine_prompt = REFINE_PROMPT_QUESTIONS)

    ques = ques_gen_chain.run(document_answer_gen) 
    
    embedding_model = OpenAIEmbeddings() 

    vectro_store = FAISS.from_documents (document_answer_gen, embedding_model) 

    llm_answer_gen = ChatOpenAI(temperature= 0.1, model = "gpt-3.5-turbo")  

    ques_list = ques.split ("\n") 

    filtered_ques_list = [element for element in ques_list if element.endswith ("?") or element.endswith(".")]

    answer_generation_chain = RetrievalQA.from_chain_type (llm= llm_answer_gen,  chain_type = "stuff", 
                                                       retriever = vectro_store.as_retriever()) 
    
    return answer_generation_chain , filtered_ques_list 