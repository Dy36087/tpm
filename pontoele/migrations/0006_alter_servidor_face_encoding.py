from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pontoele", "0005_alter_servidor_bairro_alter_servidor_cep_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servidor",
            name="face_encoding",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
