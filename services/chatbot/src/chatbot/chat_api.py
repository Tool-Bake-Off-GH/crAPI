import logging
from quart import Blueprint, jsonify, request, session
from uuid import uuid4
from .config import Config
from .chat_service import delete_chat_history, get_chat_history, process_user_message
from .session_service import (
    delete_api_key,
    get_api_key,
    get_model_name,
    get_or_create_session_id,
    store_api_key,
    store_model_name,
    get_user_jwt
)

chat_bp = Blueprint("chat", __name__, url_prefix="/genai")
logger = logging.getLogger(__name__)


@chat_bp.route("/init", methods=["POST"])
async def init():
    session_id = await get_or_create_session_id()
    data = await request.get_json()
    logger.debug("Initializing bot for session %s", session_id)
    api_key = await get_api_key(session_id)
    if api_key:
        logger.info("Model already initialized with OpenAI API Key from environment")
        return jsonify({"message": "Model Already Initialized"}), 200
    elif not data:
        logger.error("Invalid request")
        return jsonify({"message": "Invalid request"}), 400
    elif "openai_api_key" not in data:
        logger.error("openai_api_key not provided")
        return jsonify({"message": "openai_api_key not provided"}), 400
    openai_api_key: str = data["openai_api_key"]
    logger.debug("OpenAI API Key %s", openai_api_key[:5])
    # Save the api key in session
    await store_api_key(session_id, openai_api_key)
    return jsonify({"message": "Initialized"}), 200

@chat_bp.route("/model", methods=["POST"])
async def model():
    session_id = await get_or_create_session_id()
    data = await request.get_json()
    model_name = Config.DEFAULT_MODEL_NAME
    if data and "model_name" in data and data["model_name"]:
        model_name = data["model_name"]
    logger.debug("Setting model %s for session %s", model_name, session_id)
    await store_model_name(session_id, model_name)
    return jsonify({"model_used": model_name}), 200

@chat_bp.route("/ask", methods=["POST"])
async def chat():
    session_id = await get_or_create_session_id()
    openai_api_key = await get_api_key(session_id)
    model_name = await get_model_name(session_id)
    user_jwt = await get_user_jwt()
    if not openai_api_key:
        return jsonify({"message": "Missing OpenAI API key. Please authenticate."}), 400
    data = await request.get_json()
    message = data.get("message", "").strip()
    id = data.get("id", uuid4().int & (1 << 63) - 1)
    if not message:
        return jsonify({"message": "Message is required", "id": id}), 400
    reply, response_id = await process_user_message(session_id, message, openai_api_key, model_name, user_jwt)
    return jsonify({"id": response_id, "message": reply}), 200


@chat_bp.route("/state", methods=["GET"])
async def state():
    session_id = await get_or_create_session_id()
    logger.debug("Checking state for session %s", session_id)
    openai_api_key = await get_api_key(session_id)
    if openai_api_key:
        logger.debug(
            "OpenAI API Key for session %s: %s", session_id, openai_api_key[:5]
        )
        chat_history = await get_chat_history(session_id)
        # Limit chat history to last 20 messages
        chat_history = chat_history[-20:]
        return (
            jsonify(
                {
                    "initialized": "true",
                    "message": "Model initialized",
                    "chat_history": chat_history,
                }
            ),
            200,
        )
    return (
        jsonify({"initialized": "false", "message": "Model needs to be initialized"}),
        200,
    )


@chat_bp.route("/history", methods=["GET"])
async def history():
    session_id = await get_or_create_session_id()
    logger.debug("Checking state for session %s", session_id)
    openai_api_key = await get_api_key(session_id)
    if openai_api_key:
        chat_history = await get_chat_history(session_id)
        # Limit chat history to last 20 messages
        chat_history = chat_history[-20:]
        return jsonify({"chat_history": chat_history}), 200
    return (
        jsonify({"chat_history": []}),
        200,
    )


@chat_bp.route("/reset", methods=["POST"])
async def reset():
    session_id = await get_or_create_session_id()
    logger.debug("Checking state for session %s", session_id)
    await delete_chat_history(session_id)
    return jsonify({"initialized": "false", "message": "Reset successful"}), 200


@chat_bp.route("/health", methods=["GET"])
async def health():
    return jsonify({"message": "OK"}), 200
