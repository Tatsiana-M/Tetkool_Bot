import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from openai import OpenAI

# Import tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.get_courses import get_courses, tool_definition

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

# Use OpenRouter if available, otherwise fallback to OpenAI
if OPENROUTER_API_KEY:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    print(f"Using OpenRouter with model {LLM_MODEL}")
elif OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"Using OpenAI with model {LLM_MODEL}")
else:
    raise ValueError("Neither OPENROUTER_API_KEY nor OPENAI_API_KEY is set in .env")

# Initialize Bot and Dispatcher
dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Available tools map
AVAILABLE_TOOLS = {
    "get_courses": get_courses
}

TOOLS_DEFINITIONS = [tool_definition]

# Load system prompt
try:
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are a helpful assistant."

# Store conversation history (in-memory for simplicity)
user_conversations = {}

async def process_llm_request(user_id: int, user_message: str):
    messages = user_conversations.get(user_id, [])
    
    # Initialize conversation if empty
    if not messages:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=TOOLS_DEFINITIONS,
            tool_choice="auto", 
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to call a function
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # Append the assistant's message with tool calls to history
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name in AVAILABLE_TOOLS:
                    function_to_call = AVAILABLE_TOOLS[function_name]
                    print(f"Calling tool: {function_name} with args: {function_args}")
                    
                    function_response = function_to_call(**function_args)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    })
            
            # Get a new response from the model where it can see the function response
            second_response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
            )
            final_response = second_response.choices[0].message.content
             # Append final response to history
            messages.append({"role": "assistant", "content": final_response})

        else:
             final_response = response_message.content
             messages.append({"role": "assistant", "content": final_response})
        
        # Save updated history
        user_conversations[user_id] = messages
        return final_response

    except Exception as e:
        logging.error(f"Error calling OpenAI: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    # Reset conversation on start
    user_conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    await message.answer(f"Привет, {message.from_user.full_name}! 👋\nЯ помогу тебе подобрать лучший курс. Напиши, что тебя интересует!")

@dp.message()
async def message_handler(message: Message) -> None:
    user_id = message.from_user.id
    response_text = await process_llm_request(user_id, message.text)
    await message.answer(response_text)

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
