from pydantic import BaseModel, Field

class FigurinhaSchema(BaseModel):
    """Schema for validating and documenting a sticker (figurinha)."""
    id: int = Field(..., description="Unique identifier of the sticker", example=1)
    nome: str = Field(..., description="Name of the technology pioneer", example="Alan Turing")
    categoria: str = Field(..., description="Sticker category/technology", example="IA")
    imagem_url: str = Field(..., description="Relative URL of the sticker image", example="/figurinhas_img/01-alan-turing.jpg")
    papel: str = Field(..., description="Role and historical contribution of the person", example="Fundamentos da computação")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "nome": "Alan Turing",
                "categoria": "IA",
                "imagem_url": "/figurinhas_img/01-alan-turing.jpg",
                "papel": "Fundamentos da computação e do conceito de IA"
            }
        }
    }


class HealthCheckSchema(BaseModel):
    """Schema for API health check endpoint."""
    mensagem: str = Field(..., example="Olá, mundo! 🌍")
    status: str = Field(..., example="ok")


class UserRegisterSchema(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50, example="dev_pioneiro")
    password: str = Field(..., min_length=6, example="senha123")


class UserLoginSchema(BaseModel):
    """Schema for user login request."""
    username: str = Field(..., example="dev_pioneiro")
    password: str = Field(..., example="senha123")


class TokenSchema(BaseModel):
    """Schema representing JWT auth token response."""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", example="bearer")


class UserResponseSchema(BaseModel):
    """Schema for user representation in responses."""
    id: int = Field(..., example=1)
    username: str = Field(..., example="dev_pioneiro")

