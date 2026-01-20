import _2_llm_setup

from unstructured.partition.auto import partition

def read_doc_pro(file_path):
    elements =  partition(
        filename = file_path,
        strategy = "hi_res",
        ocr_languages = "eng",
        include_page_breaks = True

    )
    return elements