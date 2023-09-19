python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

#### sample commands:
### download 8 relevant documents in PMC (--oa) to each query in file "query_test12" and save metadata and the document text in dir pmid_out12
mkdir -p tests/pmid_out12 && /usr/bin/time python src/main.py find_add_pmids --file tests/query_test12.lst --outdir tests/pmid_out12 --oa --num_pmids 8

### if remove --oa, it will not download the text and only store the abstract, will also search in pubmed instead of PMC
mkdir -p tests/pmid_out12 && /usr/bin/time python src/main.py find_add_pmids --file tests/query_test12.lst --outdir tests/pmid_out12 --num_pmids 50

### sample to generate summaries for a list of queries (pathways) stored in a file, separated by newline
mkdir -p tests/pmid_out12 && /usr/bin/time python src/main.py summarize_pathway_batch --file tests/query_test12.lst --outdir tests/pmid_out12 --kg_file data/kg/reactome2langChainGraph2023.gml 
