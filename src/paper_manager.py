from paper_scraper import PaperScraper
from pdf_manager import PDFManager

## todo: what ever format we support for the knowledgebase of Reactome goes in here
class PaperManager:
    def __init__(self):
        # Initialize the list of papers
        self.papers = []

    def index_papers(self):
        # Index and embed the papers using Langchain
        pass

    def store_papers(self):
        # loads papers from db
        pass

    def scrape_papers_metadata(self):
        # scrape papers from web
        pass

    def scrape_papers(self):
        # scrape papers from web
        pass

    def load_papers_metadata(self):
        # load papers metadata from a csv file or the db
        pass
