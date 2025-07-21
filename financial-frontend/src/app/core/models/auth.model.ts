export interface LoginForm {
  email: string;
  senha: string;
  lembrar?: boolean;
}

export interface RegisterForm {
  email: string;
  primeiro_nome: string;
  ultimo_nome: string;
  telefone?: string;
  senha: string;
  confirmar_senha: string;
  aceitar_termos: boolean;
}

export interface ValidationErrors {
  [key: string]: string[];
}