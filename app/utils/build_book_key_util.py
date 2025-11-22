def build_book_key(func, namespace: str = "", request=None, response=None, *args, **kwargs):
    real_kwargs = kwargs.get("kwargs", {})
    book_id = real_kwargs.get("book_id")
    
    if not book_id:
        return "book:unknown"
        
    return f"book:{book_id}"