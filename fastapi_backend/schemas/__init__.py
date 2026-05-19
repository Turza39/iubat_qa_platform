from .user import (
    UserPublicSchema,
    UserSchema,
    UserCreateSchema,
    RegisterSchema,
    LoginSchema,
    TokenSchema,
    TokenRefreshSchema,
    UserUpdateSchema,
    UserProfileSchema,
    VerificationRequestSchema,
    VerificationSubmitSchema,
)
from .tag import TagSchema, TagCreateSchema, TagUpdateSchema
from .question import (
    QuestionListSchema,
    QuestionDetailSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionWithAnswersSchema,
    TagListSchema
)
from .answer import AnswerSchema, AnswerCreateSchema, AnswerUpdateSchema
from .vote import VoteSchema, VoteToggleResponseSchema, VoteStatsSchema

__all__ = [
    "UserPublicSchema",
    "UserSchema",
    "UserCreateSchema",
    "RegisterSchema",
    "LoginSchema",
    "TokenSchema",
    "TokenRefreshSchema",
    "UserUpdateSchema",
    "UserProfileSchema",
    "VerificationRequestSchema",
    "VerificationSubmitSchema",
    "TagSchema",
    "TagCreateSchema",
    "TagUpdateSchema",
    "QuestionListSchema",
    "QuestionDetailSchema",
    "QuestionCreateSchema",
    "QuestionUpdateSchema",
    "QuestionWithAnswersSchema",
    "TagListSchema",
    "AnswerSchema",
    "AnswerCreateSchema",
    "AnswerUpdateSchema",
    "VoteSchema",
    "VoteToggleResponseSchema",
    "VoteStatsSchema",
]

# Pydantic v2: rebuild models to resolve forward references/circular imports
try:
    # Call model_rebuild on each imported schema class if available
    for _cls in (
        UserPublicSchema,
        UserSchema,
        UserCreateSchema,
        RegisterSchema,
        LoginSchema,
        TokenSchema,
        TokenRefreshSchema,
        UserUpdateSchema,
        UserProfileSchema,
        VerificationRequestSchema,
        VerificationSubmitSchema,
        TagSchema,
        TagCreateSchema,
        TagUpdateSchema,
        QuestionListSchema,
        QuestionDetailSchema,
        QuestionCreateSchema,
        QuestionUpdateSchema,
        QuestionWithAnswersSchema,
        TagListSchema,
        AnswerSchema,
        AnswerCreateSchema,
        AnswerUpdateSchema,
        VoteSchema,
        VoteToggleResponseSchema,
        VoteStatsSchema,
    ):
        if hasattr(_cls, "model_rebuild"):
            _cls.model_rebuild()
except Exception:
    # If something goes wrong here, let the import proceed; FastAPI will raise
    # errors during runtime which are easier to debug in normal flows.
    pass
