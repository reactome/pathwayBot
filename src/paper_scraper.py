#from metapub.convert import pmid2doi
#from metapub import FindIt
from metapub import PubMedFetcher
#from metapub import CrossRefFetcher
from metapub import exceptions
from urllib.request import urlretrieve

class PaperScraper:

    def __init__(self, pdfRoot = "papers"):
        self.pdfRoot = pdfRoot
        self.pmas = []

    ## having the pubmedid returns the PMA containing all the paper meta information including the url to its PDF if OA
    def scrape_metainfo(pmid):
        ## get metainfo of the paper using pubmedid
        passed=False
        tries=3
        while not passed:
            try:
                if tries < 3:
                    print(tries, pmid)
                pma = PubMedFetcher().article_by_pmid(pmid)
                passed = True
            except exceptions.MetaPubError as e:
                print(e)
                if tries == 0:
                    passed = True
                tries-=1
                pass
        return pma
    
    ## example:
    ## url: 'https://onlinelibrary.wiley.com/doi/pdf/10.1002/jcb.20409'
    ## output_name: 15723341.pdf
    def store_pdf(self, url, output_name):
        urlretrieve(url, f'{self.pdfRoot}/{output_name}')

    def fetch_pdf_if_exists(self, pmid):
        pma = self.scrape_metainfo(pmid)
        if pma.url.notnull():
            self.store_pdf(pma.url, f'{pmid}.pdf')
        else:
            print("Paper's pdf was not accessible (e.g. was not OA)")
        return pma

    def scrape_all(self, pmidlist):
        self.pmas = []
        for pmid in pmidlist:
            pma = self.fetch_pdf_if_exists(pmid)
            self.pmas.append(pma)
            
