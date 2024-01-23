
from enum import IntEnum
from langchain.chains import GraphQAChain
from langchain.retrievers.self_query.base import SelfQueryRetriever
from typing import Any, Dict, List, Optional, cast
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, AsyncCallbackManagerForRetrieverRun
from langchain.graphs.networkx_graph import get_entities
from langchain.schema import Document
from langchain.chains.query_constructor.ir import StructuredQuery

class SequentialType(IntEnum):
   BASE = 1
   KG_FOCUS = 2
   KG_EXPANDER = 3
   KG_FOCUS_LIMITED_TOKEN = 4
   KG_EXPANDER_LIMITED_TOKEN = 5


"""
Wrapper around LangChain GraphQAChain class that allows Asyncronous calls
"""
class AsyncGraphQAChain(GraphQAChain):
       async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """Extract entities, look up info and answer question."""
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        question = inputs[self.input_key]

        entity_string = await self.entity_extraction_chain.arun(question)

        await _run_manager.on_text("Entities Extracted:", end="\n", verbose=self.verbose)
        await _run_manager.on_text(
            entity_string, color="green", end="\n", verbose=self.verbose
        )
        entities = get_entities(entity_string)
        context = ""
        all_triplets = []
        for entity in entities:
            all_triplets.extend(self.graph.get_entity_knowledge(entity))
        context = "\n".join(all_triplets)
        await _run_manager.on_text("Full Context:", end="\n", verbose=self.verbose)
        await _run_manager.on_text(context, color="green", end="\n", verbose=self.verbose)
        result = self.qa_chain(
            {"question": question, "context": context},
            callbacks=_run_manager.get_child(),
        )
        return {self.output_key: result[self.qa_chain.output_key]}

"""
Wrapper around LangChain SelfQueryRetriever class that allows Asyncronous calls
"""
class AsyncSelfQueryRetriever(SelfQueryRetriever):
       async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """
        inputs = self.llm_chain.prep_inputs({"query": query})
        structured_query = cast(
            StructuredQuery,
            await self.llm_chain.apredict_and_parse(
                callbacks=run_manager.get_child(), **inputs
            ),
        )
        if self.verbose:
            print(structured_query)
        new_query, new_kwargs = self.structured_query_translator.visit_structured_query(
            structured_query
        )
        if structured_query.limit is not None:
            new_kwargs["k"] = structured_query.limit

        if self.use_original_query:
            new_query = query

        search_kwargs = {**self.search_kwargs, **new_kwargs}
        docs = await self.vectorstore.asearch(new_query, self.search_type, **search_kwargs)
        return docs


def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))