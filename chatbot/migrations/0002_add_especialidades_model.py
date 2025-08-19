# Generated manually for especialidades system

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        # Criar o modelo Especialidade
        migrations.CreateModel(
            name='Especialidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('descricao', models.TextField(blank=True, help_text='Descrição da especialidade', null=True)),
                ('ativa', models.BooleanField(default=True, help_text='Se a especialidade está ativa para seleção')),
            ],
            options={
                'verbose_name': 'Especialidade',
                'verbose_name_plural': 'Especialidades',
                'ordering': ['nome'],
            },
        ),
        
        # Criar especialidades padrão
        migrations.RunSQL(
            """
            INSERT INTO chatbot_especialidade (nome, descricao, ativa) VALUES 
            ('Pneumologia', 'Especialidade dedicada à investigação, diagnóstico e tratamento das doenças do sistema respiratório', true),
            ('Endocrinologia', 'A Endocrinologia cuida do funcionamento das glândulas e hormônios', true),
            ('Metabologia', 'A Metabologia foca no funcionamento do metabolismo do corpo', true),
            ('Medicina do Sono', 'Esta área apresenta intersecção com as demais especialidades. A principal doença é a apneia obstrutiva do sono', true);
            """,
            reverse_sql="DELETE FROM chatbot_especialidade WHERE nome IN ('Pneumologia', 'Endocrinologia', 'Metabologia', 'Medicina do Sono');"
        ),
        
        # Adicionar o campo ManyToMany ao modelo Medico
        migrations.AddField(
            model_name='medico',
            name='especialidades_new',
            field=models.ManyToManyField(help_text='Selecione uma ou mais especialidades do médico', related_name='medicos', to='chatbot.especialidade'),
        ),
        
        # Nota: A migração de dados existentes deve ser feita manualmente no admin
        # após aplicar esta migração, associando cada médico às suas especialidades correspondentes
        
        # Remover o campo antigo de especialidades
        migrations.RemoveField(
            model_name='medico',
            name='especialidades',
        ),
        
        # Renomear o novo campo
        migrations.RenameField(
            model_name='medico',
            old_name='especialidades_new',
            new_name='especialidades',
        ),
    ]
