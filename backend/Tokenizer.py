from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("NousResearch/Hermes-3-Llama-3.2-3B")
def gettokencount(text):
    sol=tokenizer.encode(text)
    return len(sol)

#returns no:of input tokens
