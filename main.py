from langchain.chains import LLMChain
from langchain_community.chat_models import BedrockChat  # Updated import
from langchain.prompts import PromptTemplate
import boto3
import os

# Set AWS Profile for credentials
os.environ['AWS_PROFILE'] = 'AWSIAM'

# Initialize AWS Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

# Define the LLM
model_id = "anthropic.claude-3-haiku-20240307-v1:0"
llm = BedrockChat(
    model_id=model_id,
    client=bedrock_client,
    model_kwargs={"temperature": 0.9, "max_tokens": 2000}
)

# Chatbot Function
def my_chatbot(language, freeform_text):
    # Define prompt template
    prompt = PromptTemplate(
        input_variables=['language', 'freeform_text'],
        template="You are a chatbot. You respond in {language}.\n\n{freeform_text}\n\n",
    )
    
    # Build chain
    bedrock_chain = LLMChain(llm=llm, prompt=prompt)
    response = bedrock_chain({'language': language, 'freeform_text': freeform_text})
    
    # Return the response text
    return response['text']  # Ensure the correct key here if it's different

# Test the chatbot
print(my_chatbot("english", "What is the largest country in the world?"))
