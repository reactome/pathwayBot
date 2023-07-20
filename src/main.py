

import argparse
import os

def add_list_of_pmids(file_path):
    print(f"Adding list of PMIDs from file: {file_path}")

def add_biopax(file_path):
    print(f"Adding BioPAX file: {file_path}")

def add_knowledge_graph(file_path):
    print(f"Adding knowledge graph from file: {file_path}")

def run_chatbot():
    print("Running the chatbot...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task Selector")
    parser.add_argument("task", type=str, choices=["add_pmids", "add_biopax", "add_kg", "run_chatbot"], 
                        help="Choose a command: add_pmids, add_biopax, add_kg, run_chatbot")
    
    # Optional arguments for specific tasks
    parser.add_argument("--file", type=str, 
                        help="File path containing list of PMIDs for task \
                        add_pmids, BioPAX for task add_biopax, or knowledge graph for task add_kg")

    args = parser.parse_args()

    task = args.task

    if any(task == c for c in ["add_pmids", "add_biopax", "add_kg"]):
        if not args.file:
            print("Error: Task requires at least one parameter \"--file\".")
            exit(1)
        elif not os.path.isfile(args.file):
            print(f"Error: File {args.file} does not exist.")
            exit(1)
    
    if task == "add_pmids":
        add_list_of_pmids(args.file)

    elif task == "add_biopax":
        add_biopax(args.file)

    elif task == "add_kg":
        add_knowledge_graph(args.file)

    elif task == "run_chatbot":
        run_chatbot()

    else:
        print("Invalid task selected. Please choose a valid task: add_pmids, add_biopax, add_kg, or run_chatbot.")
