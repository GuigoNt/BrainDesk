import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")

if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

os.environ["ANONYMIZED_TELEMETRY"] = "False"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "meu_banco")

modelo = None
client = None

def carregar_modelo():
    global modelo
    if modelo is None:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer("all-MiniLM-L6-v2")
    return modelo

def get_collection(nome="estudos"):
    global client
    if client is None:
        import chromadb
        client = chromadb.Client(
            settings=chromadb.config.Settings(
                persist_directory=DB_PATH
            )
        )
    return client.get_or_create_collection(name=nome)

# ================= FUNÇÕES =================

def adicionar_texto(texto, id, materia="geral"):
    modelo = carregar_modelo()
    collection = get_collection(materia)

    embedding = modelo.encode(texto).tolist()

    collection.add(
        documents=[texto],
        embeddings=[embedding],
        ids=[id]
    )

    client.persist()


def buscar_contexto(pergunta, materia="geral"):
    modelo = carregar_modelo()
    collection = get_collection(materia)

    embedding = modelo.encode(pergunta).tolist()

    resultados = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )

    if resultados["documents"]:
        return " ".join(resultados["documents"][0])
    return "Sem contexto ainda."


def listar_tudo(materia="geral"):
    collection = get_collection(materia)
    dados = collection.get()

    if dados["documents"]:
        return "\n\n".join(dados["documents"])
    return "Nada salvo ainda."


def limpar_memoria(materia="geral"):
    global client
    collection = get_collection(materia)

    dados = collection.get()
    if dados["ids"]:
        collection.delete(ids=dados["ids"])
        client.persist()