import os
import pandas as pd
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class Questao(db.Model):
    __tablename__ = 'questoes'

    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(150), nullable=False)
    subtema = db.Column(db.String(150), nullable=False)
    pergunta = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.String(20), nullable=False) # 'Verdadeiro' ou 'Falso'
    explicacao = db.Column(db.Text, nullable=True)
    nivel = db.Column(db.String(50), nullable=False, default='Médio') # 'Fácil', 'Médio', 'Difícil'
    pontuacao = db.Column(db.Integer, nullable=False, default=10)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    banca = db.Column(db.String(100), nullable=False, default='Geral')

    def to_dict(self):
        return {
            'id': self.id,
            'tema': self.tema,
            'subtema': self.subtema,
            'pergunta': self.pergunta,
            'resposta_correta': self.resposta_correta,
            'explicacao': self.explicacao,
            'nivel': self.nivel,
            'pontuacao': self.pontuacao,
            'ativo': self.ativo,
            'banca': self.banca
        }

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class Resposta(db.Model):
    __tablename__ = 'respostas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id'), nullable=False)
    resposta_usuario = db.Column(db.String(20), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)
    tempo_resposta = db.Column(db.Integer, nullable=False, default=0)
    data_resposta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    questao = db.relationship('Questao', backref=db.backref('respostas', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('respostas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'questao_id': self.questao_id,
            'resposta_usuario': self.resposta_usuario,
            'acertou': self.acertou,
            'tempo_resposta': self.tempo_resposta,
            'data_resposta': self.data_resposta.strftime('%Y-%m-%d %H:%M:%S') if self.data_resposta else ''
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Garantir usuário padrão
        if not Usuario.query.first():
            user = Usuario(nome="Concurseiro")
            db.session.add(user)
            db.session.commit()

        # Importar questões automaticamente se a tabela estiver vazia
        if Questao.query.count() == 0:
            import_questoes_from_excel(app.root_path)

def import_questoes_from_excel(base_dir):
    """
    Importa questões do Excel utilizando Pandas.
    Verifica primeiramente data/quiz_template_estrutura_ideal.xlsx e Brasil.xlsx como fallback.
    """
    possible_paths = [
        os.path.join(base_dir, 'data', 'quiz_template_estrutura_ideal.xlsx'),
        os.path.join(base_dir, 'Brasil.xlsx'),
        os.path.join(os.path.dirname(base_dir), 'Brasil.xlsx')
    ]
    
    excel_path = None
    for path in possible_paths:
        if os.path.exists(path):
            excel_path = path
            break

    if not excel_path:
        print("Aviso: Nenhum arquivo Excel encontrado para importação de questões.")
        return

    try:
        df = pd.read_excel(excel_path)
        print(f"Importando questões de: {excel_path} ({len(df)} linhas lidas)")

        # Garantir tratamento de NaN e nomes de colunas
        df.columns = [col.strip().lower() for col in df.columns]
        
        questoes_para_inserir = []
        for _, row in df.iterrows():
            # Extrair e sanitizar valores
            tema = str(row.get('tema', 'Geral')).strip() if pd.notna(row.get('tema')) else 'Geral'
            subtema = str(row.get('subtema', 'Geral')).strip() if pd.notna(row.get('subtema')) else 'Geral'
            pergunta = str(row.get('pergunta', '')).strip() if pd.notna(row.get('pergunta')) else ''
            
            resp_raw = str(row.get('resposta_correta', 'Verdadeiro')).strip() if pd.notna(row.get('resposta_correta')) else 'Verdadeiro'
            resposta_correta = 'Verdadeiro' if resp_raw.lower() in ['verdadeiro', 'v', 'true', '1'] else 'Falso'
            
            explicacao = str(row.get('explicacao', '')).strip() if pd.notna(row.get('explicacao')) else ''
            nivel = str(row.get('nivel', 'Médio')).strip() if pd.notna(row.get('nivel')) else 'Médio'
            
            try:
                pontuacao = int(row.get('pontuacao', 10))
            except (ValueError, TypeError):
                pontuacao = 10
                
            ativo = bool(row.get('ativo', True)) if pd.notna(row.get('ativo')) else True
            banca = str(row.get('banca', 'Geral')).strip() if pd.notna(row.get('banca')) else 'Geral'

            if pergunta:
                q = Questao(
                    tema=tema,
                    subtema=subtema,
                    pergunta=pergunta,
                    resposta_correta=resposta_correta,
                    explicacao=explicacao,
                    nivel=nivel,
                    pontuacao=pontuacao,
                    ativo=ativo,
                    banca=banca
                )
                questoes_para_inserir.append(q)

        if questoes_para_inserir:
            db.session.bulk_save_objects(questoes_para_inserir)
            db.session.commit()
            print(f"Sucesso: {len(questoes_para_inserir)} questões importadas com sucesso para o banco de dados!")
    except Exception as e:
        print(f"Erro ao importar arquivo Excel: {e}")
        db.session.rollback()
