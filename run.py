from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from pinecone import Pinecone, ServerlessSpec
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings import OpenAIEmbeddings
from flask_cors import CORS

# Load environment variables
load_dotenv(find_dotenv())

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize LLM
llm = OpenAI()

# Define prompt template
custom_prompt_template = """Bạn là một trợ lý ảo của trường Đại học Công nghệ Thông tin và Truyền thông Thái Nguyên. 
Bạn có nhiệm vụ trả lời các thắc mắc của sinh viên từ những thông tin trong cuốn sổ tay sinh viên.
Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết, đừng cố bịa ra câu trả lời.
Tất cả câu trả lời của bạn đều phải trả lời bằng tiếng Việt.
Câu trả lời ngắn gọn, đầy đủ, độ dài không quá 500 ký tự.

Context: {context}
Question: {question}
"""
prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Initialize Pinecone client
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

# Check if index exists, create if not
index_name = "langchain-stsv"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=1536,  # Chỉnh theo embedding bạn dùng
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-west-2')
    )

# Lấy index
index = pc.Index(index_name)

# Initialize LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')
    print(f"User question: {question}")

    # Lấy thông tin context từ Pinecone
    vector_store = PineconeVectorStore(index=index, embedding_function=embeddings.embed_query)
    result = vector_store.similarity_search(question)

    context = " ".join([doc.page_content for doc in result])
    
    # Tạo câu trả lời từ LLM chain
    answer = chain.run({"context": context, "question": question})
    
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000)) 
    app.run(debug=True, host="0.0.0.0", port=port)
