python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

python main.py

#### sample commands:
### download 8 relevant documents in PMC (--oa) to each query in file "query_test12" and save metadata and the document text in dir pmid_out12
/usr/bin/time python ../src/main.py find_add_pmids --file query_test12.lst --outdir pmid_out12 --oa --num_pmids 8
### if remove --oa, it will not download the text and only store the abstract, will also search in pubmed instead of PMC
/usr/bin/time python ../src/main.py find_add_pmids --file query_test12.lst --outdir pmid_out12 --num_pmids 50
### sample to generate summaries for a list of queries (pathways) stored in a file, separated by newline
python ../src/main.py summarize_pathway_batch --file query_test1.lst --outdir pmid_out1 --kg_file ../data/kg/reactome2langChainGraph2023.gml 
