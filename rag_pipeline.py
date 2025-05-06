from haystack import Pipeline
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators.openai import OpenAIGenerator
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

class RAGPipeline:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.prompt_template = """
           You are PerceptoAI, {{user_name}}'s helpful AI assistant. You are given a statement or question from {{user_name}} and a set of relevant documents.
            
            First, determine if this is a question or statement:
            - If it's a question: Respond with 'question' followed by your answer
            - If it's a statement: Respond with 'statement' followed by your acknowledgment
            
            If the input is a question:
            - Analyze the retrieved documents to find relevant information
            - Generate a friendly and concise answer based on the info you have
            - If no relevant info is found, generate a helpful response based on general knowledge
            
            If the input is a statement:
            - Acknowledge the new information
            - Save it to your knowledge base
            - Respond naturally to show understanding
            
            Format your response as:
            - For questions: 'question: [your answer]'
            - For statements: 'statement: [your acknowledgment]'
            
            Do not mention 'documents' in your response.
            
            Retrieved Information:
            {% for document in documents %}
                {{document.content}}
            {% endfor %}

            Input: {{query}}
        """

        self.document_store = ChromaDocumentStore(persist_path="databases/chroma_db", collection_name="conversations")
        self.embedder = OpenAITextEmbedder(model="text-embedding-3-large")
        self.chroma_retriever = ChromaEmbeddingRetriever(document_store=self.document_store)
        self.prompt_builder = PromptBuilder(template=self.prompt_template)
        self.generator = OpenAIGenerator(model="gpt-4o-mini")

        self.pipeline = Pipeline()
        self.pipeline.add_component("query_embedder", self.embedder)
        self.pipeline.add_component("retriever", self.chroma_retriever)
        self.pipeline.add_component("prompt", self.prompt_builder)
        self.pipeline.add_component("generator", self.generator)

        self.pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
        self.pipeline.connect("retriever.documents", "prompt.documents")
        self.pipeline.connect("prompt", "generator")

    def process_query(self, query: str, top_k: int = 5):
        """Process a query through the RAG pipeline"""
        result = self.pipeline.run(
            {
                "query_embedder": {"text": query},
                "retriever": {"top_k": top_k},
                "prompt": {"query": query, "user_name": self.user_name},
            },
            include_outputs_from="retriever"
        )
        
        print("\nRetrieved Documents:")
        print(result['retriever']['documents'])
        
        full_response = result["generator"]["replies"][0]
        
        if full_response.startswith('question: ') or full_response.startswith('Question: '):
            prompt_type = 'question'
            content = full_response[len('question: '):].strip()
        elif full_response.startswith('statement: ') or full_response.startswith('Statement: '):
            prompt_type = 'statement'
            content = full_response[len('statement: '):].strip()
        else:
            prompt_type = 'unknown'
            content = full_response

        print("Prompt type:", prompt_type)
        print("Content:", content)

        return {
            "answer": content,
            "prompt_type": prompt_type
        }
        
