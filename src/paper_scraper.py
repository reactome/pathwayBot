#from metapub.convert import pmid2doi
from metapub import FindIt
from metapub import PubMedFetcher
#from metapub import CrossRefFetcher
from metapub import exceptions
from urllib.request import urlretrieve

from metapub import pubmedcentral

from Bio import Entrez
import xmltodict
from bs4 import BeautifulSoup

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
    
    """
    Store PDF file from the given URL
    """
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

    """
    find a valid url for the pmid that points to a PDF and store it if exists
    """
    def fetch_pdf_if_exists(self, pmid):
        src = FindIt(pmid)
        if src.url is None: 
            print("Error: Paper's pdf was not accessible. Reason:")
            print(src.reason)
            for s in src.reason.split(' '):
                if s.startswith('http') or s.startswith("(http"):
                    s = s.replace('(', '').replace(')', '')
                    print(s)
                    self.store_pdf(s, f'{pmid}.pdf')
                    break
            return True
        else:
            self.store_pdf(src.url, f'{pmid}.pdf')
            return False

    """
    Store the full content of the paper in txt format if exists and is open access
    """
    def store_text(self, pmid):
        directory = os.path.join(self.pdfRoot, "txts")
        if not os.path.exists(directory):
            os.mkdir(directory)
        output_name = "/".join([directory,f'{pmid}.txt'])
        url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode".format(pmid = str(pmid))
        response = requests.get(url)
        
        print("response status code: ", response.status_code)
        if response.status_code == 200:
            xml_content = response.content.decode("utf-8")
            soup = BeautifulSoup(xml_content, "xml")
            plain_text = soup.get_text(separator=" ")

            with open(output_name, 'w', encoding='utf-8') as file:
                file.write(f"{plain_text}")
            return True
        else:
            print(f"Error: {pmid} not found in PMC database.")
            return False


    """
    Extract and store abstract from PMA (metadata) of the pmid
    """
    def store_abstract(self, pma):
        pmid = pma['pmid']
        abstract = pma['abstract']
        directory = os.path.join(self.pdfRoot, "abstracts")
        if not os.path.exists(directory):
            os.mkdir(directory)
        output_name = "/".join([directory,f'{pmid}.txt'])

        with open(output_name, 'w', encoding='utf-8') as file:
            file.write(f"{abstract}")
        return True


    """
    Scrape all information for each pmid in the list:
    1. Save meta data for the paper:
        title, year of publication, journal, authors, keywords, etc. 
    2. If OA, download pdf and txt format of it
    3. else, store the abstract for the paper
    """
    def scrape_all(self, pmidlist, query="", fetchPDF=True):
        self.pmas = []
        for pmid in pmidlist:
            pmid = pmid.strip()
            print("pmid: ", pmid)
            pma = self.scrape_metainfo(pmid)
            #pmcid = pubmedcentral.get_pmcid_for_otherid(pmid)
            #pma['pmcid'] = pmcid
            if (pma['abstract'] != ''):
                self.store_abstract(pma)
                pma['hasPDF'] = False
                pma['hasTXT'] = False
                if fetchPDF:
                    ret = self.fetch_pdf_if_exists(pmid)
                    pma['hasPDF'] = ret
                    ret = self.store_text(pmid)
                    pma['hasTXT'] = ret
                self.pmas.append(pma)
            else:
                print(f"ERROR: {pmid} No abstracts!!")

        newList = pd.DataFrame.from_records(self.pmas)
        newList["query"] = query
        print("len(newList):", len(newList))
        print("len(previousList):", len(self.metadf))
        self.metadf = pd.concat([newList,self.metadf])
        self.metadf.drop_duplicates(['doi', 'query'], inplace=True)
        print("len(concatenated):", len(self.metadf))

    """
    Write updated list of metadata for the papers
    """
    def write_meta(self):
        print("len(metadf): ", len(self.metadf))
        print("storing metadf in file ", self.csv_file)
        #self.metadf.dropna(inplace=True)
        #print("len(metadf) after dropna: ", len(self.metadf))
        print(self.metadf)
        self.metadf.to_csv(self.csv_file, index=None)

    def load_meta(self):
        self.metadf = pd.read_csv(self.csv_file)  
        return self.metadf    

    def __del__(self):
        print("In paper scraper's deconstructor.")
        self.write_meta()