from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum
from langchain.chains import LLMChain
from langchain_community.chat_models import BedrockChat  # Updated import
from langchain.prompts import PromptTemplate
import boto3
import os

# Initialize AWS Bedrock client
try:
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'ap-south-1')  # Default to 'ap-south-1'
    )
except Exception as e:
    raise RuntimeError("Failed to initialize AWS Bedrock client. Check your AWS credentials.") from e

# Define the LLM
model_id = "anthropic.claude-3-haiku-20240307-v1:0"
try:
    llm = BedrockChat(
        model_id=model_id,
        client=bedrock_client,
        model_kwargs={"temperature": 0.9, "max_tokens": 2000}
    )
except Exception as e:
    raise RuntimeError("Failed to initialize BedrockChat. Check your model configuration.") from e

# Chatbot Function
def my_chatbot(language: str, freeform_text: str) -> str:
    """
    Handles chatbot logic with the specified language and input text.
    """
    try:
        # Define prompt template
        prompt = PromptTemplate(
            input_variables=['language', 'freeform_text'],
            template="You are a chatbot. You respond in {language}.\n\n{freeform_text}\n\n",
        )
        
        # Build chain
        bedrock_chain = LLMChain(llm=llm, prompt=prompt)
        response = bedrock_chain({'language': language, 'freeform_text': freeform_text})
        
        # Return the response text
        return response.get('text', "No response generated.")
    except Exception as e:
        raise RuntimeError(f"Chatbot processing failed: {str(e)}") from e

# Define FastAPI app
app = FastAPI()

# Simple test endpoint
@app.get("/")
async def read_root():
    """
    Simple endpoint to test if the API is working.
    """
    return {"message": "API is running!"}

# Define input data model
class ChatRequest(BaseModel):
    language: str
    freeform_text: str

# Chatbot endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    API endpoint to interact with the chatbot.
    """
    try:
        response_text = my_chatbot(request.language, request.freeform_text)
        return {"response": response_text}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add AWS Lambda compatibility
handler = Mangum(app)
