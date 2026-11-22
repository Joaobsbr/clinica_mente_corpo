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

