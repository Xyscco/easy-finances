import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { Router } from '@angular/router';
import { NzMessageService } from 'ng-zorro-antd/message';
import { AuthService } from '../../../../core/services/auth.service';
import { CreateUserRequest } from '../../../../core/models/user.model';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  @Output() switchToLogin = new EventEmitter<void>();
  
  registerForm!: FormGroup;
  loading = false;
  passwordVisible = false;
  confirmPasswordVisible = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private message: NzMessageService
  ) {}

  ngOnInit(): void {
    this.initForm();
  }

  private initForm(): void {
    this.registerForm = this.fb.group({
      primeiro_nome: ['', [Validators.required, Validators.minLength(2)]],
      ultimo_nome: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefone: ['', [Validators.pattern(/^\(\d{2}\)\s\d{4,5}-\d{4}$/)]],
      senha: ['', [Validators.required, Validators.minLength(8), this.passwordValidator]],
      confirmar_senha: ['', [Validators.required]],
      aceitar_termos: [false, [Validators.requiredTrue]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  private passwordValidator(control: AbstractControl): { [key: string]: any } | null {
    const value = control.value;
    if (!value) return null;

    const hasNumber = /[0-9]/.test(value);
    const hasUpper = /[A-Z]/.test(value);
    const hasLower = /[a-z]/.test(value);
    const hasSpecial = /[#?!@$%^&*-]/.test(value);

    const valid = hasNumber && hasUpper && hasLower && hasSpecial;
    return valid ? null : { passwordStrength: true };
  }

  private passwordMatchValidator(group: AbstractControl): { [key: string]: any } | null {
    const senha = group.get('senha');
    const confirmarSenha = group.get('confirmar_senha');
    
    if (!senha || !confirmarSenha) return null;
    
    return senha.value === confirmarSenha.value ? null : { passwordMismatch: true };
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.loading = true;
      
      const userData: CreateUserRequest = {
        email: this.registerForm.value.email,
        primeiro_nome: this.registerForm.value.primeiro_nome,
        ultimo_nome: this.registerForm.value.ultimo_nome,
        telefone: this.registerForm.value.telefone,
        senha: this.registerForm.value.senha,
        confirmar_senha: this.registerForm.value.confirmar_senha
      };

      this.authService.register(userData).subscribe({
        next: () => {
          this.message.success('Conta criada com sucesso! Faça login para continuar.');
          this.switchToLogin.emit();
        },
        error: () => {
          this.loading = false;
        },
        complete: () => {
          this.loading = false;
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      control?.markAsTouched();
      control?.updateValueAndValidity();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.registerForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${this.getFieldLabel(fieldName)} é obrigatório`;
      }
      if (field.errors['email']) {
        return 'Email inválido';
      }
      if (field.errors['minlength']) {
        return `${this.getFieldLabel(fieldName)} deve ter pelo menos ${field.errors['minlength'].requiredLength} caracteres`;
      }
      if (field.errors['pattern']) {
        return 'Formato inválido. Use: (11) 99999-9999';
      }
      if (field.errors['passwordStrength']) {
        return 'Senha deve conter: maiúscula, minúscula, número e caractere especial';
      }
      if (field.errors['requiredTrue']) {
        return 'Você deve aceitar os termos de uso';
      }
    }
    
    if (fieldName === 'confirmar_senha' && this.registerForm.errors?.['passwordMismatch'] && field?.touched) {
      return 'As senhas não coincidem';
    }
    
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      primeiro_nome: 'Nome',
      ultimo_nome: 'Sobrenome',
      email: 'Email',
      telefone: 'Telefone',
      senha: 'Senha',
      confirmar_senha: 'Confirmação de senha'
    };
    return labels[fieldName] || fieldName;
  }

  getPasswordStrength(): { strength: number; color: string; text: string } {
    const senha = this.registerForm.get('senha')?.value || '';
    let strength = 0;
    
    if (senha.length >= 8) strength++;
    if (/[a-z]/.test(senha)) strength++;
    if (/[A-Z]/.test(senha)) strength++;
    if (/[0-9]/.test(senha)) strength++;
    if (/[#?!@$%^&*-]/.test(senha)) strength++;

    const strengthMap = [
      { color: '#ff4d4f', text: 'Muito fraca' },
      { color: '#ff7a45', text: 'Fraca' },
      { color: '#ffa940', text: 'Regular' },
      { color: '#52c41a', text: 'Boa' },
      { color: '#389e0d', text: 'Muito boa' }
    ];

    return {
      strength: (strength / 5) * 100,
      color: strengthMap[strength - 1]?.color || '#d9d9d9',
      text: strengthMap[strength - 1]?.text || ''
    };
  }

  onSwitchToLogin(): void {
    this.switchToLogin.emit();
  }

  formatPhone(event: any): void {
    let value = event.target.value.replace(/\D/g, '');
    
    if (value.length <= 11) {
      if (value.length <= 2) {
        value = value.replace(/(\d{0,2})/, '($1');
      } else if (value.length <= 6) {
        value = value.replace(/(\d{2})(\d{0,4})/, '($1) $2');
      } else if (value.length <= 10) {
        value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
      } else {
        value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
      }
    }
    
    this.registerForm.patchValue({ telefone: value });
  }
}