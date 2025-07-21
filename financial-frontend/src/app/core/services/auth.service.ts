import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { NzMessageService } from 'ng-zorro-antd/message';

import { User, CreateUserRequest, LoginRequest, AuthResponse } from '../models/user.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'financial_token';
  private readonly USER_KEY = 'financial_user';
  
  private currentUserSubject = new BehaviorSubject<User | null>(this.getUserFromStorage());
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasValidToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router,
    private message: NzMessageService
  ) {}

  /**
   * Registra um novo usuário
   */
  register(userData: CreateUserRequest): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/registrar`, userData)
      .pipe(
        tap(() => {
          this.message.success('Usuário criado com sucesso! Faça login para continuar.');
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Realiza login do usuário
   */
  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          this.setSession(response);
          this.message.success(`Bem-vindo, ${response.usuario.primeiro_nome}!`);
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Realiza logout do usuário
   */
  logout(): void {
    this.clearSession();
    this.router.navigate(['/auth/login']);
    this.message.info('Logout realizado com sucesso!');
  }

  /**
   * Obtém informações do usuário atual
   */
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me`)
      .pipe(
        tap((user) => {
          this.currentUserSubject.next(user);
          this.saveUserToStorage(user);
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Verifica se o usuário está autenticado
   */
  isAuthenticated(): boolean {
    return this.hasValidToken();
  }

  /**
   * Obtém o token de acesso
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obtém o usuário atual
   */
  getCurrentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Define a sessão do usuário
   */
  private setSession(authResponse: AuthResponse): void {
    const expiresAt = new Date().getTime() + (authResponse.expires_in * 1000);
    
    localStorage.setItem(this.TOKEN_KEY, authResponse.access_token);
    localStorage.setItem('expires_at', expiresAt.toString());
    this.saveUserToStorage(authResponse.usuario);
    
    this.currentUserSubject.next(authResponse.usuario);
    this.isAuthenticatedSubject.next(true);
  }

  /**
   * Limpa a sessão do usuário
   */
  private clearSession(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('expires_at');
    localStorage.removeItem(this.USER_KEY);
    
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  /**
   * Salva usuário no localStorage
   */
  private saveUserToStorage(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  /**
   * Obtém usuário do localStorage
   */
  private getUserFromStorage(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Verifica se o token é válido
   */
  private hasValidToken(): boolean {
    const token = this.getToken();
    const expiresAt = localStorage.getItem('expires_at');
    
    if (!token || !expiresAt) {
      return false;
    }
    
    const isExpired = new Date().getTime() > parseInt(expiresAt);
    
    if (isExpired) {
      this.clearSession();
      return false;
    }
    
    return true;
  }

  /**
   * Tratamento de erros
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Ocorreu um erro inesperado';
    
    if (error.error instanceof ErrorEvent) {
      // Erro do lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      // Erro do lado do servidor
      if (error.status === 400) {
        errorMessage = error.error?.detail || 'Dados inválidos';
      } else if (error.status === 401) {
        errorMessage = 'Email ou senha incorretos';
        this.clearSession();
      } else if (error.status === 422) {
        // Erros de validação
        if (error.error?.detail) {
          if (Array.isArray(error.error.detail)) {
            errorMessage = error.error.detail.map((err: any) => err.msg).join(', ');
          } else {
            errorMessage = error.error.detail;
          }
        }
      } else if (error.status === 500) {
        errorMessage = 'Erro interno do servidor';
      }
    }
    
    this.message.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}