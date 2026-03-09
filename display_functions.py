"""Display helpers for AISuite chat completion responses."""

import json


def pretty_print_chat_completion(response):
    """Print a formatted trace of an AISuite chat completion with tool calls."""
    separator = "=" * 60

    if not hasattr(response, "choices") or not response.choices:
        print(f"\n{separator}\n  No response\n{separator}")
        return

    for i, choice in enumerate(response.choices):
        msg = choice.message

        # Print tool calls if present
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"\n{separator}")
            print("  TOOL CALLS")
            print(separator)
            for tc in msg.tool_calls:
                fn = tc.function
                print(f"  -> {fn.name}({fn.arguments})")

        # Print assistant's final text
        if hasattr(msg, "content") and msg.content:
            print(f"\n{separator}")
            print("  ASSISTANT RESPONSE")
            print(separator)
            print(msg.content)
            print(separator)
