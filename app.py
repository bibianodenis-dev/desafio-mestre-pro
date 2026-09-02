import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from sqlalchemy import func
from database.db import db, init_db, Questao, Usuario, Resposta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'desafio_mestre_pro_secret_key_2026')

# Configuração do SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'quiz.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Banco de Dados e Importação Automática do Excel
init_db(app)

# ==============================================================================
# FUNÇÕES AUXILIARES DE HELPER & GAMIFICAÇÃO
# ==============================================================================

def get_usuario_padrao():
    """Retorna o usuário padrão (ID 1: Concurseiro)."""
    user = Usuario.query.first()
    if not user:
        user = Usuario(nome="Concurseiro")
        db.session.add(user)
        db.session.commit()
    return user

def calcular_nivel_usuario(pontos):
    """Retorna a patente e progresso do usuário com base nos pontos."""
    if pontos < 100:
        return {'title': 'Iniciante', 'points': pontos, 'progress': min(100, (pontos / 100) * 100), 'next_target': 'Próximo nível: Estudante Focado (100 pts)'}
    elif pontos < 300:
        return {'title': 'Estudante Focado', 'points': pontos, 'progress': min(100, ((pontos - 100) / 200) * 100), 'next_target': 'Próximo nível: Concurseiro Avançado (300 pts)'}
    elif pontos < 600:
        return {'title': 'Concurseiro Avançado', 'points': pontos, 'progress': min(100, ((pontos - 300) / 300) * 100), 'next_target': 'Próximo nível: Mestre dos Concursos (600 pts)'}
    else:
        return {'title': 'Mestre dos Concursos', 'points': pontos, 'progress': 100, 'next_target': 'Nível Máximo Alcançado! 🏆'}

def avaliar_conquistas(user_id):
    """Verifica e retorna a lista de medalhas/conquistas desbloqueadas."""
    respostas = Resposta.query.filter_by(usuario_id=user_id).all()
    total_resp = len(respostas)
    total_acertos = sum(1 for r in respostas if r.acertou)
    pct_geral = (total_acertos / total_resp * 100) if total_resp > 0 else 0

    conquistas = []

    if total_resp >= 1:
        conquistas.append({
            'icon': '🎯',
            'title': 'Primeiro Passo',
            'desc': 'Respondeu à primeira questão na plataforma'
        })
    if total_acertos >= 10:
        conquistas.append({
            'icon': '⚡',
            'title': 'Mira Laser',
            'desc': 'Conquistou 10 respostas corretas'
        })
    if total_resp >= 100:
        conquistas.append({
            'icon': '🏆',
            'title': 'Maratonista',
            'desc': 'Respondeu a 100 questões no total'
        })
    if total_resp >= 20 and pct_geral >= 80:
        conquistas.append({
            'icon': '🌟',
            'title': 'Especialista Mestre',
            'desc': 'Atingiu mais de 80% de aproveitamento geral'
        })
    if any(r.acertou and r.tempo_resposta > 0 and r.tempo_resposta <= 10 for r in respostas):
        conquistas.append({
            'icon': '⏱️',
            'title': 'Rápido no Gatilho',
            'desc': 'Acertou uma questão em menos de 10 segundos'
        })

    return conquistas

# ==============================================================================
# ROTAS DA APLICAÇÃO
# ==============================================================================

@app.route('/zerar_historico', methods=['POST'])
def zerar_historico():
    """Zera todo o histórico de respostas, pontuação e progresso do usuário."""
    user = get_usuario_padrao()
    Resposta.query.filter_by(usuario_id=user.id).delete()
    db.session.commit()
    session.pop('quiz_ids', None)
    session.pop('quiz_index', None)
    session.pop('respostas_sessao', None)
    flash('Seu histórico de estudos, estatísticas e pontuação foram zerados com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Tela Inicial: Exibe dashboard rápido, filtros e configuração de simulado."""
    user = get_usuario_padrao()
    
    # Obter listas distintas de Temas, Subtemas e Bancas para os selects
    temas = [t[0] for t in db.session.query(Questao.tema).distinct().order_by(Questao.tema).all()]
    subtemas = [s[0] for s in db.session.query(Questao.subtema).distinct().order_by(Questao.subtema).all()]
    bancas = [b[0] for b in db.session.query(Questao.banca).distinct().order_by(Questao.banca).all()]

    # Mapeamento de subtemas por tema para dinamismo em JS
    subtemas_por_tema = {}
    for t in temas:
        subs = [s[0] for s in db.session.query(Questao.subtema).filter(Questao.tema == t).distinct().all()]
        subtemas_por_tema[t] = subs

    total_questoes = Questao.query.filter_by(ativo=True).count()
    total_respondidas = Resposta.query.filter_by(usuario_id=user.id).count()

    # Cálculo da pontuação total acumulada
    respostas_corretas = Resposta.query.filter_by(usuario_id=user.id, acertou=True).all()
    pontos_totais = sum(r.questao.pontuacao for r in respostas_corretas if r.questao)

    user_level = calcular_nivel_usuario(pontos_totais)

    return render_template(
        'index.html',
        temas=temas,
        subtemas=subtemas,
        bancas=bancas,
        subtemas_por_tema=subtemas_por_tema,
        total_questoes=total_questoes,
        total_respondidas=total_respondidas,
        user_level=user_level
    )

@app.route('/iniciar_quiz', methods=['POST'])
def iniciar_quiz():
    """Processa o formulário de filtros e inicia uma nova sessão de Quiz."""
    user = get_usuario_padrao()

    tema = request.form.get('tema', 'Todos')
    subtema = request.form.get('subtema', 'Todos')
    nivel = request.form.get('nivel', 'Todos')
    banca = request.form.get('banca', 'Todas')
    quantidade = int(request.form.get('quantidade', 10))
    modo = request.form.get('modo', 'Aleatório')
    evitar_repetidas = request.form.get('evitar_repetidas') == 'true'
    usar_cronometro = request.form.get('usar_cronometro') == 'true'
    tempo_limite = int(request.form.get('tempo_limite', 60)) if usar_cronometro else 0

    query = Questao.query.filter_by(ativo=True)

    if tema != 'Todos':
        query = query.filter_by(tema=tema)
    if subtema != 'Todos':
        query = query.filter_by(subtema=subtema)
    if nivel != 'Todos':
        query = query.filter_by(nivel=nivel)
    if banca != 'Todas':
        query = query.filter_by(banca=banca)

    # Filtrar inéditas se solicitado
    if evitar_repetidas:
        respondidas_ids = [r.questao_id for r in Resposta.query.filter_by(usuario_id=user.id).all()]
        if respondidas_ids:
            query_ineditas = query.filter(~Questao.id.in_(respondidas_ids))
            if query_ineditas.count() > 0:
                query = query_ineditas

    # Modo de ordenação
    if modo == 'Aleatório':
        query = query.order_by(func.random())
    else:
        query = query.order_by(Questao.id.asc())

    if quantidade > 0:
        questoes_filtradas = query.limit(quantidade).all()
    else:
        questoes_filtradas = query.all()

    if not questoes_filtradas:
        flash('Nenhuma questão encontrada com os filtros selecionados. Tente expandir os critérios.', 'warning')
        return redirect(url_for('index'))

    # Salvar sessão do quiz
    session['quiz_ids'] = [q.id for q in questoes_filtradas]
    session['quiz_index'] = 0
    session['usar_cronometro'] = usar_cronometro
    session['tempo_limite'] = tempo_limite
    session['respostas_sessao'] = []

    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    """Exibe a questão atual do simulado."""
    quiz_ids = session.get('quiz_ids', [])
    quiz_index = session.get('quiz_index', 0)

    if not quiz_ids or quiz_index >= len(quiz_ids):
        return redirect(url_for('resultado'))

    questao_id = quiz_ids[quiz_index]
    questao = Questao.query.get_or_404(questao_id)

    sessao_info = {
        'index': quiz_index,
        'total': len(quiz_ids),
        'usar_cronometro': session.get('usar_cronometro', True),
        'tempo_limite': session.get('tempo_limite', 60)
    }

    return render_template('quiz.html', questao=questao, sessao=sessao_info)

@app.route('/responder', methods=['POST'])
def responder_questao():
    """Endpoint AJAX para validar a resposta do usuário e registrar no banco."""
    user = get_usuario_padrao()

    questao_id = int(request.form.get('questao_id'))
    resposta_usuario = request.form.get('resposta_usuario', '').strip()
    tempo_resposta = int(request.form.get('tempo_resposta', 0))

    questao = Questao.query.get_or_404(questao_id)
    acertou = (resposta_usuario.lower() == questao.resposta_correta.lower())

    # Salvar no banco SQLite
    nova_resposta = Resposta(
        usuario_id=user.id,
        questao_id=questao.id,
        resposta_usuario=resposta_usuario,
        acertou=acertou,
        tempo_resposta=tempo_resposta,
        data_resposta=datetime.utcnow()
    )
    db.session.add(nova_resposta)
    db.session.commit()

    # Atualizar estatística da sessão atual
    respostas_sessao = session.get('respostas_sessao', [])
    respostas_sessao.append({
        'questao_id': questao.id,
        'resposta_usuario': resposta_usuario,
        'acertou': acertou,
        'pontos': questao.pontuacao if acertou else 0,
        'tempo': tempo_resposta
    })
    session['respostas_sessao'] = respostas_sessao

    return jsonify({
        'acertou': acertou,
        'resposta_correta': questao.resposta_correta,
        'resposta_usuario': resposta_usuario,
        'explicacao': questao.explicacao,
        'pontos': questao.pontuacao if acertou else 0
    })

@app.route('/proxima_questao')
def proxima_questao():
    """Avança o ponteiro da questão na sessão atual."""
    session['quiz_index'] = session.get('quiz_index', 0) + 1
    return redirect(url_for('quiz'))

@app.route('/resultado')
def resultado():
    """Exibe a tela de finalização do simulado com estatísticas da rodada e conquistas."""
    user = get_usuario_padrao()
    respostas_sessao = session.get('respostas_sessao', [])

    if not respostas_sessao:
        flash('Nenhum simulado concluído recentemente.', 'info')
        return redirect(url_for('index'))

    total = len(respostas_sessao)
    acertos = sum(1 for r in respostas_sessao if r['acertou'])
    erros = total - acertos
    percentual = round((acertos / total * 100), 1) if total > 0 else 0
    tempo_total = sum(r['tempo'] for r in respostas_sessao)
    tempo_medio = round(tempo_total / total, 1) if total > 0 else 0
    pontos_obtidos = sum(r['pontos'] for r in respostas_sessao)

    # Pontuação acumulada total
    respostas_corretas_totais = Resposta.query.filter_by(usuario_id=user.id, acertou=True).all()
    pontuacao_total = sum(r.questao.pontuacao for r in respostas_corretas_totais if r.questao)

    conquistas = avaliar_conquistas(user.id)

    resumo = {
        'total': total,
        'acertos': acertos,
        'erros': erros,
        'percentual': percentual,
        'tempo_medio': tempo_medio,
        'tempo_total': tempo_total,
        'pontos_obtidos': pontos_obtidos,
        'pontuacao_total': pontuacao_total
    }

    return render_template('resultado.html', resumo=resumo, conquistas=conquistas)

@app.route('/dashboard')
def dashboard():
    """Exibe o Painel Analítico com KPIs, Mapas de Erro e Gráficos Chart.js."""
    user = get_usuario_padrao()
    respostas = Resposta.query.filter_by(usuario_id=user.id).order_by(Resposta.data_resposta.asc()).all()

    total_respondidas = len(respostas)
    total_acertos = sum(1 for r in respostas if r.acertou)
    total_erros = total_respondidas - total_acertos
    percentual_geral = round((total_acertos / total_respondidas * 100), 1) if total_respondidas > 0 else 0
    tempo_medio_geral = round(sum(r.tempo_resposta for r in respostas) / total_respondidas, 1) if total_respondidas > 0 else 0
    pontuacao_total = sum(r.questao.pontuacao for r in respostas if r.acertou and r.questao)

    # 1. MAPA DE ERROS POR TEMA (Ordenado do Pior para o Melhor)
    temas = db.session.query(Questao.tema).distinct().all()
    mapa_erros_tema = []
    temas_stats = []

    for (t,) in temas:
        resps_tema = [r for r in respostas if r.questao and r.questao.tema == t]
        tot = len(resps_tema)
        if tot > 0:
            acert = sum(1 for r in resps_tema if r.acertou)
            err = tot - acert
            pct_erro = round((err / tot * 100), 1)
            pct_acerto = round((acert / tot * 100), 1)
            tempo_m = round(sum(r.tempo_resposta for r in resps_tema) / tot, 1)

            mapa_erros_tema.append({
                'tema': t,
                'total': tot,
                'erros': err,
                'percentual_erro': pct_erro,
                'percentual_acerto': pct_acerto
            })

            temas_stats.append({
                'tema': t,
                'total_acertos': acert,
                'tempo_medio': tempo_m
            })

    # Ordenar pior desempenho (maior erro) primeiro
    mapa_erros_tema.sort(key=lambda x: x['percentual_erro'], reverse=True)

    # 2. MAPA DE ERROS POR SUBTEMA & IDENTIFICAÇÃO DE MAIS FORTE / FRACO
    subtemas = db.session.query(Questao.subtema).distinct().all()
    subtemas_stats = []

    for (s,) in subtemas:
        resps_sub = [r for r in respostas if r.questao and r.questao.subtema == s]
        tot = len(resps_sub)
        if tot > 0:
            acert = sum(1 for r in resps_sub if r.acertou)
            pct_acerto = round((acert / tot * 100), 1)
            subtemas_stats.append({
                'subtema': s,
                'total': tot,
                'acertos': acert,
                'percentual_acerto': pct_acerto
            })

    subtemas_stats.sort(key=lambda x: x['percentual_acerto'], reverse=True)

    subtema_mais_forte = subtemas_stats[0]['subtema'] if subtemas_stats else 'Nenhum'
    subtema_mais_fraco = subtemas_stats[-1]['subtema'] if subtemas_stats else 'Nenhum'

    # 3. EVOLUÇÃO HISTÓRICA CUMULATIVA
    historico = []
    acertos_cum = 0
    for idx, r in enumerate(respostas, start=1):
        if r.acertou:
            acertos_cum += 1
        pct_cum = round((acertos_cum / idx * 100), 1)
        data_fmt = r.data_resposta.strftime('%d/%m %H:%M') if r.data_resposta else f'Item #{idx}'
        historico.append({
            'data': data_fmt,
            'acerto_cumulativo_pct': pct_cum
        })

    stats = {
        'total_respondidas': total_respondidas,
        'total_acertos': total_acertos,
        'total_erros': total_erros,
        'percentual_geral': percentual_geral,
        'tempo_medio_geral': tempo_medio_geral,
        'pontuacao_total': pontuacao_total,
        'mapa_erros_tema': mapa_erros_tema,
        'subtemas_stats': subtemas_stats,
        'subtema_mais_forte': subtema_mais_forte,
        'subtema_mais_fraco': subtema_mais_fraco,
        'temas_stats': temas_stats,
        'historico': historico
    }

    return render_template('dashboard.html', stats=stats)

@app.route('/revisar')
def revisar():
    """Interface do Caderno de Erros para filtrar e refazer apenas questões incorretas."""
    user = get_usuario_padrao()

    filtro_tema = request.args.get('tema', 'Todos')
    filtro_subtema = request.args.get('subtema', 'Todos')
    filtro_nivel = request.args.get('nivel', 'Todos')

    query = Resposta.query.filter_by(usuario_id=user.id, acertou=False).order_by(Resposta.data_resposta.desc())

    erros_brutos = query.all()
    erros_filtrados = []

    for resp in erros_brutos:
        q = resp.questao
        if not q:
            continue
        if filtro_tema != 'Todos' and q.tema != filtro_tema:
            continue
        if filtro_subtema != 'Todos' and q.subtema != filtro_subtema:
            continue
        if filtro_nivel != 'Todos' and q.nivel != filtro_nivel:
            continue

        erros_filtrados.append({
            'id': resp.id,
            'data_resposta': resp.data_resposta.strftime('%d/%m/%Y %H:%M') if resp.data_resposta else '',
            'questao': q
        })

    temas = [t[0] for t in db.session.query(Questao.tema).distinct().all()]
    subtemas = [s[0] for s in db.session.query(Questao.subtema).distinct().all()]

    return render_template(
        'revisar.html',
        erros=erros_filtrados,
        temas=temas,
        subtemas=subtemas,
        filtro_tema=filtro_tema,
        filtro_subtema=filtro_subtema,
        filtro_nivel=filtro_nivel
    )

@app.route('/iniciar_quiz_erros')
def iniciar_quiz_erros():
    """Inicia um simulado focado em refazer todas as questões que foram erradas."""
    user = get_usuario_padrao()
    respostas_erradas = Resposta.query.filter_by(usuario_id=user.id, acertou=False).all()
    questoes_ids = list(set(r.questao_id for r in respostas_erradas if r.questao))

    if not questoes_ids:
        flash('Você não possui erros pendentes para revisar no momento!', 'success')
        return redirect(url_for('revisar'))

    random.shuffle(questoes_ids)
    session['quiz_ids'] = questoes_ids
    session['quiz_index'] = 0
    session['usar_cronometro'] = True
    session['tempo_limite'] = 60
    session['respostas_sessao'] = []

    return redirect(url_for('quiz'))

@app.route('/refazer_questao_unica/<int:questao_id>')
def refazer_questao_unica(questao_id):
    """Inicia o quiz para responder a uma questão específica do caderno de erros."""
    session['quiz_ids'] = [questao_id]
    session['quiz_index'] = 0
    session['usar_cronometro'] = True
    session['tempo_limite'] = 60
    session['respostas_sessao'] = []
    return redirect(url_for('quiz'))

@app.route('/marcar_revisada/<int:resposta_id>', methods=['POST'])
def marcar_revisada(resposta_id):
    """Remove a questão da lista de erros mantendo o histórico de progresso."""
    resp = Resposta.query.get_or_404(resposta_id)
    # Marcar como acertada para tirar do caderno de erros
    resp.acertou = True
    db.session.commit()
    flash('Questão marcada como revisada com sucesso!', 'success')
    return redirect(url_for('revisar'))

@app.route('/estatisticas')
def estatisticas():
    """Tela de Estatísticas Inteligentes com Recomendações Automáticas de Estudo."""
    user = get_usuario_padrao()
    respostas = Resposta.query.filter_by(usuario_id=user.id).all()

    # Diagnósticos por Tema
    temas = db.session.query(Questao.tema).distinct().all()
    stats_temas = []
    for (t,) in temas:
        resps = [r for r in respostas if r.questao and r.questao.tema == t]
        tot = len(resps)
        if tot > 0:
            acert = sum(1 for r in resps if r.acertou)
            pct = round((acert / tot * 100), 1)
            stats_temas.append({'nome': t, 'pct': pct, 'total': tot})

    stats_temas.sort(key=lambda x: x['pct'], reverse=True)
    tema_mais_forte = stats_temas[0] if stats_temas else {'nome': 'N/A', 'pct': 0}
    tema_mais_fraco = stats_temas[-1] if stats_temas else {'nome': 'N/A', 'pct': 0}

    # Diagnósticos por Subtema
    subtemas = db.session.query(Questao.subtema).distinct().all()
    stats_subs = []
    for (s,) in subtemas:
        resps = [r for r in respostas if r.questao and r.questao.subtema == s]
        tot = len(resps)
        if tot > 0:
            acert = sum(1 for r in resps if r.acertou)
            pct = round((acert / tot * 100), 1)
            stats_subs.append({'nome': s, 'pct': pct, 'total': tot})

    stats_subs.sort(key=lambda x: x['pct'], reverse=True)
    subtema_mais_forte = stats_subs[0] if stats_subs else {'nome': 'N/A', 'pct': 0}
    subtema_mais_fraco = stats_subs[-1] if stats_subs else {'nome': 'N/A', 'pct': 0}

    # Diagnósticos por Nível
    niveis_stats = {}
    niveis_map = {'Fácil': 'facil', 'Médio': 'medio', 'Difícil': 'dificil'}
    for niv_label, niv_key in niveis_map.items():
        resps_n = [r for r in respostas if r.questao and r.questao.nivel in [niv_label, niv_key, niv_key.capitalize()]]
        tot = len(resps_n)
        acert = sum(1 for r in resps_n if r.acertou)
        pct = round((acert / tot * 100), 1) if tot > 0 else 0
        niveis_stats[niv_key] = {
            'total': tot,
            'acertos': acert,
            'pct': pct
        }

    diag = {
        'tema_mais_forte': tema_mais_forte,
        'tema_mais_fraco': tema_mais_fraco,
        'subtema_mais_forte': subtema_mais_forte,
        'subtema_mais_fraco': subtema_mais_fraco,
        'niveis': niveis_stats
    }

    # GERADOR AUTOMÁTICO DE SUGESTÕES DE ESTUDO
    sugestoes = []

    if tema_mais_fraco['nome'] != 'N/A' and tema_mais_fraco['pct'] < 50:
        sugestoes.append({
            'icon': '⚠️',
            'titulo': f'Alerta no Tema: {tema_mais_fraco["nome"]}',
            'mensagem': f'Seu desempenho em {tema_mais_fraco["nome"]} está em {tema_mais_fraco["pct"]}%. Recomenda-se revisar a teoria deste conteúdo prioritariamente.',
            'border_class': 'border-danger',
            'text_class': 'text-danger'
        })

    if subtema_mais_fraco['nome'] != 'N/A' and subtema_mais_fraco['pct'] < 60:
        sugestoes.append({
            'icon': '🎯',
            'titulo': f'Foco de Revisão: {subtema_mais_fraco["nome"]}',
            'mensagem': f'O subtema {subtema_mais_fraco["nome"]} teve aproveitamento de apenas {subtema_mais_fraco["pct"]}%. Faça questões focadas neste tópico.',
            'border_class': 'border-warning',
            'text_class': 'text-warning'
        })

    if niveis_stats['dificil']['pct'] < 40 and niveis_stats['dificil']['total'] > 0:
        sugestoes.append({
            'icon': '🔥',
            'titulo': 'Desafio Nível Difícil',
            'mensagem': 'Seu rendimento nas questões de nível Difícil é inferior a 40%. Pratique simulados sem tempo limite para consolidar o raciocínio.',
            'border_class': 'border-primary',
            'text_class': 'text-primary'
        })

    if not sugestoes:
        sugestoes.append({
            'icon': '✅',
            'titulo': 'Ótimo Rendimento!',
            'mensagem': 'Seu desempenho atual está consistente em todos os temas analisados. Continue praticando simulados em modo aleatório para manter o ritmo!',
            'border_class': 'border-success',
            'text_class': 'text-success'
        })

    return render_template('estatisticas.html', diag=diag, sugestoes=sugestoes)

# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ==============================================================================

if __name__ == '__main__':
    print("Iniciando Desafio Mestre PRO na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
