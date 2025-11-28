from search import search_prompt

def main():
  print("="*50)
  print("Chat com Documentos PDF - Sistema RAG")
  print("="*50)
  print("Digite suas perguntas sobre o documento.")
  print("Digite 'sair', 'exit' ou 'quit' para encerrar.\n")

  while True:
    user_question = input("Você: ").strip()
    if user_question.lower() in ['sair', 'exit', 'quit']:
      print("Encerrando o assistente. Até logo!")
      break

    try:
      print("\nBuscando informações...\n")
      answer = search_prompt(user_question)

      print(f"Assistente: {answer}\n")
      print("-"*50 + "\n")
    
    except Exception as e:
      print(f"Erro ao processar pergunta: {e}\n")
      print("Tente novamente.\n")


if __name__ == "__main__":
    main()