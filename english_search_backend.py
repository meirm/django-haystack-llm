"""
A very basic, ORM-based backend for simple search during tests.
"""

from functools import reduce
from warnings import warn

from django.db.models import Q

from haystack import connections
from haystack.backends import (
    BaseEngine,
    BaseSearchBackend,
    BaseSearchQuery,
    SearchNode,
    log_query,
)
from haystack.inputs import PythonData
from haystack.models import SearchResult
from haystack.utils import get_model_ct_tuple

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain

import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# account for deprecation of LLM model
import datetime
# Get the current date
current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-3.5-turbo-0125"

if not os.getenv('OPENAI_API_KEY'):
    raise("Missing OpenAI key")

llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo-instruct")

#llm = ChatOpenAI(temperature=0.9, model=llm_model)

# prompt template 1: translate to english
first_prompt = PromptTemplate(
            template="<Instructions>Translate the query to english if it is in another language, if not just output the original text</Instructions>"
 "\n\n<Query>{Query}</Query>",
            input_variables=["Query"]
                )
# chain 1: input= Review and output= English_Query
chain_one = LLMChain(llm=llm, prompt=first_prompt)

class EnglishSearchBackend(BaseSearchBackend):
    def update(self, indexer, iterable, commit=True):
        warn("update is not implemented in this backend")

    def remove(self, obj, commit=True):
        warn("remove is not implemented in this backend")

    def clear(self, models=None, commit=True):
        warn("clear is not implemented in this backend")

    @log_query
    def search(self, query_string, **kwargs):
        hits = 0
        results = []
        result_class = SearchResult
        models = (
            connections[self.connection_alias].get_unified_index().get_indexed_models()
        )

        if kwargs.get("result_class"):
            result_class = kwargs["result_class"]

        if kwargs.get("models"):
            models = kwargs["models"]

        if query_string:
            for model in models:
                if query_string == "*":
                    qs = model.objects.all()
                else:
                    for term in query_string.split():
                        queries = []

                        for field in model._meta.fields:
                            if hasattr(field, "related"):
                                continue

                            if field.get_internal_type() not in (
                                "TextField",
                                "CharField",
                                "SlugField",
                            ):
                                continue

                            queries.append(Q(**{"%s__icontains" % field.name: term}))

                        if queries:
                            qs = model.objects.filter(
                                reduce(lambda x, y: x | y, queries)
                            )
                        else:
                            qs = []

                hits += len(qs)

                for match in qs:
                    match.__dict__.pop("score", None)
                    app_label, model_name = get_model_ct_tuple(match)
                    result = result_class(
                        app_label, model_name, match.pk, 0, **match.__dict__
                    )
                    # For efficiency.
                    result._model = match.__class__
                    result._object = match
                    results.append(result)

        if hits == 0 and kwargs.get("skip_llm_query",False)==False:
            print(f"Original query: {query_string}")
            query_string = chain_one.run(query_string)
            print(f"New query: {query_string}")
            kwargs["skip_llm_query"]= True
            return self.search(query_string, **kwargs)
        print(f"Returning {hits} hits")
        return {"results": results, "hits": hits}

    def prep_value(self, db_field, value):
        return value

    def more_like_this(
        self,
        model_instance,
        additional_query_string=None,
        start_offset=0,
        end_offset=None,
        limit_to_registered_models=None,
        result_class=None,
        **kwargs
    ):
        return {"results": [], "hits": 0}


class SimpleSearchQuery(BaseSearchQuery):
    def build_query(self):
        if not self.query_filter:
            return "*"

        return self._build_sub_query(self.query_filter)

    def _build_sub_query(self, search_node):
        term_list = []

        for child in search_node.children:
            if isinstance(child, SearchNode):
                term_list.append(self._build_sub_query(child))
            else:
                value = child[1]

                if not hasattr(value, "input_type_name"):
                    value = PythonData(value)

                term_list.append(value.prepare(self))

        return (" ").join(map(str, term_list))


class EnglishEngine(BaseEngine):
    backend = EnglishSearchBackend
    query = SimpleSearchQuery
