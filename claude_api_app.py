import argparse
import os
from dotenv import load_dotenv
import anthropic


load_dotenv()  # ANTHROPIC_API_KEY

# Claude model configuration
CLAUDE_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 8192,
    "temperature": 0.7
}


def load_prompt(path):
    with open(path, 'r') as file:
        return file.read()


def get_claude_client():
    return anthropic.Anthropic()


def generate_response(client, template, topic):
    prompt = template.replace("{{topic}}", topic)
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(messages=messages, **CLAUDE_CONFIG)
    return response.content[0].text, messages


def convert_to_format(client, content, messages, fmt):
    if fmt == "html":
        format_prompt = f"""
        Convert the following content into HTML page:
        - Use CSS styling
        - Use responsive layout
        - Return only HTML code

        Content:
        {content}
        """
    elif fmt == "json":
        format_prompt = f"""
        Convert the following content into structured JSON:
        - Return only clean JSON
        - No explanations or markdown

        Content:
        {content}
        """
    elif fmt == "txt":
        return content   
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    messages.append({"role": "assistant", "content": content})
    messages.append({"role": "user", "content": format_prompt})
    response = client.messages.create(messages=messages, **CLAUDE_CONFIG)
    return response.content[0].text


def save_output(content, topic, fmt):
    filename = f"{topic.lower().replace(' ', '_')}.{fmt}"
    with open(filename, "w") as f:
        f.write(content)
    return filename


def save_chat_log(messages, topic):
    filename = f"{topic.lower().replace(' ', '_')}_chat_history.txt"
    with open(filename, "w") as f:
        for m in messages:
            f.write(f"{m['role'].capitalize()}: {m['content']}\n\n")
    return filename


def parse_args():
    parser = argparse.ArgumentParser(description="Claude API call")
    parser.add_argument("--topic", required=True, help="Topic (e.g. schedule, finance, email)")
    parser.add_argument("--prompt", default="prompt.txt", help="Prompt file with {{topic}} placeholder")
    parser.add_argument("--format", choices=["html", "txt", "json"], default="html", help="Output format")
    parser.add_argument("--save-chat", action="store_true", help="Save the full chat history to a file")
    return parser.parse_args()


def main():
    args = parse_args()
    client = get_claude_client()
    template = load_prompt(args.prompt)

    response, messages = generate_response(client, template, args.topic)

    formatted = convert_to_format(client, response, messages, args.format)
    output_file = save_output(formatted, args.topic, args.format)

    if args.save_chat:
        chat_file = save_chat_log(messages, args.topic)


if __name__ == "__main__":
    main()
