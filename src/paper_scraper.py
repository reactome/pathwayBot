#from metapub.convert import pmid2doi
from metapub import FindIt
from metapub import PubMedFetcher
#from metapub import CrossRefFetcher
from metapub import exceptions
from urllib.request import urlretrieve

import pandas as pd
import os

import requests

class PaperScraper:

    def __init__(self, pdfRoot = "papers"):
        self.pdfRoot = pdfRoot
        if not os.path.exists(self.pdfRoot):
            os.mkdir(self.pdfRoot)
        self.csv_file = "/".join([self.pdfRoot,'metainfo.csv'])
        self.metadf = pd.DataFrame()
        if os.path.isfile(self.csv_file):
            self.metadf = pd.read_csv(self.csv_file)



    ## having the pubmedid returns the PMA containing all the paper meta information including the url to its PDF if OA
    def scrape_metainfo(self, pmid):
        ## get metainfo of the paper using pubmedid
        passed=False
        tries=0
        maxTries=5
        while not passed:
            try:
                pma = PubMedFetcher().article_by_pmid(pmid)
                passed = True
            except exceptions.MetaPubError as e:
                print(e)
                if tries == maxTries:
                    passed = True
                tries+=1
                pass
        return pma.to_dict()
    
    ## example:
    ## url: 'https://onlinelibrary.wiley.com/doi/pdf/10.1002/jcb.20409'
    ## output_name: 15723341.pdf
    def store_pdf(self, url, output_name):
        r = requests.get(url)
        if r.headers.get('content-type') == 'application/pdf':
            directory = os.path.join(self.pdfRoot, "pdfs")
            if not os.path.exists(directory):
                os.mkdir(directory)
            print( "url: ", url)
            print("file name: ", "/".join([directory,output_name]))
            urlretrieve(url, "/".join([directory,output_name]))
        else:
            print(f'pdf {output_name} not available in url {url}.')

    def fetch_pdf_if_exists(self, pmid):
        print("Storing metadata for pmid:", pmid)
        src = FindIt(pmid)
        if src.url is None: 
            print("Paper's pdf was not accessible. Reason:")
            print(src.reason)
            for s in src.reason.split(' '):
                if s.startswith('http') or s.startswith("(http"):
                    s = s.replace('(', '').replace(')', '')
                    print(s)
                    self.store_pdf(s, f'{pmid}.pdf')
                    break
        else:
            self.store_pdf(src.url, f'{pmid}.pdf')

    def scrape_all(self, pmidlist, query="", fetchPDF=True):
        self.pmas = []
        for pmid in pmidlist:
            pmid = pmid.strip()
            print("pmid: ", pmid)
            pma = self.scrape_metainfo(pmid)
            if fetchPDF:
                self.fetch_pdf_if_exists(pmid)
            self.pmas.append(pma)
        newList = pd.DataFrame.from_records(self.pmas)
        newList["query"] = query
        print("len(newList):", len(newList))
        print("len(previousList):", len(self.metadf))
        self.metadf = pd.concat([newList,self.metadf])
        self.metadf.drop_duplicates('doi', inplace=True)
        print("len(concatenated):", len(self.metadf))

    def write_meta(self):
        self.metadf.to_csv(self.csv_file, index=None)
            
