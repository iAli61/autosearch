import os
import asyncio
import pandas as pd
from sklearn import covariance
import tiktoken
from dotenv import load_dotenv

from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.global_search.community_context import GlobalCommunityContext
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore

class GraphragSearch:
    def __init__(self, input_dir, lancedb_uri, config=None):
        load_dotenv()  # Load environment variables from .env file
        self.input_dir = input_dir
        self.lancedb_uri = lancedb_uri
        self.config = config or {}
        self.setup_environment()
        self.load_data()
        self.setup_llm()

    def setup_environment(self):
        # Override environment variables with provided config
        for key, value in self.config.items():
            os.environ[key] = value

    def load_data(self):
        # Load all necessary data
        self.entity_df = pd.read_parquet(f"{self.input_dir}/create_final_nodes.parquet")
        self.entity_embedding_df = pd.read_parquet(f"{self.input_dir}/create_final_entities.parquet")
        self.report_df = pd.read_parquet(f"{self.input_dir}/create_final_community_reports.parquet")
        self.relationship_df = pd.read_parquet(f"{self.input_dir}/create_final_relationships.parquet")
        covariate_file=f"{self.input_dir}/create_final_covariates.parquet"
        if os.path.exists(covariate_file):
            self.covariate_df = pd.read_parquet(f"{self.input_dir}/create_final_covariates.parquet")
            self.covariate = True
        else:
            self.covariate = False
        self.text_unit_df = pd.read_parquet(f"{self.input_dir}/create_final_text_units.parquet")

        self.entities = read_indexer_entities(self.entity_df, self.entity_embedding_df, 2)
        self.reports = read_indexer_reports(self.report_df, self.entity_df, 2)
        self.relationships = read_indexer_relationships(self.relationship_df)
        if self.covariate:
            self.claims = read_indexer_covariates(self.covariate_df)
        self.text_units = read_indexer_text_units(self.text_unit_df)

        # Setup entity description embeddings
        self.description_embedding_store = LanceDBVectorStore(collection_name="entity_description_embeddings")
        self.description_embedding_store.connect(db_uri=self.lancedb_uri)
        self.entity_description_embeddings = store_entity_semantic_embeddings(
            entities=self.entities, vectorstore=self.description_embedding_store
        )

    def setup_llm(self):
        self.api_key = os.getenv("GRAPHRAG_API_KEY")
        self.api_base = os.getenv("GRAPHRAG_API_BASE")
        self.api_version = os.getenv("GRAPHRAG_API_VERSION")
        self.llm_model = os.getenv("GRAPHRAG_LLM_MODEL", "gpt-4-turbo-preview")
        self.embedding_model = os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-3-small")
        
        # LLM setup
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            api_base=self.api_base,
            api_version=self.api_version,
            model=self.llm_model,
            api_type=OpenaiApiType.AzureOpenAI,
            deployment_name=os.getenv("GRAPHRAG_LLM_DEPLOYMENT_NAME", self.llm_model),
            max_retries=int(os.getenv("GRAPHRAG_LLM_MAX_RETRIES", "20")),
        )

        self.token_encoder = tiktoken.get_encoding(os.getenv("GRAPHRAG_ENCODING_MODEL", "cl100k_base"))

        # Embedding setup
        self.text_embedder = OpenAIEmbedding(
            api_key=os.getenv("GRAPHRAG_EMBEDDING_API_KEY", self.api_key),
            api_base=os.getenv("GRAPHRAG_EMBEDDING_API_BASE", self.api_base),
            api_version=os.getenv("GRAPHRAG_EMBEDDING_API_VERSION", self.api_version),
            api_type=OpenaiApiType.AzureOpenAI,
            model=self.embedding_model,
            deployment_name=os.getenv("GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME", self.embedding_model),
            max_retries=int(os.getenv("GRAPHRAG_EMBEDDING_MAX_RETRIES", "20")),
        )

    async def local_search(self, query, 
                           text_unit_prop=0.5,
                           community_prop=0.1,
                           conversation_history_max_turns=5,
                           conversation_history_user_turns_only=True,
                           top_k_mapped_entities=10,
                           top_k_relationships=10,
                           include_entity_rank=True,
                           include_relationship_weight=True,
                           include_community_rank=False,
                           return_candidate_context=False,
                           embedding_vectorstore_key=EntityVectorStoreKey.ID,
                           max_tokens=12000,
                           llm_max_tokens=2000,
                           temperature=0.0,
                           response_type="multiple paragraphs"):
        

        context_builder = LocalSearchMixedContext(
            community_reports=self.reports,
            text_units=self.text_units,
            entities=self.entities,
            relationships=self.relationships,
            covariates={"claims": self.claims} if self.covariate else None,
            entity_text_embeddings=self.description_embedding_store,
            embedding_vectorstore_key=embedding_vectorstore_key,
            text_embedder=self.text_embedder,
            token_encoder=self.token_encoder,
        )

        local_context_params = {
            "text_unit_prop": text_unit_prop,
            "community_prop": community_prop,
            "conversation_history_max_turns": conversation_history_max_turns,
            "conversation_history_user_turns_only": conversation_history_user_turns_only,
            "top_k_mapped_entities": top_k_mapped_entities,
            "top_k_relationships": top_k_relationships,
            "include_entity_rank": include_entity_rank,
            "include_relationship_weight": include_relationship_weight,
            "include_community_rank": include_community_rank,
            "return_candidate_context": return_candidate_context,
            "embedding_vectorstore_key": embedding_vectorstore_key,
            "max_tokens": max_tokens,
        }

        llm_params = {
            "max_tokens": llm_max_tokens,
            "temperature": temperature,
        }

        search_engine = LocalSearch(
            llm=self.llm,
            context_builder=context_builder,
            token_encoder=self.token_encoder,
            llm_params=llm_params,
            context_builder_params=local_context_params,
            response_type=response_type,
        )

        result = await search_engine.asearch(query)
        return result

    async def global_search(self, query,
                            use_community_summary=False,
                            shuffle_data=True,
                            include_community_rank=True,
                            min_community_rank=0,
                            community_rank_name="rank",
                            include_community_weight=True,
                            community_weight_name="occurrence weight",
                            normalize_community_weight=True,
                            max_tokens=12000,
                            context_name="Reports",
                            map_max_tokens=1000,
                            map_temperature=0.0,
                            reduce_max_tokens=2000,
                            reduce_temperature=0.0,
                            allow_general_knowledge=False,
                            json_mode=True,
                            concurrent_coroutines=32,
                            response_type="multiple paragraphs"):
        context_builder = GlobalCommunityContext(
            community_reports=self.reports,
            entities=self.entities,
            token_encoder=self.token_encoder,
        )

        context_builder_params = {
            "use_community_summary": use_community_summary,
            "shuffle_data": shuffle_data,
            "include_community_rank": include_community_rank,
            "min_community_rank": min_community_rank,
            "community_rank_name": community_rank_name,
            "include_community_weight": include_community_weight,
            "community_weight_name": community_weight_name,
            "normalize_community_weight": normalize_community_weight,
            "max_tokens": max_tokens,
            "context_name": context_name,
        }

        map_llm_params = {
            "max_tokens": map_max_tokens,
            "temperature": map_temperature,
            "response_format": {"type": "json_object"},
        }

        reduce_llm_params = {
            "max_tokens": reduce_max_tokens,
            "temperature": reduce_temperature,
        }

        search_engine = GlobalSearch(
            llm=self.llm,
            context_builder=context_builder,
            token_encoder=self.token_encoder,
            max_data_tokens=max_tokens,
            map_llm_params=map_llm_params,
            reduce_llm_params=reduce_llm_params,
            allow_general_knowledge=allow_general_knowledge,
            json_mode=json_mode,
            context_builder_params=context_builder_params,
            concurrent_coroutines=concurrent_coroutines,
            response_type=response_type,
        )

        result = await search_engine.asearch(query)
        return result
    
    
# Usage example:
# searcher = GraphragSearch("./inputs/operation dulce", "./inputs/operation dulce/lancedb", config={"GRAPHRAG_LLM_DEPLOYMENT_NAME": "custom_deployment"})
# asyncio.run(searcher.local_search("Tell me about Agent Mercer"))
# asyncio.run(searcher.global_search("What is the major conflict in this story?"))