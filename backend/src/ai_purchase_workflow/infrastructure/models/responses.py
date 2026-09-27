from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    content: str


class ChatChoiceResponse(BaseModel):
    message: ChatMessageResponse


class ChatCompletionResponse(BaseModel):
    choices: list[ChatChoiceResponse]
