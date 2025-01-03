"""
Utils for the Language Model (LLM) module.
"""

from typing import List, Dict, Callable

import tiktoken

from common.logger_helper import init_logger

from .formatting import ensure_terminal_formatting

from ..constants import MAX_TOKENS, GPT_4

gpt_token_encoder = tiktoken.encoding_for_model(GPT_4)
logger = init_logger()


def context_token_len(context: List[Dict[str, str]]) -> int:
    """
    Calculates the total number of tokens used in the given context for a conversation.

    This function iterates over a list of messages, represented as dictionaries with 'role' and 'content' keys,
    and computes the total number of tokens required to represent the entire context. Each message adds a
    set number of tokens for formatting, in addition to the number of tokens required by the message content.

    Args:
        context (List[Dict[str, str]]): A list of dictionaries where each dictionary represents a message in the conversation.
                                        Each message contains 'role' (e.g., 'user', 'assistant') and 'content' (the message text).

    Returns:
        int: The total number of tokens used in the context, including the content and formatting tokens.
    """
    num_tokens = 0
    for message in context:
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        num_tokens += 4
        num_tokens += len(gpt_token_encoder.encode(message["content"]))
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def limit_context_length(context: List[Dict[str, str]]):
    """
    Trims the conversation context to ensure the total number of tokens does not exceed the maximum limit.

    This function continuously removes the earliest message (excluding the first one) from the conversation
    context until the total token count falls below the maximum token limit. The first message is retained to
    preserve the original context or system instructions.

    Args:
        context (List[Dict[str, str]]): A list of dictionaries representing the conversation history.
                                        Each dictionary contains 'role' and 'content' keys for each message.

    Returns:
        None
    """
    original_length = len(context)
    while context_token_len(context) > MAX_TOKENS:
        context.pop(1)
    if len(context) < original_length:
        logger.info(
            "Warning: Context truncated. Only the most recent %d messages are being used.", len(context))
        logger.info(
            "Older messages have been removed to fit within the token limit.")


def ask_llm(context: List[Dict[str, str]], ask_fn: Callable[[List[Dict[str, str]], bool], str]) -> str:
    """
    Queries a language model (LLM) using the given conversation context and formats the response as terminal-style code.

    This function limits the context length to ensure it does not exceed the token limit, then sends the context
    to the LLM via the provided `ask_fn`. The returned response is stripped of extra whitespace and is passed through
    a function to ensure it adheres to terminal-style formatting.

    Args:
        context (List[Dict[str, str]]): A list of dictionaries representing the conversation history, where each message
                                        is stored with 'role' and 'content' keys.
        ask_fn (Callable[[List[Dict[str, str]], bool], str]): A callable function that interacts with the LLM, taking the
                                                              current context and returning a string response.

    Returns:
        str: The formatted terminal-style code generated by the LLM in response to the provided context.
    """
    limit_context_length(context)
    terminal_code = ask_fn(context).strip()
    formatted_code = ensure_terminal_formatting(terminal_code, ask_fn)
    return formatted_code
