# Espaço Mente e Corpo — Django v2

Nova base integrada Django para o site público e o sistema interno da clínica.

## O que está incluído

### Site público
- Página institucional separada da aplicação interna.
- Logo fornecida pela clínica incluída em `core/static/core/img/logo.png`.
- Seções Início, Sobre, Especialidades, Profissionais e Contato.
- Botões de WhatsApp usando o número informado: **(81) 99152-3595**.
- Especialidades e profissionais exibidos a partir dos dados cadastrados.

### Sistema interno
- Login individual com Django.
- Recepção como primeira tela após o login.
- Recepção: busca por nome do paciente ou responsável; resultados com nome, idade, sexo, status; links para editar e agendar.
- Cadastro/edição de pacientes: CPF opcional; próprio paciente como responsável ou responsável separado; telefone/e-mail; rua/número e bairro; status. Não há upload nem armazenamento de documentos de pacientes.
- Após cadastrar paciente, retorno automático à Recepção.
- Pacientes: contagem total/ativos/desativados e exportação CSV.
- Agenda geral e individual, com filtro por dia, paciente/responsável, profissional e status.
- Disponibilidade semanal por profissional, com modalidade presencial, online ou domicílio, horários e sala.
- Agendamento com paciente já cadastrado, profissional, especialidade, sala, modalidade e verificação de conflitos de paciente/profissional/sala.
- Cancelamento em tela própria, com motivo obrigatório e confirmação digitando `CANCELAR`; histórico preservado.
- Consultas: histórico de agendadas, realizadas, canceladas e não comparecimento.
- Declaração de comparecimento disponível apenas para consulta marcada como realizada.
- Administração dos modelos de declaração: criar, editar, ativar/desativar e exclusão lógica. Declarações emitidas mantêm cópia do texto e dos dados usados.
- Profissionais: somente administrador pode criar contas, editar perfil, desativar contas e definir nível Básico/Administrador, especialidade, exposição pública e permissão adicional de prontuário.
- Prontuários: módulo protegido por permissão individual `can_access_records`; sem anexos ou documentos.
- Auditoria de ações administrativas e operacionais relevantes.
- Gestão de salas e especialidades.
- Painel `/django-admin/` para manutenção técnica.

## Perfis

### Básico
- Recepção
- Agenda
- Disponibilidade
- Consultas
- Pacientes
- Não vê Profissionais nem Administração.
- Não acessa prontuários por padrão. O administrador pode autorizar esse acesso separadamente.

### Administrador
- Acesso a todas as áreas.
- Gerencia profissionais, permissões, modelos de declaração, salas, especialidades e auditoria.

## Instalação no Windows (PowerShell)

Na pasta onde está `manage.py`:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_clinic
python manage.py runserver
```

Se a política do PowerShell não permitir ativação, é possível usar diretamente:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_clinic
.\.venv\Scripts\python.exe manage.py runserver
```

Acesse:
- Site público: http://127.0.0.1:8000/
- Sistema: clique em “Área profissional” e entre com seu usuário.
- Administração Django: http://127.0.0.1:8000/django-admin/

## Configuração inicial depois de entrar

1. Use `/django-admin/` ou a tela de Administração para conferir os cadastros.
2. No menu Profissionais, crie as contas individuais da equipe. Defina nível Básico ou Administrador, especialidade e permissão de prontuário.
3. Cadastre salas em Administração (a base permite criar salas pelo painel Django; pode-se adicionar interface de gestão numa próxima iteração).
4. Execute `python manage.py seed_clinic` para cadastrar as especialidades iniciais e o modelo padrão de declaração.
5. Cadastre os horários semanais em Agenda > Disponibilidade.
6. Cadastre pacientes em Recepção, e depois agende pela própria Recepção ou pela Agenda.

## Referência das especialidades

O seed inclui os serviços observados na referência enviada: Fisioterapia, Estética, Psicologia, Clínico, Nutrição, Fonoaudiologia, Psicopedagogia, Neuropsicopedagogia, Pneumologista e Saúde do Adolescente. A clínica deve confirmar a lista final.

## O que ainda requer validação da clínica
- Se cada especialidade usa a mesma grade da planilha ou possui regras próprias.
- Se salas são compartilhadas por todos os serviços.
- Duração padrão de cada atendimento e intervalos.
- Se a modalidade online/domicílio precisa de detalhes adicionais.
- Texto oficial e campos exigidos para declaração.
- Endereço completo e apresentação institucional antes de publicar.

## Segurança e uso com dados reais
Esta é uma base inicial para desenvolvimento e homologação, não um sistema certificado ou pronto para produção. Antes de inserir dados reais:
- Configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`.
- Use HTTPS e banco de produção (por exemplo PostgreSQL).
- Configure backups testados, política de retenção e resposta a incidentes.
- Faça revisão técnica das permissões e isolamento de dados clínicos.
- Avalie LGPD, bases legais, avisos de privacidade, controles de acesso e registros de auditoria com a clínica.
- Revise textos e funcionamento de declarações com a administração da clínica.
- Não use a conta superusuário na rotina diária.

A base não contém pacientes de demonstração e não armazena arquivos/documentos de pacientes. A declaração de comparecimento é gerada pela clínica e tem texto e informações do atendimento preservados para reimpressão.
