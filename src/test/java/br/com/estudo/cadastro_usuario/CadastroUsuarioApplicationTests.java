package br.com.estudo.cadastro_usuario;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CadastroUsuarioApplicationTests {

    @Autowired
    private Environment environment;

    private final HttpClient client = HttpClient.newHttpClient();

    private HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        return client.send(HttpRequest.newBuilder(URI.create("http://localhost:" + port + path))
                .GET().build(), HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void inicioOfereceAcessoAsTresAtividades() throws Exception {
        var response = get("/");
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.body()).contains("href=\"/endereco\"", "href=\"/cadastro\"",
                "href=\"/cadastro-validado\"");
    }

    @Test
    void enderecoRenderizaSomenteCamposDeEndereco() throws Exception {
        var response = get("/endereco");
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.body()).contains("Consulta de endereço", "id=\"cep\"",
                "id=\"rua\"", "id=\"bairro\"", "id=\"cidade\"", "id=\"estado\"")
                .doesNotContain("id=\"nome\"", "id=\"senha\"", "src=\"/js/validation.js\"");
    }

    @ParameterizedTest
    @ValueSource(strings = {"/cadastro", "/cadastro-validado"})
    void cadastroRenderizaOsDozeCamposEAsUnidadesFederativas(String path) throws Exception {
        var response = get(path);
        assertThat(response.statusCode()).isEqualTo(200);
        for (String field : new String[]{"nome", "sobrenome", "email", "senha", "confirmacao",
                "cep", "rua", "bairro", "cidade", "estado", "numero", "complemento"}) {
            assertThat(response.body()).contains("id=\"" + field + "\"");
        }
        assertThat(response.body()).contains("value=\"SP\"", "value=\"AC\"", "value=\"TO\"")
                .doesNotContain("th:each", "th:text", "th:if");
    }

    @Test
    void validacaoJqueryEhCarregadaApenasNaAtividadeQuatro() throws Exception {
        assertThat(get("/cadastro").body()).contains("data-validar=\"false\"")
                .doesNotContain("jquery-3.7.1.min.js", "src=\"/js/validation.js\"");
        assertThat(get("/cadastro-validado").body()).contains("data-validar=\"true\"",
                "jquery-3.7.1.min.js", "src=\"/js/validation.js\"");
    }

    @ParameterizedTest
    @ValueSource(strings = {"/js/main.js", "/js/validation.js"})
    void scriptsSaoServidosComoJavascript(String path) throws Exception {
        var response = get(path);
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.headers().firstValue("content-type").orElse("")).contains("javascript");
        assertThat(response.body()).isNotBlank();
    }

    @Test
    void rotaInexistenteRetorna404() throws Exception {
        assertThat(get("/pagina-inexistente").statusCode()).isEqualTo(404);
    }

}
