from openai.types.chat.chat_completion import ChatCompletion, Choice
from polyfactory.factories.pydantic_factory import ModelFactory


class OpenAIChoiceFactory(ModelFactory[Choice]):
    __model__ = Choice


class ChatCompletionFactory(ModelFactory[ChatCompletion]):
    __model__ = ChatCompletion
