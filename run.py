from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
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
custom_prompt_template = """Bạn là một trợ lý ảo của trường Đại học công nghệ thông tin và truyển thông Thái Nguyên. Được phát triển bởi nhóm 
sinh viên lớp học máy K19 Kỹ thuật phần mềm. Nhóm phát triển gồm: Hải, Đức, Bình, Kiên, Trung.Bạn có nhiệm vụ trả lời các thắc mắc của sinh viên 
từ những thông tin trong cuốn sổ tay sinh viên.
Hãy sử dụng các thông tin sau đây để trả lời câu hỏi của người dùng.
Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết, đừng cố bịa ra câu trả lời.
Tất cả câu trả lời của bạn đều phải trả lời bằng tiếng việt
Câu trả lời ngắn gọn,đầy đủ, độ dài không quá 500 ký tự.

Context: {context}
Question: {question}
"""
prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

embeddings = OpenAIEmbeddings()
# Initialize LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("langchain-stsv")

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')
    print(question)
    # Lấy thông tin context từ Pinecone

    
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    result = vector_store.similarity_search(question)

    context = " ".join([doc.page_content for doc in result])
    
    # Tạo câu trả lời từ LLM chain
    answer = chain.run({"context": context, "question": question})
    
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000)) 
    app.run(debug=True, host="0.0.0.0", port=port)
