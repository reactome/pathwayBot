python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

python main.py

#### sample commands:
/usr/bin/time python ../src/main.py find_add_pmids --file query_test12.lst --outdir pmid_out12 --oa --num_pmids 8
