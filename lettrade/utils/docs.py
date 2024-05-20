def is_docs_session():
    if __debug__:
        import os

        return "MKDOCS_CONFIG_DIR" in os.environ
