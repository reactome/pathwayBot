
from langchain.document_loaders import DirectoryLoader
#from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from summary_generator import SummaryGenerator

## Manages PDFs
## loads
## splits
## embeds
## 
class PDFManager:
    def __init__(self, pdfRoot = "papers"):
        self.pdfRoot = pdfRoot
        self.pdfs = []
        self.index = {}
        self.embeddings = OpenAIEmbeddings()
        self.embeddb = Chroma.from_documents("initializer", self.embeddings)
        self.summarizer = SummaryGenerator()

    # Given a list of pdf names under pdfRoot, load them all
    def load_pdfs(self, pdfList):
        loader = DirectoryLoader(f'{self.pdfRoot}', glob = '|'.join(pdfList), loader_cls=PyMuPDFLoader, show_progress=True)
        self.pdfs = loader.load()
        # Confirm correct number of documents loaded
        print(f"# of pdfs:{len(pdfList)} , # of loaded docs:{len(self.pdfs)}")


    def split_pdfs(self):
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
        self.pdfs = text_splitter.split_documents(self.pdfs)

    def embed_pdfs(self):
        self.embeddb = Chroma.from_documents(self.pdfs, self.embeddings)

    def summarize_pdfs(self, title):
        self.summary = self.summarizer.generate_summary(title, self.pdfs)
