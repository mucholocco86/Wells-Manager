# ========================================================================
# WELLS FRAMEWORK — SISTEMA DE WALKTHROUGH E MOTOR DE INTERVENÇÃO (WF)
# Baseado na Engenharia Reversa e Documentação do Repositório GitHub
# ========================================================================

init -998 python:
    import renpy.ast as ast

    class WFChoice(object):
        """
        Representação e encapsulamento fiel de um item de Menu.items do Ren'Py.
        Controla a projeção de código, identificação de desvios e estado visual.
        """
        def __init__(self, index, text, item_raw):
            self.index = index
            self.text = text
            self.item_raw = item_raw
            self.jumpTo = "Avança para a história..."
            self.code = "Nenhuma alteração de estado detectada."
            self.isVisible = True
            
            # Desempacota a tupla nativa do SDK [texto, condição, bloco AST]
            if isinstance(item_raw, tuple) and len(item_raw) >= 3:
                self.block = item_raw[2]
            else:
                self.block = getattr(item_raw, "block", None)
                
            self.reconstruir_e_analisar()

        def reconstruir_e_analisar(self):
            """
            Simula o comportamento do CodeView/PathDetection: perfura as camadas
            de tradução e reconstrói o destino estrutural baseado no bloco AST.
            """
            if not isinstance(self.block, list) or not self.block:
                return

            nos_expandidos = list(self.block)
            for no in nos_expandidos:
                # Se encontrar o encapsulamento de tradução nativo do Ren'Py 7/8
                if isinstance(no, renpy.ast.Translate) and hasattr(no, "block") and isinstance(no.block, list):
                    nos_expandidos.extend(no.block)
                    continue

                # Identificação cirúrgica de nós de desvio (Circuito A)
                if isinstance(no, renpy.ast.Jump):
                    self.jumpTo = "Pular para label '{}'".format(no.target)
                    break
                elif isinstance(no, renpy.ast.Call):
                    self.jumpTo = "Chamar label (Call) '{}'".format(no.label)
                    break
                elif isinstance(no, renpy.ast.Python):
                    fonte = no.code.source.strip()
                    self.code = "Alteração: {}".format(fonte)
                    self.jumpTo = "Modifica variáveis do Store"
                    break

        def Action(self):
            """
            Intervenção mecânica na fronteira do Ren'Py antes do ChoiceReturn.
            Libera o fixed rollback para permitir que a seleção programática passe.
            """
            # Implementação exata da descoberta da engenharia reversa do URM
            try:
                renpy.game.log.rollback_is_fixed = False
            except AttributeError:
                pass
                
            # Força o checkpoint não-hard do monitoramento de estado (Circuito B)
            try:
                renpy.game.context().force_checkpoint = True
            except AttributeError:
                pass
                
            # Devolve a execução de forma limpa para a infraestrutura nativa da engine
            return renpy.ui.ChoiceReturn(self.text, self.index)()


    class WFWalkthrough(object):
        """
        Responsável por mapear o estado do Menu atual e gerenciar
        o StoreMonitor virtual do Wells Framework.
        """
        @classmethod
        def processar_menu_atual(cls):
            try:
                context = renpy.game.context()
                if not context.current:
                    return None
                    
                no_atual = renpy.game.script.lookup(context.current)
                if not isinstance(no_atual, renpy.ast.Menu):
                    return None
                    
                mapa_wf = {}
                for idx, item in enumerate(no_atual.items):
                    if item:
                        # Extrai o texto de exibição original da escolha
                        texto = item[0] if isinstance(item, tuple) else getattr(item, "caption", "")
                        # Cria o objeto WFChoice completo com inteligência de bloco
                        mapa_wf[idx] = WFChoice(idx, texto, item)
                        
                return mapa_wf
            except Exception:
                return None
