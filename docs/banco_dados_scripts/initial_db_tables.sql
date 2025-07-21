-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de usuários
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    primeiro_nome VARCHAR(100) NOT NULL,
    ultimo_nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de categorias
CREATE TABLE categorias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    cor VARCHAR(7), -- Para cores hex (#FFFFFF)
    icone VARCHAR(50),
    tipo VARCHAR(20) CHECK (tipo IN ('receita', 'despesa')) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, nome, tipo)
);

-- Tabela de contas bancárias
CREATE TABLE contas_bancarias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    nome_banco VARCHAR(100),
    tipo_conta VARCHAR(20) CHECK (tipo_conta IN ('corrente', 'poupanca', 'investimento', 'dinheiro')) NOT NULL,
    saldo DECIMAL(15,2) DEFAULT 0.00,
    saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de cartões de crédito
CREATE TABLE cartoes_credito (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    nome_banco VARCHAR(100),
    ultimos_digitos VARCHAR(4),
    limite_credito DECIMAL(15,2) NOT NULL,
    saldo_atual DECIMAL(15,2) DEFAULT 0.00,
    dia_fechamento INTEGER CHECK (dia_fechamento BETWEEN 1 AND 31) NOT NULL,
    dia_vencimento INTEGER CHECK (dia_vencimento BETWEEN 1 AND 31) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de empréstimos
CREATE TABLE emprestimos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    tipo_emprestimo VARCHAR(20) CHECK (tipo_emprestimo IN ('pessoal', 'habitacional', 'veiculo', 'estudantil', 'empresarial')) NOT NULL,
    valor_principal DECIMAL(15,2) NOT NULL,
    saldo_devedor DECIMAL(15,2) NOT NULL,
    taxa_juros DECIMAL(5,2) NOT NULL, -- Taxa de juros anual
    total_parcelas INTEGER NOT NULL,
    parcelas_pagas INTEGER DEFAULT 0,
    valor_parcela DECIMAL(15,2) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    proximo_vencimento DATE,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de transações
CREATE TABLE transacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    categoria_id UUID REFERENCES categorias(id) ON DELETE SET NULL,
    conta_bancaria_id UUID REFERENCES contas_bancarias(id) ON DELETE SET NULL,
    cartao_credito_id UUID REFERENCES cartoes_credito(id) ON DELETE SET NULL,
    emprestimo_id UUID REFERENCES emprestimos(id) ON DELETE SET NULL,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    tipo_transacao VARCHAR(20) CHECK (tipo_transacao IN ('receita', 'despesa', 'transferencia', 'pagamento_emprestimo', 'pagamento_cartao')) NOT NULL,
    data_transacao DATE NOT NULL,
    data_vencimento DATE, -- Para transações futuras/agendadas
    eh_recorrente BOOLEAN DEFAULT false,
    frequencia_recorrencia VARCHAR(20) CHECK (frequencia_recorrencia IN ('diaria', 'semanal', 'mensal', 'anual')),
    data_fim_recorrencia DATE,
    status VARCHAR(20) CHECK (status IN ('pendente', 'concluida', 'cancelada')) DEFAULT 'concluida',
    observacoes TEXT,
    etiquetas TEXT[], -- Array de tags
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de faturas de cartão de crédito
CREATE TABLE faturas_cartao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cartao_credito_id UUID NOT NULL REFERENCES cartoes_credito(id) ON DELETE CASCADE,
    mes_referencia DATE NOT NULL, -- Mês de referência da fatura
    valor_total DECIMAL(15,2) NOT NULL,
    pagamento_minimo DECIMAL(15,2) NOT NULL,
    data_vencimento DATE NOT NULL,
    data_fechamento DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('aberta', 'fechada', 'paga', 'vencida')) DEFAULT 'aberta',
    valor_pago DECIMAL(15,2) DEFAULT 0.00,
    data_pagamento DATE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de parcelas de empréstimo
CREATE TABLE parcelas_emprestimo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emprestimo_id UUID NOT NULL REFERENCES emprestimos(id) ON DELETE CASCADE,
    numero_parcela INTEGER NOT NULL,
    data_vencimento DATE NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    valor_principal DECIMAL(15,2) NOT NULL,
    valor_juros DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pendente', 'paga', 'vencida')) DEFAULT 'pendente',
    data_pagamento DATE,
    valor_pago DECIMAL(15,2) DEFAULT 0.00,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(emprestimo_id, numero_parcela)
);

-- Tabela de orçamentos
CREATE TABLE orcamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    categoria_id UUID REFERENCES categorias(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    valor_limite DECIMAL(15,2) NOT NULL,
    valor_gasto DECIMAL(15,2) DEFAULT 0.00,
    tipo_periodo VARCHAR(20) CHECK (tipo_periodo IN ('mensal', 'anual')) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de metas financeiras
CREATE TABLE metas_financeiras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor_objetivo DECIMAL(15,2) NOT NULL,
    valor_atual DECIMAL(15,2) DEFAULT 0.00,
    data_inicio DATE NOT NULL,
    data_objetivo DATE NOT NULL,
    tipo_meta VARCHAR(20) CHECK (tipo_meta IN ('economia', 'investimento', 'compra', 'viagem', 'emergencia')) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('ativa', 'concluida', 'pausada', 'cancelada')) DEFAULT 'ativa',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de alertas e notificações
CREATE TABLE alertas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo_alerta VARCHAR(30) CHECK (tipo_alerta IN ('vencimento_fatura', 'vencimento_emprestimo', 'limite_orcamento', 'meta_atingida', 'saldo_baixo')) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    mensagem TEXT NOT NULL,
    data_alerta TIMESTAMP WITH TIME ZONE NOT NULL,
    lido BOOLEAN DEFAULT false,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de configurações do usuário
CREATE TABLE configuracoes_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    moeda VARCHAR(3) DEFAULT 'BRL',
    formato_data VARCHAR(10) DEFAULT 'DD/MM/YYYY',
    tema VARCHAR(10) CHECK (tema IN ('claro', 'escuro', 'auto')) DEFAULT 'auto',
    notificacoes_email BOOLEAN DEFAULT true,
    notificacoes_push BOOLEAN DEFAULT true,
    dia_fechamento_mes INTEGER CHECK (dia_fechamento_mes BETWEEN 1 AND 31) DEFAULT 1,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id)
);

-- Índices para performance
CREATE INDEX idx_transacoes_usuario_id ON transacoes(usuario_id);
CREATE INDEX idx_transacoes_data ON transacoes(data_transacao);
CREATE INDEX idx_transacoes_categoria ON transacoes(categoria_id);
CREATE INDEX idx_transacoes_tipo ON transacoes(tipo_transacao);
CREATE INDEX idx_faturas_cartao_id ON faturas_cartao(cartao_credito_id);
CREATE INDEX idx_parcelas_emprestimo_id ON parcelas_emprestimo(emprestimo_id);
CREATE INDEX idx_parcelas_vencimento ON parcelas_emprestimo(data_vencimento);
CREATE INDEX idx_alertas_usuario_id ON alertas(usuario_id);
CREATE INDEX idx_alertas_data ON alertas(data_alerta);

-- Triggers para atualizar atualizado_em
CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_usuarios_atualizado_em BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_categorias_atualizado_em BEFORE UPDATE ON categorias FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_contas_bancarias_atualizado_em BEFORE UPDATE ON contas_bancarias FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_cartoes_credito_atualizado_em BEFORE UPDATE ON cartoes_credito FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_emprestimos_atualizado_em BEFORE UPDATE ON emprestimos FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_transacoes_atualizado_em BEFORE UPDATE ON transacoes FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_faturas_cartao_atualizado_em BEFORE UPDATE ON faturas_cartao FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_parcelas_emprestimo_atualizado_em BEFORE UPDATE ON parcelas_emprestimo FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_orcamentos_atualizado_em BEFORE UPDATE ON orcamentos FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_metas_financeiras_atualizado_em BEFORE UPDATE ON metas_financeiras FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trigger_configuracoes_usuario_atualizado_em BEFORE UPDATE ON configuracoes_usuario FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

-- Views úteis para relatórios
CREATE VIEW vw_resumo_financeiro AS
SELECT 
    u.id as usuario_id,
    u.primeiro_nome || ' ' || u.ultimo_nome as nome_completo,
    COALESCE(cb.total_contas, 0) as total_contas_bancarias,
    COALESCE(cc.total_cartoes, 0) as total_divida_cartoes,
    COALESCE(emp.total_emprestimos, 0) as total_divida_emprestimos,
    COALESCE(cb.total_contas, 0) - COALESCE(cc.total_cartoes, 0) - COALESCE(emp.total_emprestimos, 0) as patrimonio_liquido
FROM usuarios u
LEFT JOIN (
    SELECT usuario_id, SUM(saldo) as total_contas
    FROM contas_bancarias 
    WHERE ativo = true
    GROUP BY usuario_id
) cb ON u.id = cb.usuario_id
LEFT JOIN (
    SELECT usuario_id, SUM(saldo_atual) as total_cartoes
    FROM cartoes_credito 
    WHERE ativo = true
    GROUP BY usuario_id
) cc ON u.id = cc.usuario_id
LEFT JOIN (
    SELECT usuario_id, SUM(saldo_devedor) as total_emprestimos
    FROM emprestimos 
    WHERE ativo = true
    GROUP BY usuario_id
) emp ON u.id = emp.usuario_id
WHERE u.ativo = true;

-- View para transações do mês atual
CREATE VIEW vw_transacoes_mes_atual AS
SELECT 
    t.*,
    c.nome as categoria_nome,
    c.tipo as categoria_tipo,
    cb.nome as conta_nome,
    cc.nome as cartao_nome
FROM transacoes t
LEFT JOIN categorias c ON t.categoria_id = c.id
LEFT JOIN contas_bancarias cb ON t.conta_bancaria_id = cb.id
LEFT JOIN cartoes_credito cc ON t.cartao_credito_id = cc.id
WHERE EXTRACT(YEAR FROM t.data_transacao) = EXTRACT(YEAR FROM CURRENT_DATE)
  AND EXTRACT(MONTH FROM t.data_transacao) = EXTRACT(MONTH FROM CURRENT_DATE)
  AND t.status = 'concluida';

-- Função para calcular próximo vencimento de empréstimo
CREATE OR REPLACE FUNCTION calcular_proximo_vencimento_emprestimo(emprestimo_uuid UUID)
RETURNS DATE AS $$
DECLARE
    proximo_vencimento DATE;
BEGIN
    SELECT MIN(data_vencimento) INTO proximo_vencimento
    FROM parcelas_emprestimo
    WHERE emprestimo_id = emprestimo_uuid
      AND status = 'pendente'
      AND data_vencimento >= CURRENT_DATE;
    
    RETURN proximo_vencimento;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar saldo da conta após transação
CREATE OR REPLACE FUNCTION atualizar_saldo_conta()
RETURNS TRIGGER AS $$
BEGIN
    -- Se é uma nova transação
    IF TG_OP = 'INSERT' THEN
        IF NEW.conta_bancaria_id IS NOT NULL THEN
            IF NEW.tipo_transacao = 'receita' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo + NEW.valor 
                WHERE id = NEW.conta_bancaria_id;
            ELSIF NEW.tipo_transacao = 'despesa' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo - NEW.valor 
                WHERE id = NEW.conta_bancaria_id;
            END IF;
        END IF;
        RETURN NEW;
    END IF;
    
    -- Se é uma atualização de transação
    IF TG_OP = 'UPDATE' THEN
        -- Reverter transação antiga se mudou de conta
        IF OLD.conta_bancaria_id IS NOT NULL AND OLD.conta_bancaria_id != NEW.conta_bancaria_id THEN
            IF OLD.tipo_transacao = 'receita' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo - OLD.valor 
                WHERE id = OLD.conta_bancaria_id;
            ELSIF OLD.tipo_transacao = 'despesa' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo + OLD.valor 
                WHERE id = OLD.conta_bancaria_id;
            END IF;
        END IF;
        
        -- Aplicar nova transação
        IF NEW.conta_bancaria_id IS NOT NULL THEN
            IF NEW.tipo_transacao = 'receita' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo + NEW.valor 
                WHERE id = NEW.conta_bancaria_id;
            ELSIF NEW.tipo_transacao = 'despesa' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo - NEW.valor 
                WHERE id = NEW.conta_bancaria_id;
            END IF;
        END IF;
        RETURN NEW;
    END IF;
    
    -- Se é uma exclusão de transação
    IF TG_OP = 'DELETE' THEN
        IF OLD.conta_bancaria_id IS NOT NULL THEN
            IF OLD.tipo_transacao = 'receita' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo - OLD.valor 
                WHERE id = OLD.conta_bancaria_id;
            ELSIF OLD.tipo_transacao = 'despesa' THEN
                UPDATE contas_bancarias 
                SET saldo = saldo + OLD.valor 
                WHERE id = OLD.conta_bancaria_id;
            END IF;
        END IF;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar saldo automaticamente
CREATE TRIGGER trigger_atualizar_saldo_conta
    AFTER INSERT OR UPDATE OR DELETE ON transacoes
    FOR EACH ROW EXECUTE FUNCTION atualizar_saldo_conta();

-- Inserir categorias padrão
INSERT INTO categorias (id, usuario_id, nome, descricao, tipo, cor, icone) VALUES
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Alimentação', 'Gastos com comida e bebida', 'despesa', '#FF6B6B', 'restaurant'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Transporte', 'Gastos com locomoção', 'despesa', '#4ECDC4', 'directions_car'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Moradia', 'Aluguel, financiamento, condomínio', 'despesa', '#45B7D1', 'home'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Saúde', 'Médicos, medicamentos, plano de saúde', 'despesa', '#96CEB4', 'local_hospital'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Educação', 'Cursos, livros, material escolar', 'despesa', '#FFEAA7', 'school'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Lazer', 'Entretenimento e diversão', 'despesa', '#DDA0DD', 'sports_esports'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Salário', 'Salário e bonificações', 'receita', '#55A3FF', 'work'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Freelance', 'Trabalhos extras', 'receita', '#26DE81', 'business_center'),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Investimentos', 'Rendimentos de investimentos', 'receita', '#FD79A8', 'trending_up');