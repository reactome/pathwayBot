from paper_scraper import PaperScraper
from metapub import PubMedFetcher
import os
import time
from metapub.cite import *
import pandas as pd

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
                if not pmc_only:
                    time.sleep(10)
                print("pmids:", pmidList)
                ### Only go through the pdf download process if the search is restricted to OA papers from PMC
                self.paperScraper.scrape_all(pmidList, query, fetchPDF=pmc_only)
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
        self.metadata = pd.read_csv()
        pass

    def create_citation_from_meta(self, paper_txt):
        pmid=int(paper_txt.metadata['source'].split('/')[-1][:-4].strip())
        pmadict = self.metainfo[self.metainfo['pmid'] == pmid]
        for key in pmadict.columns:
            if key not in ['xml','abstract']:
                paper_txt.metadata[key] = str(pmadict[key].values[0])
        paper_txt.metadata['authors'] = paper_txt.metadata['authors'].replace("[", "").replace("]", "").replace("'", "").split(',')
        paper_txt.metadata['citation'] = citation(
        authors=paper_txt.metadata['authors'],
        title=paper_txt.metadata['title'],
        journal=paper_txt.metadata['journal'],
        year=paper_txt.metadata['year'], 
        volume=paper_txt.metadata['volume'],
        pages=paper_txt.metadata['pages'],
        doi=paper_txt.metadata['doi'])
        if len(paper_txt.metadata['authors']) <= 2:
            paper_txt.metadata['authoryear-comp'] = \
            ' and '.join(paper_txt.metadata['authors']) + ' (' + str(paper_txt.metadata['year']) + ')'
        else:
            paper_txt.metadata['authoryear-comp'] = \
            paper_txt.metadata['authors'][0] + ' et. al. (' + str(paper_txt.metadata['year']) + ')'
        return paper_txt