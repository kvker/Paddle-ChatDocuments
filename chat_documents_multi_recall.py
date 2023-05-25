import glob
import os

from pipelines.document_stores import ElasticsearchDocumentStore
from pipelines.nodes import (BM25Retriever, CharacterTextSplitter, ChatGLMBot,
                             DensePassageRetriever, DocxToTextConverter,
                             ErnieRanker, ImageToTextConverter, JoinDocuments,
                             MarkdownConverter, PDFToTextConverter,
                             PromptTemplate, TextConverter,
                             TruncatedConversationHistory)
from pipelines.pipelines import Pipeline


class ChatGLM_documents():

    device: str = 'gpu'
    index_name: str = 'dureader_index'
    max_seq_len_query: int = 64
    max_seq_len_passage: int = 256
    retriever_batch_size: int = 16
    query_embedding_model: str = 'rocketqa-zh-nano-query-encoder'
    passage_embedding_model: str = 'rocketqa-zh-nano-query-encoder'
    ranker_model: str = 'rocketqa-zh-dureader-cross-encoder'
    params_path: str = 'checkpoints/model_40/model_state.pdparams'
    embedding_dim: int = 312
    embed_title: bool = False
    tgt_length: int = 512
    model_type: str = 'ernie_search'
    host: str = 'localhost'
    port: str = 9200

    chatglm = ChatGLMBot(tgt_length=tgt_length)

    def get_es_retriever(self, use_gpu, filepaths, chunk_size):
        document_store = ElasticsearchDocumentStore(
            host=self.host,
            port=self.port,
            username="",
            password="",
            embedding_dim=self.embedding_dim,
            index=self.index_name,
        )
        use_gpu = True if self.device == "gpu" else False
        retriever = DensePassageRetriever(
            document_store=document_store,
            query_embedding_model=self.query_embedding_model,
            passage_embedding_model=self.passage_embedding_model,
            params_path=self.params_path,
            output_emb_size=self.embedding_dim
            if self.model_type in ["ernie_search", "neural_search"] else None,
            max_seq_len_query=self.max_seq_len_query,
            max_seq_len_passage=self.max_seq_len_passage,
            batch_size=self.retriever_batch_size,
            use_gpu=use_gpu,
            embed_title=self.embed_title,
        )

        try:
            # Indexing Markdowns
            markdown_converter = MarkdownConverter()

            text_splitter = CharacterTextSplitter(separator="\n",
                                                  chunk_size=chunk_size,
                                                  chunk_overlap=0,
                                                  filters=["\n"])
            indexing_md_pipeline = Pipeline()
            indexing_md_pipeline.add_node(component=markdown_converter,
                                          name="MarkdownConverter",
                                          inputs=["File"])
            indexing_md_pipeline.add_node(component=text_splitter,
                                          name="Splitter",
                                          inputs=["MarkdownConverter"])
            indexing_md_pipeline.add_node(component=retriever,
                                          name="Retriever",
                                          inputs=["Splitter"])
            indexing_md_pipeline.add_node(component=document_store,
                                          name="DocumentStore",
                                          inputs=["Retriever"])
            files = glob.glob(filepaths + "/*.md")
            indexing_md_pipeline.run(file_paths=files)
        except:
            pass

        try:
            # Indexing Docx
            docx_converter = DocxToTextConverter()

            text_splitter = CharacterTextSplitter(separator="\f",
                                                  chunk_size=chunk_size,
                                                  chunk_overlap=0,
                                                  filters=["\n"])
            indexing_docx_pipeline = Pipeline()
            indexing_docx_pipeline.add_node(component=docx_converter,
                                            name="DocxConverter",
                                            inputs=["File"])
            indexing_docx_pipeline.add_node(component=text_splitter,
                                            name="Splitter",
                                            inputs=["DocxConverter"])
            indexing_docx_pipeline.add_node(component=retriever,
                                            name="Retriever",
                                            inputs=["Splitter"])
            indexing_docx_pipeline.add_node(component=document_store,
                                            name="DocumentStore",
                                            inputs=["Retriever"])
            files = glob.glob(filepaths + "/*.docx")
            indexing_docx_pipeline.run(file_paths=files)
        except:
            pass

        try:
            # Indexing PDF
            pdf_converter = PDFToTextConverter()

            text_splitter = CharacterTextSplitter(
                separator="\f",
                chunk_size=chunk_size,
                chunk_overlap=0,
                filters=['([﹒﹔﹖﹗．。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$))'])
            indexing_pdf_pipeline = Pipeline()
            indexing_pdf_pipeline.add_node(component=pdf_converter,
                                           name="PDFConverter",
                                           inputs=["File"])
            indexing_pdf_pipeline.add_node(component=text_splitter,
                                           name="Splitter",
                                           inputs=["PDFConverter"])
            indexing_pdf_pipeline.add_node(component=retriever,
                                           name="Retriever",
                                           inputs=["Splitter"])
            indexing_pdf_pipeline.add_node(component=document_store,
                                           name="DocumentStore",
                                           inputs=["Retriever"])
            files = glob.glob(filepaths + "/*.pdf")
            indexing_pdf_pipeline.run(file_paths=files)
        except:
            pass

        try:
            # Indexing Image
            image_converter = ImageToTextConverter()

            text_splitter = CharacterTextSplitter(separator="\f",
                                                  chunk_size=chunk_size,
                                                  chunk_overlap=0,
                                                  filters=["\n"])
            indexing_image_pipeline = Pipeline()
            indexing_image_pipeline.add_node(component=image_converter,
                                             name="ImageConverter",
                                             inputs=["File"])
            indexing_image_pipeline.add_node(component=text_splitter,
                                             name="Splitter",
                                             inputs=["ImageConverter"])
            indexing_image_pipeline.add_node(component=retriever,
                                             name="Retriever",
                                             inputs=["Splitter"])
            indexing_image_pipeline.add_node(component=document_store,
                                             name="DocumentStore",
                                             inputs=["Retriever"])
            files = glob.glob(filepaths + "/*.png")
            indexing_image_pipeline.run(file_paths=files)
        except:
            pass

        try:
            # Indexing Text
            text_converter = TextConverter()

            text_splitter = CharacterTextSplitter(separator="\f",
                                                  chunk_size=chunk_size,
                                                  chunk_overlap=0,
                                                  filters=["\n"])
            indexing_text_pipeline = Pipeline()
            indexing_text_pipeline.add_node(component=text_converter,
                                            name="TextConverter",
                                            inputs=["File"])
            indexing_text_pipeline.add_node(component=text_splitter,
                                            name="Splitter",
                                            inputs=["TextConverter"])
            indexing_text_pipeline.add_node(component=retriever,
                                            name="Retriever",
                                            inputs=["Splitter"])
            indexing_text_pipeline.add_node(component=document_store,
                                            name="DocumentStore",
                                            inputs=["Retriever"])
            files = glob.glob(filepaths + "/*.txt")
            indexing_text_pipeline.run(file_paths=files)
        except:
            pass
        document_store.update_embeddings(retriever)
        bm_retriever = BM25Retriever(document_store=document_store)
        return retriever, bm_retriever

    def chatglm_bot(self,
                    query,
                    dpr_retriever,
                    bm_retriever,
                    history=[],
                    top_k=10,
                    max_length=128,
                    **kwargs):

        ranker = ErnieRanker(
            model_name_or_path=self.ranker_model,
            use_gpu=self.device,
        )
        pipe = Pipeline()

        pipe.add_node(component=bm_retriever,
                      name="BMRetriever",
                      inputs=["Query"])
        pipe.add_node(component=dpr_retriever,
                      name="DenseRetriever",
                      inputs=["Query"])
        pipe.add_node(component=JoinDocuments(join_mode="concatenate"),
                      name="JoinResults",
                      inputs=["BMRetriever", "DenseRetriever"])
        pipe.add_node(component=ranker, name="Ranker", inputs=["JoinResults"])

        pipe.add_node(component=PromptTemplate("""基于以下已知信息，请简洁并专业地回答用户的问题。
                如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"。不允许在答案中添加编造成分。另外，答案请使用中文。

                已知内容：{documents} 
                
                问题：{query}"""),
                      name="Template",
                      inputs=["Ranker"])
        pipe.add_node(
            component=TruncatedConversationHistory(max_length=max_length),
            name="TruncateHistory",
            inputs=["Template"])
        pipe.add_node(component=self.chatglm,
                      name="ChatGLMBot",
                      inputs=["TruncateHistory"])

        history = []

        prediction = pipe.run(query=query,
                              params={
                                  "BMRetriever": {
                                      "top_k": top_k
                                  },
                                  "DenseRetriever": {
                                      "top_k": top_k
                                  },
                                  "Ranker": {
                                      "top_k": top_k
                                  },
                                  "TruncateHistory": {
                                      "history": history
                                  }
                              })
        print("user: {}".format(query))
        print("assistant: {}".format(prediction["result"]))
        history.append((query, prediction["result"]))
        return history


if __name__ == "__main__":
    chatglm_documents = ChatGLM_documents()
    # retriever= chatglm_documents.get_faiss_retriever(use_gpu=True, filepaths="/home/aistudio/docs", chunk_size=10000)
    dpr_retriever, bm_retriever = chatglm_documents.get_es_retriever(
        use_gpu=True,
        filepaths="/home/aistudio/Paddle-ChatDocuments/docs",
        chunk_size=1000)

    chatglm_documents.chatglm_bot('chatglm-6b的局限性在哪里？如何改进？',
                                  dpr_retriever=dpr_retriever,
                                  bm_retriever=bm_retriever)
