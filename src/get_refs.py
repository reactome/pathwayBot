
#!pip install pandas
#!pip install pybiopax

import pandas as pd
import pybiopax


def get_refs_for_pathway(pid, model):
    
    ## Find the pathway object using the pid 
    obj = ""
    for m in model.get_objects_by_type(pybiopax.biopax.Pathway):
        for x in m.xref:
            if x.id == pid:
                obj = model.objects[m.uid]
                break
    lst = []
    if isinstance(obj, pybiopax.biopax.Pathway):
        for x in obj.xref:
            if isinstance(x, pybiopax.biopax.PublicationXref):
                lst.append(('direct', str(type(obj)).split('.')[-1][:-2], obj.name, x.id, x.title))
                
        ### There might be other interesting elements other than pathway_components too
        for cmp in obj.pathway_component:
            for x in cmp.xref:
                if isinstance(x, pybiopax.biopax.PublicationXref):
                    lst.append(('pathway_component', str(type(cmp)).split('.')[-1][:-2], cmp.name, x.id, x.title))
        return pd.DataFrame.from_records(lst, columns=['relationship', 'type', 'name', 'pmid', 'article_title'])
    else:
        print("Pathway not found")
        return None
    
    
if __name__ == "__main__":

    model = pybiopax.model_from_owl_file('../data/biopax3/Homo_sapiens.owl')
    ## example pid: R-HSA-5218920
    pid="R-HSA-5218920"
    get_refs_for_pathway(pid, model).to_csv(f"../results/{pid}.csv", index=None)