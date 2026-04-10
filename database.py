import sys
import os

# Corrigir erro do PyInstaller
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")

if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

os.environ["ANONYMIZED_TELEMETRY"] = "False"

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "meu_banco")

modelo = None
client = None

# ================= MODELO =================

def carregar_modelo():
    global modelo
    if modelo is None:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer("all-MiniLM-L6-v2")
    return modelo

# ================= CHROMA (FIXO) =================

def get_client():
    global client

    if client is None:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.Client(
            Settings(
                persist_directory=DB_PATH,
                anonymized_telemetry=False,
                is_persistent=True
            )
        )

    return client


def get_collection(nome="estudos"):
    client = get_client()
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

    get_client().persist()


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
    collection = get_collection(materia)

    dados = collection.get()
    if dados["ids"]:
        collection.delete(ids=dados["ids"])
        get_client().persist()