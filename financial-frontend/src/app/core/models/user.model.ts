export interface User {
  id: string;
  email: string;
  primeiro_nome: string;
  ultimo_nome: string;
  telefone?: string;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface CreateUserRequest {
  email: string;
  primeiro_nome: string;
  ultimo_nome: string;
  telefone?: string;
  senha: string;
  confirmar_senha: string;
}

export interface LoginRequest {
  email: string;
  senha: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  usuario: User;
}