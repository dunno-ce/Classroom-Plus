from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="classrecording",
            name="subject",
            field=models.CharField(db_index=True, default="general", max_length=64),
        ),
        migrations.AddField(
            model_name="teachernote",
            name="subject",
            field=models.CharField(db_index=True, default="general", max_length=64),
        ),
        migrations.CreateModel(
            name="SubjectTest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(db_index=True, default="general", max_length=64)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("uploaded_by", models.CharField(default="Teacher", max_length=120)),
                ("attachment", models.FileField(upload_to="tests/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
