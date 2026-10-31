"""Testes no navegador. Requer a aplicação em APP_URL (padrão localhost:8087).

As respostas do ViaCEP são controladas nestes testes para não depender de um
serviço externo. jQuery é carregado a partir do CDN usado pela aplicação.
"""
import json
import os
import unittest

from playwright.sync_api import sync_playwright, expect


class FormulariosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1000, "height": 900})
        self.base = os.environ.get("APP_URL", "http://localhost:8087")
        self.cep_requests = []
        self.page.route("https://viacep.com.br/ws/**", self.viacep)

    def tearDown(self):
        self.page.close()

    def viacep(self, route):
        self.cep_requests.append(route.request.url)
        data = ({"erro": True} if "99999999" in route.request.url else {
            "logradouro": "Praça da Sé", "bairro": "Sé", "localidade": "São Paulo", "uf": "SP"
        })
        route.fulfill(status=200, content_type="application/json", body=json.dumps(data))

    def abrir(self, path="/cadastro-validado"):
        self.page.goto(self.base + path)
        if path == "/cadastro-validado":
            self.page.wait_for_function("typeof window.jQuery === 'function'")

    def preencher(self):
        for name, value in {"nome": "Ana", "sobrenome": "Exemplo", "email": "ana@example.com",
                            "senha": "Exemplo123!", "confirmacao": "Exemplo123!"}.items():
            self.page.locator("#" + name).fill(value)
        self.page.locator("#cep").fill("01001000")
        self.page.locator("#buscar-cep").click()
        expect(self.page.locator("#cidade")).to_have_value("São Paulo")
        self.page.locator("#numero").fill("100")
        self.page.locator("#complemento").fill("Não se aplica")

    def test_campos_obrigatorios_e_foco_no_primeiro_erro(self):
        self.abrir()
        self.page.locator("button[type=submit]").click()
        expect(self.page.locator('[aria-invalid="true"]')).to_have_count(12)
        expect(self.page.locator("#nome")).to_be_focused()
        expect(self.page.locator("#resultado")).to_contain_text("Revise")

    def test_email_senha_e_confirmacao_rejeitados(self):
        self.abrir()
        self.preencher()
        self.page.locator("#email").fill("email-invalido")
        self.page.locator("#senha").fill("123")
        self.page.locator("#confirmacao").fill("456")
        self.page.locator("button[type=submit]").click()
        expect(self.page.locator("#email-erro")).to_contain_text("e-mail válido")
        expect(self.page.locator("#senha-erro")).to_contain_text("8 caracteres")
        expect(self.page.locator("#confirmacao-erro")).to_contain_text("iguais")
        expect(self.page.locator("#resultado")).not_to_contain_text("sucesso")

    def test_dados_validos_e_limpeza_sem_envio_de_cadastro(self):
        self.abrir()
        self.preencher()
        enviados = []
        self.page.on("request", lambda request: enviados.append(request) if request.method == "POST" else None)
        self.page.locator("button[type=submit]").click()
        expect(self.page.locator("#resultado")).to_contain_text("sucesso")
        expect(self.page.locator('[aria-invalid="true"]')).to_have_count(0)
        self.assertEqual(enviados, [])
        self.page.locator("button[type=reset]").click()
        expect(self.page.locator("#nome")).to_have_value("")
        expect(self.page.locator("#rua")).to_have_value("")
        expect(self.page.locator("#resultado")).to_be_hidden()
        expect(self.page.locator("[aria-invalid]")).to_have_count(0)

    def test_cep_valido_preenche_endereco_e_edicao_limpa_dados_anteriores(self):
        self.abrir("/endereco")
        self.page.locator("#cep").fill("01001000")
        self.page.locator("#buscar-cep").click()
        for field, value in {"rua": "Praça da Sé", "bairro": "Sé", "cidade": "São Paulo", "estado": "SP"}.items():
            expect(self.page.locator("#" + field)).to_have_value(value)
        self.page.locator("#cep").fill("02000000")
        for field in ["rua", "bairro", "cidade", "estado"]:
            expect(self.page.locator("#" + field)).to_have_value("")

    def test_cep_incompleto_nao_consulta_api(self):
        self.abrir("/endereco")
        self.page.locator("#cep").fill("123")
        self.page.locator("#buscar-cep").click()
        expect(self.page.locator("#cep-status")).to_contain_text("8 dígitos")
        self.assertEqual(self.cep_requests, [])

    def test_cep_inexistente_informa_erro(self):
        self.abrir("/endereco")
        self.page.locator("#cep").fill("99999999")
        self.page.locator("#buscar-cep").click()
        expect(self.page.locator("#cep-status")).to_contain_text("não encontrado")
        expect(self.page.locator("#cidade")).to_have_value("")

    def test_falha_de_rede_permite_preenchimento_manual(self):
        self.abrir("/endereco")
        self.page.unroute("https://viacep.com.br/ws/**")
        self.page.route("https://viacep.com.br/ws/**", lambda route: route.abort())
        self.page.locator("#cep").fill("01001000")
        self.page.locator("#buscar-cep").click()
        expect(self.page.locator("#cep-status")).to_contain_text("Não foi possível")
        expect(self.page.locator("#buscar-cep")).to_be_enabled()
        self.page.locator("#rua").fill("Endereço manual")
        expect(self.page.locator("#rua")).to_have_value("Endereço manual")

    def test_tela_estreita_sem_transbordamento_horizontal(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.abrir()
        self.page.wait_for_function("getComputedStyle(document.body).backgroundColor !== 'rgba(0, 0, 0, 0)'")
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))


if __name__ == "__main__":
    unittest.main()
