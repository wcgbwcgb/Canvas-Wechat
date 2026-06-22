"""Pydantic models for iLink Bot API request/response payloads."""

from pydantic import BaseModel, Field


# --- QR Code / Auth ---

class QRCodeResponse(BaseModel):
    qrcode: str = ""
    errcode: int | None = None
    errmsg: str | None = None


class QRCodeStatusResponse(BaseModel):
    status: str = ""  # "waiting", "confirmed", "expired"
    bot_token: str | None = None
    errcode: int | None = None
    errmsg: str | None = None


# --- Message Items ---

class TextItem(BaseModel):
    type: int = 1
    text_item: dict = Field(default_factory=lambda: {"text": ""})


class ImageItem(BaseModel):
    type: int = 2
    image_item: dict = Field(default_factory=dict)


class FileItem(BaseModel):
    type: int = 4
    file_item: dict = Field(default_factory=dict)


# --- Incoming Message ---

class IncomingMessage(BaseModel):
    """A single message received from the getupdates endpoint."""

    from_user_id: str = ""
    to_user_id: str = ""
    message_type: int = 1  # 1=text, 2=image, 3=voice, 4=file, 5=video
    message_state: int = 1
    context_token: str | None = None
    item_list: list[dict] = Field(default_factory=list)
    message_id: str | None = None
    create_time: int | None = None

    @property
    def text(self) -> str:
        """Extract text content from the first text item."""
        for item in self.item_list:
            if item.get("type") == 1:
                return item.get("text_item", {}).get("text", "")
        return ""


# --- Outgoing Message ---

class OutgoingMsg(BaseModel):
    to_user_id: str
    message_type: int = 2  # reply
    message_state: int = 2
    context_token: str = ""
    item_list: list[dict] = Field(default_factory=list)


class SendMessageRequest(BaseModel):
    msg: OutgoingMsg


class SendMessageResponse(BaseModel):
    ret: int = 0
    errcode: int | None = None
    errmsg: str | None = None
    msg_id: str | None = None


# --- getupdates ---

class GetUpdatesRequest(BaseModel):
    get_updates_buf: str = ""
    base_info: dict = Field(default_factory=lambda: {"channel_version": "1.0.3"})


class GetUpdatesResponse(BaseModel):
    msgs: list[IncomingMessage] = Field(default_factory=list)
    get_updates_buf: str = ""
    errcode: int | None = None
    errmsg: str | None = None


# --- getconfig ---

class GetConfigRequest(BaseModel):
    base_info: dict = Field(default_factory=lambda: {"channel_version": "1.0.3"})


class GetConfigResponse(BaseModel):
    typing_ticket: str | None = None
