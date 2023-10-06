### These environment variables should be set in the venv file:
### export OPENAI_API_KEY=
### export OPENAI_ORGANIZATION=
### export PINECONE_API_KEY=
### export PINECONE_ENV=
### export SERPER_API_KEY=
### export SCRAPER_API_KEY=

### you need to request access to the PINECONE Pathway_summation index.
 

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

#### sample commands:
### download 8 relevant documents in PMC (--oa) to each query in file "test_query12.lst" and save metadata and the document text in dir pmid_out12
mkdir -p examples/outputs/pmid_out12 && /usr/bin/time python src/main.py find_add_pmids --file examples/test_query12.lst --outdir examples/outputs/pmid_out12 --oa --num_pmids 8

### if remove --oa, it will not download the text and only store the abstract, will also search in pubmed instead of PMC
mkdir -p examples/outputs/pmid_out12 && /usr/bin/time python src/main.py find_add_pmids --file examples/query_test12.lst --outdir examples/outputs/pmid_out12 --num_pmids 50

### sample to generate summaries for a list of queries (pathways) stored in a file, separated by newline
mkdir -p examples/outputs/pmid_out12 && /usr/bin/time python src/main.py summarize_pathway_batch --file examples/query_test12.lst --outdir examples/outputs/pmid_out12 --kg_file data/kg/reactome2langChainGraph2023.gml 
