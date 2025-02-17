import os
from fasthtml.common import Titled, Card, Div, Group, Form, Input, Button, P, Script, Style, UploadFile, fast_app, serve
from document_qa import DocumentQA

# FastHTML app
app, rt = fast_app()

# Laadime süsteemi ja lisame esimese PDF faili
qa_system = DocumentQA()
try:
    qa_system.load_document("uploads/2025-en.pdf")
    loaded_file = "2025-en.pdf"
except Exception as e:
    print(f"Error loading initial document: {str(e)}")
    qa_system = None
    loaded_file = None

# Kataloog kasutaja failide jaoks
os.makedirs("uploads", exist_ok=True)

@rt("/")
def get():
    return Titled("Document Q&A System",
        Card(
            # Info valitud dokumendi kohta
            Div(
                P(f"Currently loaded: {loaded_file}" if loaded_file else "No document loaded"),
                style="margin-bottom: 15px;"
            ),
            Group(
                # Dokumendi üleslaadimine
                Form(
                    Input(type="file", name="file", accept=".pdf,.txt"),
                    Button("Change Document", type="submit"),
                    hx_post="/upload",
                    hx_target="#upload-status"
                ),
                Div(id="upload-status")
            ),
            # Q&A sektsioon
            Div(
                Form(
                    Input(type="text", name="question", placeholder="Ask a question about the document..."),
                    Button("Ask", type="submit", id="ask-button"),
                    hx_post="/ask",
                    hx_target="#answer",
                    id="question-form",
                    style="display: block;" if qa_system else "display: none;"
                ),
                # Spinner ootamise ajaks
                Div(
                    Div(cls="spinner-circle"),
                    id="spinner",
                    style="display: none; margin-top: 10px; text-align: center;"
                ),
                Div(id="answer", cls="answer-section"),
                style="margin-top: 20px;"
            )
        ),
        Script("""
            htmx.on('#question-form', 'htmx:beforeRequest', function(evt) {
                document.getElementById('spinner').style.display = 'block';
                document.getElementById('ask-button').style.display = 'none';
                document.getElementById('answer').innerHTML = ''; // Clear previous answer
            });
            
            htmx.on('#question-form', 'htmx:afterRequest', function(evt) {
                document.getElementById('spinner').style.display = 'none';
                document.getElementById('ask-button').style.display = 'block';
            });
        """),
        Style("""
            .answer-section {
                margin-top: 15px;
                white-space: pre-wrap;
            }
            .reference {
                font-size: 0.9em;
                color: #666;
                margin-top: 10px;
            }
            .spinner-circle {
                width: 40px;
                height: 40px;
                margin: 0 auto;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        """)
    )

@rt("/upload")
async def post(file: UploadFile):
    global qa_system, loaded_file
    
    try:
        # Salvestame üleslaaditud faili
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Laadime uue faili
        qa_system.load_document(file_path)
        loaded_file = file.filename
        
        return Div(
            P(f"✅ File {file.filename} uploaded and processed successfully"),
            Script("document.getElementById('question-form').style.display = 'block';")
        )
    except Exception as e:
        return Div(f"❌ Error processing file: {str(e)}", style="color: red;")

@rt("/ask")
def post(question: str = Form(...)):
    if qa_system is None:
        return Div("❌ Please upload a document first", style="color: red;")
    
    try:
        # Vastame küsimusele
        result = qa_system.answer_question(question)
        
        # Ja näitame vastust
        response_html = [
            Div(result['answer'])
        ]        
        return Div(*response_html)
    except Exception as e:
        return Div(f"❌ Error processing question: {str(e)}", style="color: red;")


@rt("/api/ask")
def post(question: str = Form(...)):
    # API vastamise jaoks
    if qa_system is None:
        return {"error": "Please upload a document first"}    
    try:
        result = qa_system.answer_question(question)
        response = {
            "answer": result['answer']
        }        
        return response
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    serve()
