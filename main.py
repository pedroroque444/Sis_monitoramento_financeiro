from banco_dados import configurar_banco
from componentes_tela import JanelaLogin, JanelaPrincipal

class ControladorAplicativo:
    def __init__(self):
        # Garante a inicialização e tabelas corretas do banco de dados ao iniciar
        configurar_banco()
        self.inicializar_tela_login()

    def inicializar_tela_login(self):
        # Passa o método sucesso_login como o callback de sucesso
        self.tela_login = JanelaLogin(callback_sucesso=self.sucesso_login)
        self.tela_login.mainloop()

    # CORRIGIDO: Adicionado o parâmetro 'usuario_id' para receber o ID do usuário logado
    def sucesso_login(self, usuario_id):
        # Instancia a tela principal injetando o ID do usuário autenticado para isolar os dados
        self.app_principal = JanelaPrincipal(usuario_logado_id=usuario_id)
        self.app_principal.mainloop()

if __name__ == "__main__":
    # Inicializa o controlador do aplicativo
    app = ControladorAplicativo()