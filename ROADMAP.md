# Bússola Financeira

**Roteiro de projeto · construção guiada**

Seu primeiro projeto de verdade: um site pessoal que reúne entradas, gastos fixos, lista de desejos com metas de economia e controle de faturas por banco e por mês. Este roteiro te leva do zero ao primeiro deploy, uma fase de cada vez.

- **Nível:** iniciante com base
- **Stack:** Python · Flask · SQLite
- **Ritmo:** livre, por fases

---

## 01. Preparar o ambiente

### Colocar o Claude Code pra funcionar no VS Code

Você já instalou a extensão — falta só abrir e entrar com sua conta.

1. Abra a pasta do projeto no VS Code: **File → Open Folder**. Pode ser uma pasta vazia por enquanto.
2. Abra o painel: clique no ícone de faísca (✱) no canto superior direito do editor (aparece quando você tem um arquivo aberto), ou aperte `Ctrl+Shift+P` (Windows/Linux) e digite `Claude Code`. Também dá pra clicar em **✱ Claude Code** na barra inferior — esse funciona mesmo sem arquivo aberto.
3. Na primeira vez vai aparecer uma tela de login: clique em **Sign in** e autorize no navegador, usando a mesma conta que você já usa aqui.
4. Depois do login aparece um checklist "Learn Claude Code" — vale seguir os passos com **Show me**, ou fechar com o X e voltar depois.
5. Repare no indicador de modo, embaixo da caixa de texto. Comece no modo **Manual**: toda alteração de arquivo aparece como um diff (lado a lado) antes de ser aplicada, e você aceita, rejeita ou pede pra mudar. É o melhor jeito de aprender, porque você vê exatamente o que foi alterado e por quê.
6. Pra pedir ajuda, escreva no campo de prompt, por exemplo: *"cria a estrutura inicial de um projeto Flask com um model de Transação"* — e revise antes de aceitar.
7. Pra rodar os comandos de terminal da próxima seção, abra o terminal integrado com `` Ctrl+` `` — o Claude Code se integra automaticamente com ele.

> **Dica:** fique no modo Manual pelo menos até terminar a Fase 1. Ler cada diff é onde a aprendizagem realmente acontece — depois que os padrões ficarem familiares, migrar pro modo automático economiza tempo.

### Git e GitHub: o mínimo pra este projeto

Git guarda o histórico de tudo que você muda no código. GitHub é onde esse histórico fica hospedado na nuvem — serve de backup e, mais pra frente, de portfólio.

**Verificar se o git está instalado**
```
git --version
```

**Configurar sua identidade (uma vez só, no computador)**
```
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

**Criar o repositório, dentro da pasta do projeto**
```
git init
```

**Criar um arquivo .gitignore na raiz do projeto, com este conteúdo**
```
venv/
__pycache__/
*.pyc
instance/
*.db
.env
.vscode/
```

**O ciclo do dia a dia**
```
git status                    # o que mudou desde o último commit
git add nome-do-arquivo.py    # prepara um arquivo específico
git add .                     # ou prepara tudo que mudou
git commit -m "mensagem descrevendo a mudança"
git log --oneline             # ver o histórico
```

**Conectar ao GitHub (crie um repositório vazio em github.com primeiro, sem README)**
```
git remote add origin https://github.com/seu-usuario/bussola-financeira.git
git branch -M main
git push -u origin main
```

**Depois da primeira vez, é só**
```
git add .
git commit -m "mensagem"
git push
```

> **Dica:** faça um commit por funcionalidade pequena e funcionando — nunca um commit gigante no fim do dia. Mensagens como `"adiciona cadastro de despesas"` valem muito mais do que `"mudanças"`. Se quiser, peça para o próprio Claude Code escrever a mensagem de commit pra você: ele lê o diff e resume.

---

## 02. Roteiro por fases

Cada fase termina com algo funcionando de verdade — não pule pra próxima sem ver a anterior rodando.

### Fase 1 — Fundamentos: CRUD de entradas e saídas

- **Objetivo:** Montar a espinha dorsal do site: cadastrar, listar, editar e excluir receitas e despesas.
- **Você aprende:** Rotas no Flask, templates com Jinja2, formulários HTML, modelagem com SQLAlchemy.
- **Entregável:** Uma página onde você lança um valor e vê a lista atualizada, com o saldo total calculado.
- **Dica:** ignore a aparência por enquanto — CSS bonito é fase 5. O foco aqui é 100% fazer os dados persistirem corretamente no banco.

### Fase 2 — Gastos fixos recorrentes

- **Objetivo:** Separar despesas que se repetem todo mês (aluguel, assinaturas, internet) dos gastos pontuais.
- **Você aprende:** Categorias, campos de recorrência e a lógica de marcar um gasto fixo como "pago" a cada mês.
- **Entregável:** Uma tela "Gastos fixos" com a lista deles e quanto já foi pago no mês atual.
- **Dica:** modele o gasto fixo como uma "assinatura" (nome, valor, dia de vencimento), separada da tabela de lançamentos avulsos.

### Fase 3 — Lista de desejos e metas de economia

- **Objetivo:** Cadastrar itens que você quer comprar e calcular quanto precisa guardar por mês para chegar lá.
- **Você aprende:** Regra de negócio no back-end — (preço − já guardado) ÷ meses restantes — e barras de progresso.
- **Entregável:** Cada item mostra algo como "faltam R$ 340 — guarde R$ 85/mês pra comprar até dezembro".
- **Dica:** essa é a funcionalidade mais "sua" do projeto — vale caprichar na regra de cálculo, é o que vai te dar mais satisfação de usar de verdade.

### Fase 4 — Faturas por banco e por mês

- **Objetivo:** Modelar várias faturas de cartão, cada uma ligada a um banco e a um mês/ano específico, com seus gastos.
- **Você aprende:** Relacionamentos mais complexos (um banco tem várias faturas, uma fatura tem vários gastos) e filtros por mês.
- **Entregável:** Uma tela onde você escolhe o banco e o mês, e vê a fatura daquele período com o total.
- **Dica:** é a fase mais difícil de modelar. Antes de codar, desenhe as tabelas no papel: Banco, Fatura, Gasto — e como elas se conectam.

### Fase 5 — Dashboard com gráficos

- **Objetivo:** Uma tela inicial que resume tudo: entradas x saídas do mês, progresso das metas, total das faturas em aberto.
- **Você aprende:** Agregações (somas e totais por categoria) e Chart.js para gráficos simples de pizza e barra.
- **Entregável:** O dashboard visual — a "cara" do site, o que você mostra quando alguém pergunta o que você andou fazendo.
- **Dica:** essa também é a fase de deixar o CSS bonito de verdade. Fases 1 a 4 são sobre funcionar; esta é sobre apresentar.

### Fase 6 — Login e deploy *(opcional)*

- **Objetivo:** Proteger o site com login (mesmo sendo só pra você) e colocá-lo no ar.
- **Você aprende:** Autenticação com Flask-Login, variáveis de ambiente e deploy num serviço gratuito (Render, Railway ou PythonAnywhere).
- **Entregável:** Um link do site funcionando na internet, acessível também pelo celular.
- **Dica:** só vale a pena se você quiser acessar de fora de casa. Para uso 100% local, essa fase é dispensável — pode ficar só rodando na sua máquina.

---

## 03. Recursos de estudo

| Área | Recurso | Descrição |
|---|---|---|
| Flask | Flask Mega-Tutorial (Miguel Grinberg) | O tutorial mais completo e didático para aprender Flask do zero construindo um app real, passo a passo. |
| Flask | Documentação oficial do Flask | flask.palletsprojects.com — quickstart curto, ótimo pra consultar enquanto codifica. |
| SQL | SQLBolt | Lições interativas e curtas de SQL, direto no navegador — úteis antes da Fase 1, pra entender o que o SQLAlchemy faz por baixo dos panos. |
| Git | Learn Git Branching | Simulador visual e interativo de git — ótimo depois que os comandos básicos acima já estiverem confortáveis. |
| Gráficos | Documentação do Chart.js | Exemplos prontos de gráfico de pizza e barra — o suficiente para a Fase 5. |

---

Projeto pessoal, primeiro de muitos. Não existe prazo certo aqui — o objetivo é sair da Fase 1 sabendo mais do que entrou. Volte a este roteiro sempre que precisar lembrar o próximo passo.
