# 🏆 Desafio Mestre PRO

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple.svg)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4.1-ff6384.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Desafie sua mente. Amplie seu potencial. Alcance novos níveis de aprendizado.**

**Desafio Mestre PRO** é uma plataforma web moderna e interativa de estudos direcionada a concursos públicos. O sistema oferece simulados baseados em questões de **Verdadeiro ou Falso**, com diagnóstico inteligente por subtema, análise gráfica de desempenho e sistema de gamificação.

---

## 🎯 Principais Funcionalidades

- 📚 **Banco de Questões Inédito (100% Autêntico)**:
  - 100 questões inéditas de Língua Portuguesa divididas em 8 temas fundamentais do edital.
  - Gabaritos oficiais comentados com explicação pedagógica detalhada para cada item.
- ⚙️ **Personalização de Simulados**:
  - Filtros por Tema, Subtema, Nível de Dificuldade (Fácil, Médio, Difícil), Qtd. de Questões e Modo (Aleatório / Sequencial).
  - Cronômetro por questão configurável para treinamento de ritmo de prova.
- 📊 **Dashboard Analítico em Tempo Real**:
  - KPIs completos: Respostas, Acertos, Erros, % Aproveitamento Geral, Tempo Médio e Pontuação Acumulada.
  - **Mapa de Erros por Tema**: Ranking ordenado do pior para o melhor desempenho.
  - **Mapa de Erros por Subtema**: Destaque automático do subtema mais forte e mais fraco.
  - **5 Gráficos Interativos (Chart.js)**: Doughnut de Acertos x Erros, Barras de Subtemas, Linha de Evolução Histórica, Tempo Médio e Distribuição de Acertos.
- 💡 **Recomendador Inteligente de Estudos**:
  - Algoritmo que gera sugestões e alertas personalizados com base nas fraquezas detectadas.
- 🏆 **Gamificação Integrada**:
  - Sistema de patentes/níveis (Iniciante, Estudante Focado, Concurseiro Avançado, Mestre dos Concursos) e conquistas desbloqueáveis.
- 🔄 **Caderno de Erros & Reset de Histórico**:
  - Espaço exclusivo para refazer erros e botão para zerar histórico e recomeçar os estudos.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.13, Flask 3.1.0
- **Persistência de Dados**: SQLite 3, SQLAlchemy 2.0.38
- **Processamento de Dados**: Pandas 2.2.3, OpenPyXL 3.1.5
- **Frontend & UI**: HTML5, CSS3 Vanilla (Glassmorphism & Gradients), Bootstrap 5.3.3, Bootstrap Icons
- **Visualização de Dados**: Chart.js 4.4.1

---

## 📂 Estrutura de Pastas

```text
desafio-mestre-pro/
├── app.py                      # Aplicação principal Flask e gerenciador de rotas
├── requirements.txt            # Dependências do projeto
├── .gitignore                  # Arquivos ignorados no Git
├── .env.example                # Modelo de variáveis de ambiente
├── README.md                   # Documentação do projeto
├── database/
│   ├── db.py                   # Modelos SQLAlchemy e importador automático do Excel
│   └── quiz.db                 # Banco SQLite (gerado automaticamente no primeiro start)
├── data/
│   └── quiz_template_estrutura_ideal.xlsx # Base de 100 questões inéditas em Excel
├── templates/
│   ├── base.html               # Layout base com Navbar, Footer e Modais
│   ├── index.html              # Tela inicial com personalização de simulado
│   ├── quiz.html               # Tela de resolução de questões com feedback AJAX
│   ├── resultado.html          # Resumo da rodada e conquistas desbloqueadas
│   ├── dashboard.html          # Painel analítico com mapa de erros e gráficos
│   ├── revisar.html            # Caderno de erros filtrável
│   └── estatisticas.html       # Diagnósticos inteligentes e plano de ação
└── static/
    ├── css/
    │   └── style.css           # Estilos customizados e design system
    └── js/
        └── dashboard.js        # Inicializador dos gráficos Chart.js
```

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- **Python 3.10+** instalado.
- **Git** instalado.

### Passo a Passo

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/bibianodenis-dev/desafio-mestre-pro.git
   cd desafio-mestre-pro
   ```

2. **Criar e Ativar Ambiente Virtual (Recomendado)**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variáveis de Ambiente (Opcional)**:
   ```bash
   cp .env.example .env
   ```

5. **Executar a Aplicação**:
   ```bash
   python app.py
   ```

6. **Acessar no Navegador**:
   Abra a URL: `http://localhost:5000` ou `http://127.0.0.1:5000`

---

## 🔒 Segurança e Boas Práticas

- Nenhuma chave sensível ou segredo hardcoded foi exposto.
- O projeto inclui um `.gitignore` configurado para prevenir o commit acidental de ambientes virtuais (`venv/`), arquivos temporários, caches (`__pycache__/`) e bancos de dados locais de execução.
- Modelo `.env.example` fornecido para fácil desacoplamento de configurações em produção.

---

## 👤 Autor

Desenvolvido por **Bibiano Denis**:
- **GitHub**: [@bibianodenis-dev](https://github.com/bibianodenis-dev)

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE). Sinta-se à vontade para utilizar, estudar e aprimorar o código.
