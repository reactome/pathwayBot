from paper_scraper import PaperScraper
from pdf_manager import PDFManager
from metapub import PubMedFetcher
import os

## todo: what ever format we support for the knowledgebase of Reactome goes in here
class PaperManager:
    def __init__(self, pdfRoot="papers"):
        self.pdfRoot = pdfRoot
        if not os.path.exists(self.pdfRoot):
            os.mkdir(self.pdfRoot)
        
        self.paperScraper = PaperScraper(pdfRoot=self.pdfRoot)

        # Initialize the list of papers
        #self.papers = self.paperScraper.metadf

    def get_papers_for_query(self, pmidFile, num_pmids=3, pmc_only=True):
        with open(pmidFile) as f:
            for query in f:
                query = query.strip()
                print(query)
                pmidList = PubMedFetcher().pmids_for_medical_genetics_query(query=query, retmax=num_pmids, pmc_only=pmc_only)
                print("pmids:")
                print(pmidList)
                self.paperScraper.scrape_all(pmidList, query)
        self.paperScraper.write_meta()

    def get_papers_using_pmidFile(self, pmidFile):
        with open(pmidFile) as f:
            # reading the file
            data = f.read()
            pmidList = data.strip().split("\n")
            self.paperScraper.scrape_all(pmidList)
            self.paperScraper.write_meta()

    def load_papers_metadata(self):
        # load papers metadata from a csv file or the db
        pass
