

import argparse
import os
from paper_manager import PaperManager
from summary_generator import SummaryGenerator
import asyncio

def add_list_of_pmids(file_path, outdir_path):
    print(f"""
          
          Adding list of PMIDs from file: {file_path} to directory {outdir_path}.""")
    pm = PaperManager(outdir_path)
    pm.get_papers_using_pmidFile(file_path)

def add_query_pmids(file_path, outdir_path, num_pmids, oa=False):
    print(f"""
          
          Adding {num_pmids} PMIDs for papers most relevant to queries in file: 
          {file_path} and store to directory {outdir_path}.
          Only OA: {oa}""")
    pm = PaperManager(outdir_path)
    pm.get_papers_for_query(file_path, num_pmids, oa)

def add_biopax(file_path, outdir_path):
    print(f"Adding BioPAX file: {file_path} to directory {outdir_path}.")

def add_knowledge_graph(file_path, outdir_path):
    print(f"Adding knowledge graph from file: {file_path} to directory {outdir_path}.")

def summarize_pathway_batch(file_path, kg_file, outdir_path):
    print(f"Running summary generator for pathways in: {file_path} and storing results to directory {outdir_path}.")    
    asyncio.run(SummaryGenerator(kg_file).concur_generate_batch_summary(file_path, outdir_path))
    
def run_chatbot():
    print("Running the chatbot...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task Selector")
    parser.add_argument("task", type=str, choices=["add_pmids", "find_add_pmids", "add_biopax", "add_kg", "run_chatbot", "summarize_pathway_batch"], 
                        help="Choose a command: add_pmids, add_biopax, add_kg, run_chatbot")
    
    # Optional arguments for specific tasks
    parser.add_argument("--file", type=str, 
                        help="""File path containing list of PMIDs for task \
                        add_pmids, 
                        queries to search for find_add_pmids, 
                        BioPAX for task add_biopax, 
                        knowledge graph for task add_kg,
                        or list of pathways for task summarize_pathway_batch.""")

    parser.add_argument("--num_pmids", type=int, 
                        help="number of PMIDs to select from most relevant PMIDs found for the search query",
                        default=2)

    parser.add_argument("--oa", action="store_true", 
                        help="Search for relevant PMIDs ONLY through PMC (Open Access papers)")

    parser.add_argument("--outdir", type=str, 
                        help="Directory path to store output files for tasks \
                        add_pmids, add_biopax, or add_kg (default: current directory)",
                        default="./")
    
    parser.add_argument("--kg_file", type=str, 
                        help="The path to the knowledge-graph file in gml format.")

    args = parser.parse_args()

    task = args.task

    if any(task == c for c in ["add_pmids", "find_add_pmids", "add_biopax", "add_kg", "summarize_pathway_batch"]):
        if not args.file:
            print("Error: Task requires parameter \"--file\".")
            exit(1)
        elif not os.path.isfile(args.file):
            print(f"Error: File {args.file} does not exist.")
            exit(1)
        elif not args.outdir:
            print("Warning: No output directories provided: \"--outdir\". Using current path as output directory.")
            args.outdir = "./"
        if not os.path.isdir(args.outdir):
            print(f"Error: Output directory {args.outdir} does not exist. Please create the directory first.")
            exit(1)

    
    if task == "add_pmids":
        add_list_of_pmids(args.file, args.outdir)
    
    elif task == "find_add_pmids":
        add_query_pmids(args.file, args.outdir, args.num_pmids, args.oa)

    elif task == "add_biopax":
        add_biopax(args.file, args.outdir)

    elif task == "add_kg":
        add_knowledge_graph(args.file, args.outdir)

    elif task == "summarize_pathway_batch":
        if not args.kg_file:
            print("Error: Task requires parameter \"--kg_file\".")
            exit(1)
        elif not os.path.isfile(args.kg_file):
            print(f"Error: File \"{args.kg_file}\" does not exist.")
            exit(1)
        asyncio.run(SummaryGenerator(args.kg_file).concur_generate_batch_summary(args.file, args.outdir))

        #summarize_pathway_batch(args.file, args.kg_file, args.outdir)

    elif task == "run_chatbot":
        run_chatbot()

    else:
        print("Invalid task selected. Please choose a valid task: add_pmids, add_biopax, add_kg, or run_chatbot.")
